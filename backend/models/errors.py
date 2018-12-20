
class RequestError(Exception):

    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message


class OperationFailed(RequestError):

    def __init__(self, code="ApiOperationFailed", message=None):
        super().__init__(code=code, message=message)
