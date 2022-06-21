import pytest
import datetime
from unittest.mock import patch
import requests_mock
from http import HTTPStatus

from sibila.project import Project


def tzlocal():
    return


@pytest.fixture()
def project(
    describe_dataset_group_response,
    list_predictors_response,
    describe_dataset_import_job_response,
    describe_dataset_response,
    describe_predictor_response,
):
    with patch("sibila.project.AWSHandler") as handler:
        mocked_handler = handler.return_value
        mocked_handler.forecast.describe_dataset_group.return_value = (
            describe_dataset_group_response
        )
        mocked_handler.forecast.describe_dataset.return_value = (
            describe_dataset_response
        )
        mocked_handler.forecast.list_predictors.return_value = list_predictors_response
        mocked_handler.forecast.describe_dataset_import_job.return_value = (
            describe_dataset_import_job_response
        )
        mocked_handler.forecast.describe_predictor.return_value = (
            describe_predictor_response
        )

        # For all the responses below anything with a STATUS passes all tests
        mocked_handler.forecast.describe_forecast.return_value = (
            describe_predictor_response
        )
        mocked_handler.forecast.describe_forecast_export_job.return_value = (
            describe_predictor_response
        )
        mocked_handler.forecast.describe_forecast_backtest_export_job.return_value = (
            describe_predictor_response
        )
        mocked_handler.forecast.describe_predictor_backtest_export_job.return_value = (
            describe_predictor_response
        )

        mocked_handler.team = "EQUIPO_DE_PRUEBA_1"
        with requests_mock.Mocker() as request_mock:
            request_mock.post(
                "https://internal-api.mercadolibre.com/data-team/auth/login",
                status_code=HTTPStatus.NO_CONTENT,
            )
            project = Project(
                name="nombre-de_prueba-1",
                team="equipo_de-prueba-1",
                username="username",
                password="password",
                aws_access_key_id="a",
                aws_secret_access_key="b",
                aws_session_token="c",
                region_name="region",
            )
            return project


