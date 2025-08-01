class NetworkAutomationException(Exception):
    """
    Base exception class for the network automation application
    """
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class DatabaseException(NetworkAutomationException):
    """
    Exception raised for database errors
    """
    pass

class AuthenticationException(NetworkAutomationException):
    """
    Exception raised for authentication errors
    """
    pass

class AuthorizationException(NetworkAutomationException):
    """
    Exception raised for authorization errors
    """
    pass

class DeviceConnectionException(NetworkAutomationException):
    """
    Exception raised for device connection errors
    """
    pass

class DeviceNotFoundException(NetworkAutomationException):
    """
    Exception raised when a device is not found
    """
    pass

class ConfigurationException(NetworkAutomationException):
    """
    Exception raised for configuration-related errors
    """
    pass

class LLMException(NetworkAutomationException):
    """
    Exception raised for LLM-related errors
    """
    pass

class NetworkOperationException(NetworkAutomationException):
    """
    Exception raised for network operation errors
    """
    pass

class ChatException(NetworkAutomationException):
    """
    Exception raised for chat-related errors
    """
    pass

class ValidationException(NetworkAutomationException):
    """
    Exception raised for validation errors
    """
    pass

class RateLimitException(NetworkAutomationException):
    """
    Exception raised when rate limits are exceeded
    """
    pass

# HTTP Exception Classes for API responses
class HTTPException(Exception):
    """
    Base HTTP exception for API responses
    """
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class BadRequestException(HTTPException):
    """
    HTTP 400 Bad Request
    """
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(400, detail)

class UnauthorizedException(HTTPException):
    """
    HTTP 401 Unauthorized
    """
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(401, detail)

class ForbiddenException(HTTPException):
    """
    HTTP 403 Forbidden
    """
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(403, detail)

class NotFoundException(HTTPException):
    """
    HTTP 404 Not Found
    """
    def __init__(self, detail: str = "Not Found"):
        super().__init__(404, detail)

class ConflictException(HTTPException):
    """
    HTTP 409 Conflict
    """
    def __init__(self, detail: str = "Conflict"):
        super().__init__(409, detail)

class InternalServerErrorException(HTTPException):
    """
    HTTP 500 Internal Server Error
    """
    def __init__(self, detail: str = "Internal Server Error"):
        super().__init__(500, detail)

class ServiceUnavailableException(HTTPException):
    """
    HTTP 503 Service Unavailable
    """
    def __init__(self, detail: str = "Service Unavailable"):
        super().__init__(503, detail)