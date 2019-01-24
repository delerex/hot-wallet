
class RequestError(Exception):

    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message

    def __repr__(self):
        return f"{self.__class__}[{self.code}]: {self.message}"

    def __str__(self):
        return self.__repr__()


class OperationFailed(RequestError):

    def __init__(self, message=None):
        super().__init__(code="ApiOperationFailed", message=message)


class ApiInsufficientFund(RequestError):

    def __init__(self, message=None):
        super().__init__(code="ApiInsufficientFund", message=message)


class ApiObjectNotFound(RequestError):

    def __init__(self, message=None):
        super().__init__(code="ApiObjectNotFound", message=message)


class ApiUnexpectedError(RequestError):

    def __init__(self, message=None):
        super().__init__(code="ApiUnexpectedError", message=message)