@pytest.fixture()
def list_predictors_response():
    return {
        "Predictors": [
            {
                "PredictorArn": "arn:aws:forecast:us-east-1:628956477585:predictor/BI_ML_CROSS__ARIMA_demanda",
                "PredictorName": "BI_ML_CROSS__ARIMA_demanda",
                "DatasetGroupArn": "arn:aws:forecast:us-east-1:628956477585:dataset-group/BI_ML_CROSS__demanda_point",
                "Status": "ACTIVE",
                "CreationTime": datetime.datetime(
                    2020, 12, 22, 17, 47, 41, 4000, tzinfo=tzlocal()
                ),
                "LastModificationTime": datetime.datetime(
                    2020, 12, 22, 19, 40, 32, 426000, tzinfo=tzlocal()
                ),
            },
            {
                "PredictorArn": "arn:aws:forecast:us-east-1:628956477585:predictor/forecast_ventas_all",
                "PredictorName": "forecast_ventas_all",
                "DatasetGroupArn": "arn:aws:forecast:us-east-1:628956477585:dataset-group/MGG_MLA_CE_ALL",
                "Status": "CREATE_FAILED",
                "Message": "Items found in the TARGET_TIME_SERIES dataset are missing from the ITEM_METADATA dataset. A total of 153 items are missing from the ITEM_METADATA dataset.",
                "CreationTime": datetime.datetime(
                    2020, 11, 27, 9, 44, 23, 249000, tzinfo=tzlocal()
                ),
                "LastModificationTime": datetime.datetime(
                    2020, 11, 27, 9, 54, 12, 814000, tzinfo=tzlocal()
                ),
            },
            {
                "PredictorArn": "arn:aws:forecast:us-east-1:628956477585:predictor/ventas_publicaiones",
                "PredictorName": "ventas_publicaiones",
                "DatasetGroupArn": "arn:aws:forecast:us-east-1:628956477585:dataset-group/Ventas_metadata",
                "Status": "ACTIVE",
                "CreationTime": datetime.datetime(
                    2020, 11, 23, 22, 19, 18, 796000, tzinfo=tzlocal()
                ),
                "LastModificationTime": datetime.datetime(
                    2020, 11, 24, 0, 5, 36, 620000, tzinfo=tzlocal()
                ),
            },
            {
                "PredictorArn": "arn:aws:forecast:us-east-1:628956477585:predictor/solo_ventas_est",
                "PredictorName": "solo_ventas_est",
                "DatasetGroupArn": "arn:aws:forecast:us-east-1:628956477585:dataset-group/MGG_MLA_CE_ONLY_SALES",
                "Status": "ACTIVE",
                "CreationTime": datetime.datetime(
                    2020, 11, 23, 18, 30, 38, 380000, tzinfo=tzlocal()
                ),
                "LastModificationTime": datetime.datetime(
                    2020, 11, 23, 20, 6, 8, 993000, tzinfo=tzlocal()
                ),
            },
            {
                "PredictorArn": "arn:aws:forecast:us-east-1:628956477585:predictor/ventas_est",
                "PredictorName": "ventas_est",
                "DatasetGroupArn": "arn:aws:forecast:us-east-1:628956477585:dataset-group/MGG_MLA_CE",
                "Status": "ACTIVE",
                "CreationTime": datetime.datetime(
                    2020, 11, 23, 16, 13, 49, 621000, tzinfo=tzlocal()
                ),
                "LastModificationTime": datetime.datetime(
                    2020, 11, 23, 16, 44, 35, 900000, tzinfo=tzlocal()
                ),
            },
            {
                "PredictorArn": "arn:aws:forecast:us-east-1:628956477585:predictor/MLM_predictor_till_august",
                "PredictorName": "MLM_predictor_till_august",
                "DatasetGroupArn": "arn:aws:forecast:us-east-1:628956477585:dataset-group/item_variation_forecast",
                "Status": "ACTIVE",
                "CreationTime": datetime.datetime(
                    2020, 11, 19, 13, 35, 50, 69000, tzinfo=tzlocal()
                ),
                "LastModificationTime": datetime.datetime(
                    2020, 11, 19, 16, 47, 6, 477000, tzinfo=tzlocal()
                ),
            },
            {
                "PredictorArn": "arn:aws:forecast:us-east-1:628956477585:predictor/my_modelo",
                "PredictorName": "my_modelo",
                "DatasetGroupArn": "arn:aws:forecast:us-east-1:628956477585:dataset-group/mlseeds_forecast",
                "Status": "ACTIVE",
                "CreationTime": datetime.datetime(
                    2020, 10, 15, 15, 28, 32, 159000, tzinfo=tzlocal()
                ),
                "LastModificationTime": datetime.datetime(
                    2020, 10, 15, 15, 45, 17, 464000, tzinfo=tzlocal()
                ),
            },
        ],
        "ResponseMetadata": {
            "RequestId": "32506860-76f1-4d64-ad39-527e3f3fc2bd",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "content-type": "application/x-amz-json-1.1",
                "date": "Mon, 28 Dec 2020 13:24:35 GMT",
                "x-amzn-requestid": "32506860-76f1-4d64-ad39-527e3f3fc2bd",
                "content-length": "2335",
                "connection": "keep-alive",
            },
            "RetryAttempts": 0,
        },
    }


@pytest.fixture()
def describe_dataset_group_response():
    return {
        "DatasetGroupName": "BI_ML_CROSS__demanda_point",
        "DatasetGroupArn": "arn:aws:forecast:us-east-1:628956477585:dataset-group/BI_ML_CROSS__demanda_point",
        "DatasetArns": [
            "arn:aws:forecast:us-east-1:628956477585:dataset/BI_ML_CROSS__demanda_point__TTS"
        ],
        "Domain": "CUSTOM",
        "Status": "ACTIVE",
        "CreationTime": datetime.datetime(
            2020, 12, 22, 15, 45, 44, 878000, tzinfo=tzlocal()
        ),
        "LastModificationTime": datetime.datetime(
            2020, 12, 22, 17, 47, 58, 522000, tzinfo=tzlocal()
        ),
        "ResponseMetadata": {
            "RequestId": "2cf84b7c-3c05-4227-94d1-4195ba7c4d71",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "content-type": "application/x-amz-json-1.1",
                "date": "Mon, 28 Dec 2020 15:09:14 GMT",
                "x-amzn-requestid": "2cf84b7c-3c05-4227-94d1-4195ba7c4d71",
                "content-length": "356",
                "connection": "keep-alive",
            },
            "RetryAttempts": 0,
        },
    }


