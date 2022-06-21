from urllib.parse import urlparse

from melitk import logging

from sibila.errors import DatasetError
from sibila.utils import wait_for_resource, logger


class Dataset:

    TARGET_TIME_SERIES = "TARGET_TIME_SERIES"
    RELATED_TIME_SERIES = "RELATED_TIME_SERIES"
    ITEM_METADATA = "ITEM_METADATA"

    VALID_DATASET_TYPES = (TARGET_TIME_SERIES, RELATED_TIME_SERIES, ITEM_METADATA)

    def __init__(
        self,
        dsg_arn: str,
        ds_type: str,
        schema: dict,
        s3_uri: str,
        aws_handler: "AWSHandler",
        frequency: str = None,
        timestamp_format: str = None,
    ):
        if ds_type not in Dataset.VALID_DATASET_TYPES:
            raise DatasetError(f"Valid dataset types are {Dataset.VALID_DATASET_TYPES}")

        if (ds_type != Dataset.ITEM_METADATA) and not (frequency and timestamp_format):
            raise DatasetError(
                "You must specify a frequency and a timestamp_format for this type of dataset."
            )

        self.dsg_arn = dsg_arn
        self.ds_type = ds_type
        self.schema = schema
        self.frequency = frequency
        # TODO: parsear con datetime y validar.
        self.timestamp_format = timestamp_format
        self.s3_uri = s3_uri
        self.aws_handler = aws_handler

        # These are set either when the dataset is instantiated or manually set upon retrieval.
        self._ds_name = None
        self._import_name = None
        self.arn = None
        self.import_arn = None

    def _create(self):
        creation_request = {
            "Domain": self.aws_handler.DOMAIN,
            "DatasetType": self.ds_type,
            "DatasetName": self._ds_name,
            "Schema": self.schema,
            "Tags": [{"Key": "Name", "Value": self.aws_handler.team}],
        }

        if self.frequency:
            creation_request["DataFrequency"] = self.frequency

        # Instantiates the dataset in the forecast service.
        response_ds = self.aws_handler.forecast.create_dataset(**creation_request)

        logger.debug(f"Dataset creation response: {response_ds}")

        dataset_arn = response_ds["DatasetArn"]

        return dataset_arn

    def _create_import(self):

        # Wait for the dataset to be active before trying to create an import.
        wait_for_resource("dataset", self.arn, self.aws_handler)
        wait_for_resource("dataset_group", self.dsg_arn, self.aws_handler)

        # Instantiate the import in the forecast service.
        logger.debug(
            f"Creating import {self._import_name} that points to {self.s3_uri}"
        )

        creation_request = {
            "DatasetImportJobName": self._import_name,
            "DatasetArn": self.arn,
            "DataSource": {
                "S3Config": {
                    "Path": self.s3_uri,
                    "RoleArn": self.aws_handler.ROLE_ARN,
                }
            },
            "Tags": [{"Key": "Name", "Value": self.aws_handler.team}],
        }

        if self.timestamp_format:
            creation_request["TimestampFormat"] = self.timestamp_format

        response_import = self.aws_handler.forecast.create_dataset_import_job(
            **creation_request
        )

        logger.debug(f"Import creation response: {response_import}")

        self.import_arn = response_import["DatasetImportJobArn"]

    def to_csv(self, destination: str):
        parsed_s3_uri = urlparse(self.s3_uri)
        bucket, key = parsed_s3_uri.netloc, parsed_s3_uri.path.lstrip("/")

        self.aws_handler.s3.download_file(
            Bucket=bucket,
            Key=key,
            Filename=destination,
        )

    # def to_df(self):
    # pass
