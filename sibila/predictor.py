import os
from datetime import datetime

from melitk import logging

from sibila.errors import PredictorError, ResourceError
from sibila.utils import wait_for_resource, download_and_merge, logger


class Predictor:

    AUTO = "AUTO"
    ARIMA = "ARIMA"
    DEEP_AR_PLUS = "Deep_AR_Plus"
    ETS = "ETS"
    NPTS = "NPTS"
    PROPHET = "Prophet"
    CNN_QR = "CNN-QR"

    VALID_ALGORITHMS = (AUTO, ARIMA, DEEP_AR_PLUS, ETS, NPTS, PROPHET, CNN_QR)

    def __init__(
        self,
        aws_handler: "AWSHandler",
        dsg_arn: str,
        name: str,
        algorithm: str,
        horizon: int,
        frequency: str,
        forecast_dimensions: list = None,
        featurizations: list = None,
        supplementary_features: list = None,
        backtest_windows: int = 1,
        window_offset: int = 0,
        hpo: int = False,
        hpo_config: dict = None,
        training_parameters: dict = None,
    ):
        if algorithm not in Predictor.VALID_ALGORITHMS:
            raise PredictorError(f"Valid algorithms are {Predictor.VALID_ALGORITHMS}")

        self.aws_handler = aws_handler
        self.dsg_arn = dsg_arn
        self.name = name
        self.algorithm = algorithm
        self.horizon = horizon
        self.backtest_windows = backtest_windows
        self.frequency = frequency
        self.forecast_dimensions = forecast_dimensions
        self.featurizations = featurizations
        self.supplementary_features = supplementary_features
        self.window_offset = window_offset or horizon
        self.hpo = hpo
        self.hpo_config = hpo_config
        self.training_parameters = training_parameters
        self.perform_automl = algorithm == Predictor.AUTO
        # If HPOConfig is given, HPO must be set to True
        if self.hpo_config:
            self.hpo = True

        # These are set manually either when the predictor is instantiated or upon retrieval.
        self._predictor_name = None
        self.arn = None

    def _create(self):
        """Instantiates the predictor on the AWS forecast service"""

        self._request = {
            "PredictorName": self._predictor_name,
            "ForecastHorizon": self.horizon,
            "PerformAutoML": self.perform_automl,
            "PerformHPO": self.hpo,
            "EvaluationParameters": {
                "NumberOfBacktestWindows": self.backtest_windows,
                "BackTestWindowOffset": self.window_offset,
            },
            "InputDataConfig": {"DatasetGroupArn": self.dsg_arn},
            "FeaturizationConfig": {
                "ForecastFrequency": self.frequency,
            },
            "Tags": [{"Key": "Name", "Value": self.aws_handler.team}],
        }

        if not self.perform_automl:
            self._request["AlgorithmArn"] = (
                "arn:aws:forecast:::algorithm/" + self.algorithm
            )

        if self.featurizations != None:
            self._request["FeaturizationConfig"][
                "Featurizations"
            ] = self.featurizations or [
                {
                    "AttributeName": "target_value",
                    "FeaturizationPipeline": [
                        {
                            "FeaturizationMethodName": "filling",
                            "FeaturizationMethodParameters": {
                                "frontfill": "none",
                                "middlefill": "zero",
                                "backfill": "zero",
                            },
                        }
                    ],
                }
            ]

        if self.supplementary_features != None:
            self._request["InputDataConfig"][
                "SupplementaryFeatures"
            ] = self.supplementary_features

        if self.forecast_dimensions != None:
            self._request["FeaturizationConfig"][
                "ForecastDimensions"
            ] = self.forecast_dimensions

        if self.hpo_config != None:
            self._request["HPOConfig"] = self.hpo_config

        if self.training_parameters != None:
            self._request["TrainingParameters"] = self.training_parameters

        logger.debug(f"Predictor creation request: {self._request}")
        return self.aws_handler.forecast.create_predictor(**self._request)[
            "PredictorArn"
        ]

    def _update(self):
        predictor_info = self.aws_handler.forecast.describe_predictor(
            PredictorArn=self.arn
        )
        try:
            algorithm = predictor_info["AlgorithmArn"].split("/")[-1]
        except KeyError:
            algorithm = predictor_info["AutoMLAlgorithmArns"][0].split("/")[-1]

        self.algorithm = algorithm
        self.horizon = predictor_info["ForecastHorizon"]
        self.frequency = predictor_info["FeaturizationConfig"]["ForecastFrequency"]
        self.forecast_dimensions = predictor_info["FeaturizationConfig"].get(
            "ForecastDimensions"
        )
        self.featurizations = predictor_info["FeaturizationConfig"].get(
            "Featurizations"
        )
        self.supplementary_features = predictor_info["InputDataConfig"].get(
            "SupplementaryFeatures"
        )
        self.backtest_windows = predictor_info["EvaluationParameters"][
            "NumberOfBacktestWindows"
        ]
        self.window_offset = predictor_info["EvaluationParameters"][
            "BackTestWindowOffset"
        ]
        self.hpo = predictor_info.get("PerformHPO")
        self.hpo_config = predictor_info.get("HPOConfig")
        self.training_parameters = predictor_info.get("TrainingParameters")

    @property
    def info(self):
        self._update()
        return {
            "name": self.name,
            "algorithm": self.algorithm,
            "horizon": self.horizon,
            "frequency": self.frequency,
            "backtest_windows": self.backtest_windows,
            "window_offset": self.window_offset,
            "forecast_dimensions": self.forecast_dimensions,
            "featurizations": self.featurizations,
            "supplementary_features": self.supplementary_features,
            "hpo": self.hpo,
            "hpo_config": self.hpo_config,
            "training_parameters": self.training_parameters,
        }

    def wait_for_training(self):
        try:
            wait_for_resource("predictor", self.arn, self.aws_handler)
        except ResourceError as e:  # pragma: no cover
            logger.error(f"There was an error {e} when creating the predictor")
            return

    def metrics(self, destination_dir):

        if not os.path.isdir(destination_dir):  # pragma: no cover
            logger.info(f"Creating directory: {destination_dir}")
            os.mkdir(destination_dir)

        name = "backtest_" + str(datetime.now().timestamp()).replace(".", "_")
        s3_uri = f"{self.aws_handler.s3_uri}/backtests/{name}"

        # Wait for the predictor to be active before trying to retrieve the metrics.
        logger.info("Waiting for the predictor to be ready...")
        try:
            wait_for_resource("predictor", self.arn, self.aws_handler)
        except ResourceError as e:  # pragma: no cover
            logger.error(
                f"The metrics could not be retrieved because there was an error {e} when creating the predictor"
            )
            return

        # Create the backtest export job.
        logger.debug(f"Creating backtest export {name} to {s3_uri}")
        backtest_arn = self.aws_handler.forecast.create_predictor_backtest_export_job(
            PredictorBacktestExportJobName=name,
            PredictorArn=self.arn,
            Destination={
                "S3Config": {
                    "Path": s3_uri,
                    "RoleArn": self.aws_handler.ROLE_ARN,
                }
            },
            Tags=[
                {
                    "Key": "Name",
                    "Value": self.aws_handler.team,
                },
            ],
        )["PredictorBacktestExportJobArn"]

        logger.info("Waiting for predictor metrics to be ready...")
        try:
            wait_for_resource(
                "predictor_backtest_export_job", backtest_arn, self.aws_handler
            )
        except ResourceError as e:  # pragma: no cover
            logger.error(
                f"The metrics could not be exported because an error {e} ocurred"
            )
            return

        # Download the exported csv files and merge them into the destination path.
        logger.debug("Downloading and merging files")
        download_and_merge(
            s3_uri + "/accuracy-metrics-values/",
            os.path.join(destination_dir, "backtest_metrics.csv"),
            self.aws_handler,
        )
        download_and_merge(
            s3_uri + "/forecasted-values/",
            os.path.join(destination_dir, "backtest_forecasts.csv"),
            self.aws_handler,
        )

        return destination_dir

    def forecast(
        self,
        destination_path: str,
        quantiles: list = None,
    ):

        quantiles = quantiles or ["0.1", "0.5", "0.9"]

        name = "forecast_" + str(datetime.now().timestamp()).replace(".", "_")
        s3_uri = f"{self.aws_handler.s3_uri}/forecasts/{name}"

        # Wait for all datasets to be ready before forecasting.
        logger.info("Waiting for all datasets to be ready")
        for dataset_arn in self.aws_handler._datasets.values():
            try:
                wait_for_resource("dataset", dataset_arn, self.aws_handler)
            except ResourceError as e:  # pragma: no cover
                logger.error(f"Error in dataset {dataset_arn}: {e}")
                logger.error(
                    """The forecast could not be created because some of the datasets in the project contain errors.
                    You should re-upload the ones that failed."""
                )
                return

        # Wait for the predictor to be active before trying to create a forecast.
        logger.info("Waiting for the predictor to be ready")
        try:
            wait_for_resource("predictor", self.arn, self.aws_handler)
        except ResourceError as e:  # pragma: no cover
            logger.error(
                f"The forecast could not be generated because there was an error {e} when creating the predictor"
            )
            return

        logger.debug(f"Creating forecast {name}")
        forecast_arn = self.aws_handler.forecast.create_forecast(
            ForecastName=name,
            PredictorArn=self.arn,
            ForecastTypes=quantiles,
            Tags=[{"Key": "Name", "Value": self.aws_handler.team}],
        )["ForecastArn"]

        # Wait for forecast to be active before trying to make an export.
        logger.info("Waiting for forecast to be ready...")
        try:
            wait_for_resource("forecast", forecast_arn, self.aws_handler)
        except ResourceError as e:  # pragma: no cover
            logger.error(
                f"The forecast could not be created because there was an error {e} while creating the export"
            )
            return

        # Create the export
        logger.debug(f"Creating forecast export {name}__e to {s3_uri}")
        export_arn = self.aws_handler.forecast.create_forecast_export_job(
            ForecastExportJobName=name + "__e",
            ForecastArn=forecast_arn,
            Destination={
                "S3Config": {
                    "Path": s3_uri,
                    "RoleArn": self.aws_handler.ROLE_ARN,
                }
            },
            Tags=[{"Key": "Name", "Value": self.aws_handler.team}],
        )["ForecastExportJobArn"]

        ## Download exports and join them into the destination csv file.

        # Wait for forecast export to be active before trying download files.
        logger.debug(f"Waiting for forecast export {export_arn} to be ready...")
        try:
            wait_for_resource("forecast_export_job", export_arn, self.aws_handler)
        except ResourceError as e:  # pragma: no cover
            logger.error(
                f"The forecast could not be retrieved because there was an error {e} while creating the forecast"
            )
            return

        # Download the exported csv files and merge them into the destination path.
        logger.debug("Downloading and merging files")
        download_and_merge(s3_uri, destination_path, self.aws_handler)

        # Delete forecast since there is a quota.
        logger.debug(f"Deleting forecast with ARN {forecast_arn}")
        self.aws_handler.forecast.delete_forecast(ForecastArn=forecast_arn)
