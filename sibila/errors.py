class UnableToLoginError(Exception):
    pass


class AutoforecastException(Exception):
    pass


class DatasetError(AutoforecastException):
    pass


class PredictorError(AutoforecastException):
    pass


class AWSHandlerError(Exception):
    pass


class ResourceError(AWSHandlerError):
    pass