@pytest.fixture()
def describe_dataset_import_job_response():
    return {
        "DatasetImportJobName": "demanada_2018_a_2020_import",
        "DatasetImportJobArn": "arn:aws:forecast:us-east-1:628956477585:dataset-import-job/demanada_2018_a_2020/demanada_2018_a_2020_import",
        "DatasetArn": "arn:aws:forecast:us-east-1:628956477585:dataset/demanada_2018_a_2020",
        "TimestampFormat": "yyyy-MM-dd hh:mm:ss",
        "UseGeolocationForTimeZone": False,
        "DataSource": {
            "S3Config": {
                "Path": "s3://bi-ml-forecasting-data/input/mi_equipo/forecast_demanda_producto/TARGET_TIME_SERIES/demanada_2018_a_2020.csv",
                "RoleArn": "arn:aws:iam::628956477585:role/BI-Forecast",
            }
        },
        "FieldStatistics": {
            "item_id": {"Count": 23973, "CountDistinct": 3, "CountNull": 0},
            "target_value": {
                "Count": 23973,
                "CountDistinct": 4818,
                "CountNull": 0,
                "CountNan": 0,
                "Min": "0.0",
                "Max": "212.27197346600326",
                "Avg": 50.44732317068067,
                "Stddev": 38.72169238224657,
            },
            "timestamp": {
                "Count": 23973,
                "CountDistinct": 7991,
                "CountNull": 0,
                "Min": "2014-01-01T01:00:00Z",
                "Max": "2014-11-29T23:00:00Z",
            },
        },
        "DataSize": 0.0010688817128539085,
        "Status": "ACTIVE",
        "CreationTime": datetime.datetime(
            2020, 12, 11, 16, 2, 26, 674000, tzinfo=tzlocal()
        ),
        "LastModificationTime": datetime.datetime(
            2020, 12, 11, 16, 37, 4, 803000, tzinfo=tzlocal()
        ),
        "ResponseMetadata": {
            "RequestId": "2d6c10c9-04e6-43b4-9426-331df24be55d",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "content-type": "application/x-amz-json-1.1",
                "date": "Mon, 14 Dec 2020 13:15:20 GMT",
                "x-amzn-requestid": "2d6c10c9-04e6-43b4-9426-331df24be55d",
                "content-length": "1238",
                "connection": "keep-alive",
            },
            "RetryAttempts": 0,
        },
    }


@pytest.fixture()
def describe_dataset_response():
    return {
        "DatasetArn": "arn:aws:forecast:us-east-1:628956477585:dataset/generate_periodic_func__70__5_4_0_5__0_4_0_5",
        "DatasetName": "generate_periodic_func__70__5_4_0_5__0_4_0_5",
        "Domain": "RETAIL",
        "DatasetType": "TARGET_TIME_SERIES",
        "DataFrequency": "D",
        "Schema": {
            "Attributes": [
                {"AttributeName": "item_id", "AttributeType": "string"},
                {"AttributeName": "timestamp", "AttributeType": "timestamp"},
                {"AttributeName": "demand", "AttributeType": "float"},
            ]
        },
        "EncryptionConfig": {},
        "Status": "ACTIVE",
        "CreationTime": datetime.datetime(
            2020, 10, 19, 15, 50, 53, 341000, tzinfo=tzlocal()
        ),
        "LastModificationTime": datetime.datetime(
            2020, 10, 19, 17, 28, 41, 166000, tzinfo=tzlocal()
        ),
        "ResponseMetadata": {
            "RequestId": "4c4417b2-a7d9-4fc5-a41a-323ecdc030db",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "content-type": "application/x-amz-json-1.1",
                "date": "Mon, 14 Dec 2020 13:19:39 GMT",
                "x-amzn-requestid": "4c4417b2-a7d9-4fc5-a41a-323ecdc030db",
                "content-length": "543",
                "connection": "keep-alive",
            },
            "RetryAttempts": 0,
        },
    }


