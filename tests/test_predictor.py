from os.path import isfile, isdir
from unittest.mock import patch


def test_forecast(
    describe_dataset_group_response, describe_predictor_response, project
):

    project.aws_handler.team = "EQUIPO_DE_PRUEBA_1"

    predictor_name = f"{project.aws_handler.team}__test_predictor"
    project._predictors = {predictor_name: "test_predictor_arn"}

    project.aws_handler.forecast.describe_forecast_export_job.return_value = (
        describe_predictor_response
    )

    predictor = project.get_predictor("test_predictor")
    with patch("sibila.predictor.wait_for_resource"):
        predictor.forecast("./here3")
    assert isfile("./here3")


def test_predictor_metrics(
    describe_dataset_group_response, describe_predictor_response, project
):

    predictor_name = f"{project.aws_handler.team}__test_predictor"
    project._predictors = {predictor_name: "test_predictor_arn"}

    # Anything with a STATUS works here
    project.aws_handler.forecast.describe_predictor_backtest_export_job.return_value = (
        describe_predictor_response
    )

    predictor = project.get_predictor("test_predictor")
    predictor.metrics("./test_metrics")
    assert isdir("./test_metrics")
