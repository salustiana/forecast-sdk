import sys
from os import environ
from time import sleep
import logging
from urllib.parse import urlparse
from tempfile import TemporaryDirectory

import boto3

from sibila.errors import ResourceError

logging.basicConfig()
logger = logging.getLogger("sibila")

logger.setLevel(logging.INFO)


ds_types_short = {
    "TARGET_TIME_SERIES": "TTS",
    "RELATED_TIME_SERIES": "RTS",
    "ITEM_METADATA": "IM",
}


class AWSHandler:
    DEFAULT_AWS_REGION = "us-east-1"
    ROLE_ARN = "arn:aws:iam::628956477585:role/BI-Forecast"
    DOMAIN = "CUSTOM"

    def __init__(
        self,
        team: str,
        s3_uri: str,
        aws_access_key_id: str = environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key: str = environ.get("AWS_SECRET_ACCESS_KEY"),
        aws_session_token: str = environ.get("AWS_SESSION_TOKEN"),
        region_name: str = DEFAULT_AWS_REGION,
    ):

        self.team = team
        self.s3_uri = s3_uri

        logger.debug("Creating s3 client")
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name,
        )

        logger.debug("Creating forecast client")
        self.forecast = boto3.client(
            "forecast",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name,
        )


def wait_for_resource(resource_name: str, resource_arn: str, aws_handler: "AWSHandler"):
    describing_method = getattr(aws_handler.forecast, f"describe_{resource_name}")
    keyword_arg = "".join([word.title() for word in resource_name.split("_")]) + "Arn"

    while True:
        response = describing_method(**{keyword_arg: resource_arn})
        logger.debug(
            f"{resource_name.upper()} {resource_arn} has status {response['Status']}"
        )
        if response["Status"] == "ACTIVE":
            return
        elif response["Status"] == "CREATE_FAILED":
            raise ResourceError(response["Message"])

        sleep(20)

    # status_indicator.end()


def download_and_merge(s3_uri, destination_path, aws_handler):
    parsed_s3_uri = urlparse(s3_uri)
    bucket, prefix = parsed_s3_uri.netloc, parsed_s3_uri.path.lstrip("/")

    file_keys = [
        f["Key"]
        for f in aws_handler.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)[
            "Contents"
        ]
        if f["Key"].endswith(".csv")
    ]

    dest_file = open(destination_path, mode="a")
    with TemporaryDirectory() as tmpdir:  # pragma: no cover
        for i, file_key in enumerate(file_keys):
            logger.debug(
                f"Downloading key {file_key} from bucket {bucket} into {tmpdir}/{i}"
            )
            aws_handler.s3.download_file(
                Bucket=bucket,
                Key=file_key,
                Filename=f"{tmpdir}/{i}",
            )

            # Write header only for first file
            logger.debug(f"Appending {tmpdir}/{i} to {destination_path}")
            if i == 0:
                dest_file.write(open(f"{tmpdir}/{i}").read())
            else:
                dest_file.writelines(open(f"{tmpdir}/{i}").readlines()[1:])
    dest_file.close()
