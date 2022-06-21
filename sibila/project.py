import requests
from os import environ
from os.path import isfile
from http import HTTPStatus
from datetime import datetime
from urllib.parse import urlparse

from melitk import logging

from sibila.utils import AWSHandler, wait_for_resource, ds_types_short, logger
from sibila.dataset import Dataset
from sibila.predictor import Predictor
from sibila.errors import (
    UnableToLoginError,
    DatasetError,
    PredictorError,
    ResourceError,
)


class Project:
    def __init__(
        self,
        name: str,
        team: str,
        username: str,
        password: str,
        aws_access_key_id: str = environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key: str = environ.get("AWS_SECRET_ACCESS_KEY"),
        aws_session_token: str = environ.get("AWS_SESSION_TOKEN"),
        region_name: str = "us-east-1",
    ):
        if not aws_access_key_id and not aws_secret_access_key and not aws_session_token:
            # provifing defaults. Remove soon.
            aws_access_key_id = "AKIAZE4F2HCI7ZIB3SBP"
            aws_secret_access_key = "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"

        """Instantiates a DatasetGroup in AWS.
        Naming convention:
            DatasetGroupName: TEAM__project_name
        """

        # Authenticate the LDAP user against the data-team-ml-ldap app.
        if environ.get("DATA_APP_STEP"):
            base_auth_url = "https://internal.mercadolibre.com"
        else:
            base_auth_url = "https://internal-api.mercadolibre.com"
        response = requests.post(
            f"{base_auth_url}/data-team/auth/login",
            json={"username": username, "password": password},
        )

        if response.status_code != HTTPStatus.NO_CONTENT:
            raise UnableToLoginError(
                f"Unable to authenticate username {username} - status_code: {response.status_code}"
            )

        # Only underscores are allowed by AWS.
        team = team.replace("-", "_").upper()
        self.name = name.replace("-", "_")
        # Since i'll be using __ as a separator, I don't want any instances of it in the name or team.
        while "__" in team:
            team = team.replace("__", "_")
        while "__" in self.name:
            self.name = self.name.replace("__", "_")

        # Name to instantiate in the service
        self._dsg_name = f"{team}__{self.name}"

        self.aws_handler = AWSHandler(
            team=team,
            s3_uri=f"s3://bi-ml-forecasting-data/{team}/{self.name}",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name,
        )

        dataset_groups = self._dataset_groups()
        if self._dsg_name in dataset_groups.keys():
            logger.debug(f"Pointing to existing dataset group {self._dsg_name}")
            self.arn = dataset_groups[self._dsg_name]
        else:
            logger.debug(f"Creating new dataset group {self._dsg_name}")
            self.arn = self._create_group()

        self._datasets, self.imports, self._predictors = self._get_entities()
        # This is a hotfix so that I can access the _datasets within the Predictor class.
        self.aws_handler._datasets = self._datasets

    def _create_group(self):
        return self.aws_handler.forecast.create_dataset_group(
            DatasetGroupName=self._dsg_name,
            Domain=self.aws_handler.DOMAIN,
            Tags=[{"Key": "Name", "Value": self.aws_handler.team}],
        )["DatasetGroupArn"]

    def upload_dataset(
        self,
        local_path: str,
        ds_type: str,
        schema: dict,
        frequency: str = None,
        timestamp_format: str = None,
    ):
        """Returns a dataset object by creating an import and a dataset to hold it in aws.
        Naming convention:
            CSV Path: s3://bi-ml-forecasting-data/TEAM/project_name/datasets/TARGET_TIME_SERIES.csv"
            DatasetName: TEAM__project_name__TTS
            ImportName: TTS__timestamp
        """

        # Validations
        if not local_path.endswith(".csv"):
            raise DatasetError("The file provided must be a .csv file")

        if not isfile(local_path):
            raise DatasetError("Could not find a file in the specified local_path")

        if ds_type not in Dataset.VALID_DATASET_TYPES:
            raise DatasetError(f"Valid dataset types are {Dataset.VALID_DATASET_TYPES}")

        if (ds_type != Dataset.ITEM_METADATA) and not (frequency and timestamp_format):
            raise DatasetError(
                "You must specify a frequency and a timestamp_format for this type of dataset."
            )

        # Service names according to convention. ds_types_short is used because aws has a cap in length
        ds_name = f"{self.aws_handler.team}__{self.name}__{ds_types_short[ds_type]}"
        import_name = (
            ds_types_short[ds_type]
            + "__"
            + str(datetime.now().timestamp()).replace(".", "_")
        )

        # Determine the dataset s3_uri.
        s3_uri = self.aws_handler.s3_uri + f"/datasets/{ds_type}.csv"

        # If the dataset doesn't exist, create it.
        if ds_name not in self._datasets.keys():
            # Create a dataset object.
            dataset = Dataset(
                dsg_arn=self.arn,
                ds_type=ds_type,
                schema=schema,
                frequency=frequency,
                timestamp_format=timestamp_format,
                s3_uri=s3_uri,
                aws_handler=self.aws_handler,
            )

            # Set service names
            dataset._ds_name = ds_name
            dataset._import_name = import_name
            logger.debug(f"Creating new dataset {ds_name}")
            dataset.arn = dataset._create()

            # Save the dataset to the Project's _datasets.
            self._datasets[dataset._ds_name] = dataset.arn
            # Update the AWSHandler's datasets. This is a hotfix so that I can access the _datasets within the Predictor class.
            self.aws_handler._datasets = self._datasets

            # Update the dataset group dataset's to include the new one
            # as well as the existing ones.
            datasets_to_update = [ds_arn for ds_arn in self._datasets.values()]
            logger.debug(f"Updating dataset group with datasets {datasets_to_update}")
            response_dsg = self.aws_handler.forecast.update_dataset_group(
                DatasetGroupArn=self.arn, DatasetArns=datasets_to_update
            )

            logger.debug(f"Dataset group update response: {response_dsg}")

        # If the dataset exists, point to it
        else:  # pragma: no cover
            dataset_arn = self._datasets[ds_name]
            dataset_info = self.aws_handler.forecast.describe_dataset(
                DatasetArn=dataset_arn
            )

            # TODO: when AWS starts supporting recursive deletion of dataset, delete
            # old dataset and create a new one if user requests new DataFrequency.
            retrieved_frequency = dataset_info.get("DataFrequency")
            if retrieved_frequency and retrieved_frequency != frequency:
                raise DatasetError(
                    f"You are attempting to upload a {ds_type} with a frequency of {frequency} when you have used a frequency of {retrieved_frequency} in the past for this type of dataset. If you really want to do this, you should create a new project. Swapping frequencies for the same project is a feature that will be coming in the future."
                )
            dataset = Dataset(
                dsg_arn=self.arn,
                ds_type=dataset_info["DatasetType"],
                schema=dataset_info["Schema"],
                frequency=retrieved_frequency,
                timestamp_format=timestamp_format,
                s3_uri=s3_uri,
                aws_handler=self.aws_handler,
            )

            dataset._ds_name = ds_name
            logger.debug(f"Pointing to existing dataset {ds_name}")
            dataset._import_name = import_name
            dataset.arn = dataset_arn

        # Upload the csv to s3.
        parsed_s3_uri = urlparse(dataset.s3_uri)
        bucket, key = parsed_s3_uri.netloc, parsed_s3_uri.path.lstrip("/")
        logger.info(f"Uploading dataset to s3")
        logger.debug(f"Uploading {local_path} to key {key} in bucket {bucket}")
        self.aws_handler.s3.upload_file(Filename=local_path, Bucket=bucket, Key=key)

        # Create an import.
        logger.debug(f"Creating new import")
        try:
            dataset._create_import()
        except ResourceError as e:  # pragma: no cover
            logger.error(
                f"The dataset could not be created because an error {e} was found when creating the import"
            )
            return

        # Save the import to the Project's imports.
        self.imports[dataset._import_name] = dataset.import_arn

        return dataset

    def get_dataset(self, ds_type: str):
        """Returns a dataset object by retrieving a dataset import from aws."""

        ds_name = f"{self.aws_handler.team}__{self.name}__{ds_types_short[ds_type]}"

        # sorting by import job by timestamp and ds_type
        ds_imports = filter(
            lambda x: x.startswith(ds_types_short[ds_type]), self.imports.keys()
        )
        ds_imports = sorted(
            ds_imports, key=lambda x: float(x.split("__")[1].replace("_", "."))
        )

        import_name = ds_imports[-1] if len(ds_imports) > 0 else None
        if not (ds_name in self._datasets.keys() and import_name):
            raise DatasetError(
                f"No {ds_type} dataset was found in project {self.name}.\nTo create a new dataset, use the `upload_dataset` method"
            )

        # Get dataset and import info.
        import_arn = self.imports[import_name]
        import_info = self.aws_handler.forecast.describe_dataset_import_job(
            DatasetImportJobArn=import_arn
        )
        dataset_arn = self._datasets[ds_name]
        dataset_info = self.aws_handler.forecast.describe_dataset(
            DatasetArn=dataset_arn
        )

        dataset = Dataset(
            dsg_arn=self.arn,
            ds_type=dataset_info["DatasetType"],
            schema=dataset_info["Schema"],
            frequency=dataset_info["DataFrequency"],
            timestamp_format=import_info.get("TimestampFormat"),
            s3_uri=import_info["DataSource"]["S3Config"]["Path"],
            aws_handler=self.aws_handler,
        )

        dataset._ds_name = ds_name
        dataset._import_name = import_name
        dataset.arn = dataset_arn
        dataset.import_arn = import_arn

        # https://docs.aws.amazon.com/cli/latest/reference/personalize/describe-dataset-import-job.html
        dataset.status = import_info["Status"]
        dataset.failure_reason = import_info.get("FailureReason")
        return dataset

    def train_new_predictor(
        self,
        name: str,
        algorithm: str,
        horizon: int,
        frequency: str,
        forecast_dimensions: list = None,
        featurizations: list = None,
        supplementary_features: list = None,
        backtest_windows: int = 1,
        window_offset: int = None,
        hpo: int = False,
        hpo_config: dict = None,
        training_parameters: dict = None,
    ):
        """Returns a predictor object by creating a predictor in aws.
        Naming convention:
            PredictorName: TEAM__name
        """

        name = name.replace("-", "_")
        while "__" in name:
            name = name.replace("__", "_")

        predictor_name = f"{self.aws_handler.team}__{name}"

        if predictor_name in self._predictors.keys():
            raise PredictorError(
                f"A predictor with the name {name} already exists for this project.\nYou can retrieve it by using the `get_predictor` method"
            )

        predictor = Predictor(
            aws_handler=self.aws_handler,
            dsg_arn=self.arn,
            name=name,
            algorithm=algorithm,
            horizon=horizon,
            frequency=frequency,
            forecast_dimensions=forecast_dimensions,
            featurizations=featurizations,
            supplementary_features=supplementary_features,
            backtest_windows=backtest_windows,
            window_offset=window_offset,
            hpo=hpo,
            hpo_config=hpo_config,
            training_parameters=training_parameters,
        )

        predictor._predictor_name = predictor_name

        logger.info("Waiting for all datasets to be ready.")
        # Wait for all datasets to be ready before training the predictor.
        for dataset_arn in self._datasets.values():
            try:
                wait_for_resource("dataset", dataset_arn, self.aws_handler)
            except ResourceError as e:  # pragma: no cover
                logger.error(f"Error in dataset {dataset_arn}: {e}")
                logger.error(
                    """The predictor could not be created because some of the datasets in the project contain errors.
                    You should re-upload the ones that failed."""
                )
                return

        # Wait for all dataset imports to be ready before training the predictor.
        for import_name, import_arn in self.imports.items():
            try:
                wait_for_resource("dataset_import_job", import_arn, self.aws_handler)
            except ResourceError as e:  # pragma: no cover
                logger.error(f"Error in dataset {import_arn}: {e}")
                # Delete the import
                self.aws_handler.forecast.delete_dataset_import_job(
                    DatasetImportJobArn=import_arn
                )

                # Delete the import from the project's imports
                del self.imports[import_name]

                logger.error(
                    """The predictor could not be created because some of the datasets in the project contain errors.
                    You should re-upload the ones that failed."""
                )
                return

        logger.info(f"Creating predictor {predictor._predictor_name}")
        predictor.arn = predictor._create()

        # Add predictor to the project's _predictors
        self._predictors[predictor_name] = predictor.arn

        return predictor

    def get_predictor(self, name: str):
        """Returns a predictor object by retrieving information from an existing predictor in aws."""

        name = name.replace("-", "_")
        while "__" in name:
            name = name.replace("__", "_")

        predictor_name = f"{self.aws_handler.team}__{name}"

        logger.debug(f"Attempting to retrieve predictor {predictor_name}")
        if predictor_name not in self._predictors.keys():
            raise PredictorError(
                f"No predictor with the name {name} was found in project {self.name}.\nTo create a new predictor, use the `train_new_predictor` method"
            )

        predictor_arn = self._predictors[predictor_name]

        # Wait for the predictor to be active so that predictor_info is accurate.
        wait_for_resource("predictor", predictor_arn, self.aws_handler)

        predictor_info = self.aws_handler.forecast.describe_predictor(
            PredictorArn=predictor_arn
        )
        # TODO: this doesn't work when autoML was used with the predictor. AlgorithmArn is not a valid key.
        # This is mocked until AWS fixes this issue.
        try:
            algorithm = predictor_info["AlgorithmArn"].split("/")[-1]
        except KeyError:
            algorithm = predictor_info["AutoMLAlgorithmArns"][0].split("/")[-1]

        predictor = Predictor(
            aws_handler=self.aws_handler,
            dsg_arn=self.arn,
            name=name,
            algorithm=algorithm,
            horizon=predictor_info["ForecastHorizon"],
            frequency=predictor_info["FeaturizationConfig"]["ForecastFrequency"],
            forecast_dimensions=predictor_info["FeaturizationConfig"].get(
                "ForecastDimensions"
            ),
            featurizations=predictor_info["FeaturizationConfig"].get("Featurizations"),
            supplementary_features=predictor_info["InputDataConfig"].get(
                "SupplementaryFeatures"
            ),
            backtest_windows=predictor_info["EvaluationParameters"][
                "NumberOfBacktestWindows"
            ],
            window_offset=predictor_info["EvaluationParameters"][
                "BackTestWindowOffset"
            ],
            hpo=predictor_info.get("PerformHPO"),
            hpo_config=predictor_info.get("HPOConfig"),
            training_parameters=predictor_info.get("TrainingParameters"),
        )

        predictor._predictor_name = predictor_name
        predictor.arn = predictor_arn

        return predictor

    def _dataset_groups(self):
        return {
            dataset_group["DatasetGroupName"]: dataset_group["DatasetGroupArn"]
            for dataset_group in self.aws_handler.forecast.list_dataset_groups()[
                "DatasetGroups"
            ]
        }

    def _get_entities(self):
        datasets = {
            dataset_arn.split("/")[-1]: dataset_arn
            for dataset_arn in self.aws_handler.forecast.describe_dataset_group(
                DatasetGroupArn=self.arn
            )["DatasetArns"]
        }

        imports = {
            import_job["DatasetImportJobName"]: import_job["DatasetImportJobArn"]
            for import_job in self.aws_handler.forecast.list_dataset_import_jobs()[
                "DatasetImportJobs"
            ]
            if import_job["DatasetImportJobArn"].split("/")[-2] in datasets.keys()
        }

        predictors = {
            predictor["PredictorName"]: predictor["PredictorArn"]
            for predictor in self.aws_handler.forecast.list_predictors()["Predictors"]
            if predictor["DatasetGroupArn"] == self.arn
        }

        return datasets, imports, predictors

    def predictors(self):
        predictors = []
        for name in self._predictors.keys():
            predictors.append(name.split("__")[1])
        return predictors

    def datasets(self):
        datasets = []
        ds_types_long = {v: k for k, v in ds_types_short.items()}
        for name in self._datasets.keys():
            datasets.append(ds_types_long[name.split("__")[-1]])
        return datasets
