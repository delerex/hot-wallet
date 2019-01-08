
class RequestError(Exception):

    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message

    def __repr__(self):
        return f"{self.__class__}[{self.code}]: {self.message}"

    def __str__(self):
        return self.__repr__()


class OperationFailed(RequestError):

    def __init__(self, code="ApiOperationFailed", message=None):
        super().__init__(code=code, message=message)


class ApiInsufficientFund(RequestError):

    def __init__(self, code="ApiInsufficientFund", message=None):
        super().__init__(code=code, message=message)


class ApiUnexpectedError(RequestError):

    def __init__(self, code="ApiUnexpectedError", message=None):
        super().__init__(code=code, message=message)
