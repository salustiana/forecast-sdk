import pytest
from unittest.mock import patch

from datetime import datetime

from sibila.utils import AWSHandler
from sibila.errors import DatasetError


def test_project_attributes(project):
    assert project.name == "nombre_de_prueba_1"
    assert project._datasets == {
        "BI_ML_CROSS__demanda_point__TTS": "arn:aws:forecast:us-east-1:628956477585:dataset/BI_ML_CROSS__demanda_point__TTS"
    }
    project._predictors = {"BI_ML_CROSS__ARIMA_demanda": "arn1"}
    assert project.predictors() == ["ARIMA_demanda"]
    assert project.datasets() == ["TARGET_TIME_SERIES"]


@patch("sibila.utils.boto3")
def test_aws_handler_attributes(boto3_mock):
    aws_handler = AWSHandler(
        team="EQUIPO_DE_PRUEBA_1",
        s3_uri="s3://bi-ml-forecasting-data/EQUIPO_DE_PRUEBA_1/nombre_de_prueba_1",
        aws_access_key_id="aws_access_key_id",
        aws_secret_access_key="aws_secret_access_key",
        aws_session_token="aws_session_token",
        region_name="region_name",
    )

    assert aws_handler.team == "EQUIPO_DE_PRUEBA_1"
    assert (
        aws_handler.s3_uri
        == "s3://bi-ml-forecasting-data/EQUIPO_DE_PRUEBA_1/nombre_de_prueba_1"
    )


@patch("sibila.project.isfile")
def test_upload_dataset(isfile_mock, describe_predictor_response, project):

    local_path = "./here.csv"
    ds_type = "TARGET_TIME_SERIES"
    schema = {}
    frequency = "D"
    timestamp_format = "dd:hh"

    project.aws_handler.s3_uri = (
        "s3://bi-ml-forecasting-data/input/EQUIPO_DE_PRUEBA_1/nombre_de_prueba_1"
    )

    # Anything with a STATUS works here
    project.aws_handler.forecast.describe_dataset.return_value = (
        describe_predictor_response
    )

    project.aws_handler.team = "EQUIPO_DE_PRUEBA_1"

    dataset = project.upload_dataset(
        local_path=local_path,
        ds_type=ds_type,
        schema=schema,
        frequency=frequency,
        timestamp_format=timestamp_format,
    )

    assert dataset._ds_name == "EQUIPO_DE_PRUEBA_1__nombre_de_prueba_1__TTS"
    assert (
        dataset.s3_uri
        == "s3://bi-ml-forecasting-data/input/EQUIPO_DE_PRUEBA_1/nombre_de_prueba_1/datasets/TARGET_TIME_SERIES.csv"
    )


@patch("sibila.project.isfile")
def test_upload_dataset_with_existing_name(
    isfile_mock, describe_predictor_response, project
):

    project.aws_handler.forecast.describe_dataset.return_value = {
        "DatasetType": "ITEM_METADATA",
        "Schema": {},
        "DataFrequency": "D",
    }
    project.aws_handler.team = "EQUIPO_DE_PRUEBA_1"
    project.aws_handler.s3_uri = (
        "s3://bi-ml-forecasting-data/input/EQUIPO_DE_PRUEBA_1/nombre_de_prueba_1"
    )

    # Anything with a STATUS works here
    project.aws_handler.forecast.describe_dataset.return_value = (
        describe_predictor_response
    )

    local_path = "./here.csv"
    ds_type = "TARGET_TIME_SERIES"
    schema = {}
    frequency = "D"
    timestamp_format = "dd:hh"

    ds_name = f"{project.aws_handler.team}__{project.name}__{ds_type}"
    project._datasets = {ds_name: "fake_arn"}

    dataset = project.upload_dataset(
        local_path=local_path,
        ds_type=ds_type,
        schema=schema,
        frequency=frequency,
        timestamp_format=timestamp_format,
    )

    assert dataset._ds_name == "EQUIPO_DE_PRUEBA_1__nombre_de_prueba_1__TTS"
    assert (
        dataset.s3_uri
        == "s3://bi-ml-forecasting-data/input/EQUIPO_DE_PRUEBA_1/nombre_de_prueba_1/datasets/TARGET_TIME_SERIES.csv"
    )


def test_train_new_predictor(describe_predictor_response, project):
    # Anything with a STATUS works here

    predictor = project.train_new_predictor(
        name="test_predictor",
        algorithm="ARIMA",
        horizon=30,
        frequency="D",
        featurizations=[{"a": 2}],
        supplementary_features=[{"Name": "Juan", "Value": "Carlos"}],
    )

    assert predictor.name == "test_predictor"


def test_train_new_predictor_with_failed_import(
    project,
):

    project.imports = {"a": "b"}
    project.aws_handler.forecast.describe_dataset_import_job.return_value = {
        "Status": "CREATE_FAILED",
        "Message": "Some error",
    }

    predictor = project.train_new_predictor(
        name="test_predictor",
        algorithm="ARIMA",
        horizon=30,
        frequency="D",
        featurizations=[{"a": 2}],
    )

    # Check if the import was deleted from the project's imports
    assert project.imports == {}


def test_get_dataset_to_csv(
    project,
):

    team = "EQUIPO_DE_PRUEBA_1"

    project.aws_handler.team = team

    project._datasets = {
        "EQUIPO_DE_PRUEBA_1__nombre_de_prueba_1__IM": "test_dataset_arn"
    }
    project.imports = {
        f'IM__{str(datetime.now().timestamp()).replace(".", "_")}': "test_dataset_import_arn"
    }

             

    dataset = project.get_dataset("ITEM_METADATA")

    dataset.to_csv("./here")

    assert dataset._ds_name == "EQUIPO_DE_PRUEBA_1__nombre_de_prueba_1__IM"
    # This uri comes from describe_dataset_response
    assert (
        dataset.s3_uri
        == "s3://bi-ml-forecasting-data/input/mi_equipo/forecast_demanda_producto/TARGET_TIME_SERIES/demanada_2018_a_2020.csv"
    )


def test_get_predictor(project):

    project.aws_handler.team = "EQUIPO_DE_PRUEBA_1"

    predictor_name = f"{project.aws_handler.team}__test_predictor"
    project._predictors = {predictor_name: "test_predictor_arn"}

    predictor = project.get_predictor("test_predictor")
    assert predictor.arn == "test_predictor_arn"


def test_upload_dataset_fails_if_csv_is_invalid(project):

    project.aws_handler.s3_uri = (
        "s3://bi-ml-forecasting-data/input/EQUIPO_DE_PRUEBA_1/nombre_de_prueba_1"
    )

    local_path = "./here2.csv"
    ds_type = "TARGET_TIME_SERIES"
    schema = {}
    frequency = "D"
    timestamp_format = "dd:hh"
    with pytest.raises(DatasetError):
        dataset = project.upload_dataset(
            local_path=local_path,
            ds_type=ds_type,
            schema=schema,
            frequency=frequency,
            timestamp_format=timestamp_format,
        )