@pytest.fixture()
def describe_predictor_response():
    return {
        "PredictorArn": "arn:aws:forecast:us-east-1:628956477585:predictor/predictor_1",
        "PredictorName": "predictor_1",
        "ForecastHorizon": 80,
        "ForecastTypes": ["0.1", "0.5", "0.9"],
        "PerformAutoML": True,
        "TrainingParameters": {
            "context_length": "483",
            "epochs": "100",
            "use_item_metadata": "NONE",
            "use_related_data": "HISTORICAL",
        },
        "EvaluationParameters": {
            "NumberOfBacktestWindows": 1,
            "BackTestWindowOffset": 80,
        },
        "InputDataConfig": {
            "DatasetGroupArn": "arn:aws:forecast:us-east-1:628956477585:dataset-group/testing_func_fit"
        },
        "FeaturizationConfig": {
            "ForecastFrequency": "D",
            "ForecastDimensions": ["D", "B"],
            "Featurizations": [
                {
                    "AttributeName": "demand",
                    "FeaturizationPipeline": [
                        {
                            "FeaturizationMethodName": "filling",
                            "FeaturizationMethodParameters": {
                                "aggregation": "sum",
                                "backfill": "zero",
                                "frontfill": "none",
                                "middlefill": "zero",
                            },
                        }
                    ],
                }
            ],
        },
        "PredictorExecutionDetails": {
            "PredictorExecutions": [
                {
                    "AlgorithmArn": "arn:aws:forecast:::algorithm/ETS",
                    "TestWindows": [
                        {
                            "TestWindowStart": datetime.datetime(
                                2021, 1, 24, 21, 0, tzinfo=tzlocal()
                            ),
                            "TestWindowEnd": datetime.datetime(
                                2021, 4, 14, 21, 0, tzinfo=tzlocal()
                            ),
                            "Status": "ACTIVE",
                        }
                    ],
                },
                {
                    "AlgorithmArn": "arn:aws:forecast:::algorithm/CNN-QR",
                    "TestWindows": [
                        {
                            "TestWindowStart": datetime.datetime(
                                2021, 1, 24, 21, 0, tzinfo=tzlocal()
                            ),
                            "TestWindowEnd": datetime.datetime(
                                2021, 4, 14, 21, 0, tzinfo=tzlocal()
                            ),
                            "Status": "ACTIVE",
                        }
                    ],
                },
                {
                    "AlgorithmArn": "arn:aws:forecast:::algorithm/NPTS",
                    "TestWindows": [
                        {
                            "TestWindowStart": datetime.datetime(
                                2021, 1, 24, 21, 0, tzinfo=tzlocal()
                            ),
                            "TestWindowEnd": datetime.datetime(
                                2021, 4, 14, 21, 0, tzinfo=tzlocal()
                            ),
                            "Status": "ACTIVE",
                        }
                    ],
                },
                {
                    "AlgorithmArn": "arn:aws:forecast:::algorithm/Prophet",
                    "TestWindows": [
                        {
                            "TestWindowStart": datetime.datetime(
                                2021, 1, 24, 21, 0, tzinfo=tzlocal()
                            ),
                            "TestWindowEnd": datetime.datetime(
                                2021, 4, 14, 21, 0, tzinfo=tzlocal()
                            ),
                            "Status": "ACTIVE",
                        }
                    ],
                },
                {
                    "AlgorithmArn": "arn:aws:forecast:::algorithm/ARIMA",
                    "TestWindows": [
                        {
                            "TestWindowStart": datetime.datetime(
                                2021, 1, 24, 21, 0, tzinfo=tzlocal()
                            ),
                            "TestWindowEnd": datetime.datetime(
                                2021, 4, 14, 21, 0, tzinfo=tzlocal()
                            ),
                            "Status": "ACTIVE",
                        }
                    ],
                },
                {
                    "AlgorithmArn": "arn:aws:forecast:::algorithm/Deep_AR_Plus",
                    "TestWindows": [
                        {
                            "TestWindowStart": datetime.datetime(
                                2021, 1, 24, 21, 0, tzinfo=tzlocal()
                            ),
                            "TestWindowEnd": datetime.datetime(
                                2021, 4, 14, 21, 0, tzinfo=tzlocal()
                            ),
                            "Status": "ACTIVE",
                        }
                    ],
                },
            ]
        },
        "DatasetImportJobArns": [
            "arn:aws:forecast:us-east-1:628956477585:dataset-import-job/generate_periodic_func__70__5_4_0_5__0_4_0_5/prueba_2"
        ],
        "AutoMLAlgorithmArns": ["arn:aws:forecast:::algorithm/CNN-QR"],
        "Status": "ACTIVE",
        "CreationTime": datetime.datetime(
            2020, 10, 19, 17, 37, 6, 44000, tzinfo=tzlocal()
        ),
        "LastModificationTime": datetime.datetime(
            2020, 10, 20, 12, 2, 17, 788000, tzinfo=tzlocal()
        ),
        "ResponseMetadata": {
            "RequestId": "05f6d2e6-2b9d-4d7b-aea7-8e1e841181d7",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "content-type": "application/x-amz-json-1.1",
                "date": "Mon, 14 Dec 2020 13:41:28 GMT",
                "x-amzn-requestid": "05f6d2e6-2b9d-4d7b-aea7-8e1e841181d7",
                "content-length": "2008",
                "connection": "keep-alive",
            },
            "RetryAttempts": 0,
        },
    }
