from functools import wraps
import traceback
from typing import Callable, Tuple, Dict, List, Any

from meiga import Result
from meiga.decorators import meiga

from petisco.application.application_config import ApplicationConfig
from petisco.controller.errors.internal_http_error import InternalHttpError
from petisco.controller.errors.known_result_failure_handler import (
    KnownResultFailureHandler,
)
from petisco.controller.tokens.jwt_decorator import jwt
from petisco.domain.aggregate_roots.info_id import InfoId
from petisco.events.request_responded import RequestResponded
from petisco.events.event_config import EventConfig
from petisco.frameworks.flask.flask_headers_provider import flask_headers_provider
from petisco.logger.interface_logger import ERROR, INFO
from petisco.controller.errors.http_error import HttpError
from petisco.controller.tokens.jwt_config import JwtConfig
from petisco.logger.log_message import LogMessage
from petisco.logger.not_implemented_logger import NotImplementedLogger
from petisco.tools.timer import timer

DEFAULT_SUCCESS_MESSAGE = {"message": "OK"}, 200
DEFAULT_ERROR_MESSAGE = HttpError().handle()


class _ControllerHandler:
    def set_application_config(self, application_config: ApplicationConfig):
        if application_config:
            self.app_name = application_config.app_name
            self.app_version = application_config.app_version
            self.logger = application_config.logger
            if self.event_config.is_configured:
                self.event_config.event_manager = application_config.event_manager

    def __init__(
        self,
        app_name: str = "app-undefined",
        app_version: str = None,
        logger=NotImplementedLogger(),
        event_config: EventConfig = EventConfig(),
        jwt_config: JwtConfig = None,
        success_handler: Callable[[Result], Tuple[Dict, int]] = None,
        error_handler: Callable[[Result], HttpError] = None,
        headers_provider: Callable = flask_headers_provider,
        logging_types_blacklist: List[Any] = [bytes],
        application_config: ApplicationConfig = None,
    ):
        """
        Parameters
        ----------
        app_name
            Application Name
        app_version
            Application Version
        logger
            A ILogger implementation. Default NotImplementedLogger
        event_config
            EventConfig object. Here, you can define event management.
        jwt_config
            JwtConfig object. Here, you can define how to deal with JWT Tokens
        success_handler
            Handler to deal with Success Results
        error_handler
            Handler to deal with Failure Results
        headers_provider
            Injectable function to provide headers. By default is used headers_provider
        logging_types_blacklist
            Logging Blacklist. Object of defined Type will not be logged. By default ( [bytes] ) bytes object won't be logged.
        application_config
            Use ApplicationConfig to set params as: app_name, app_version, logger, or event_manager (EventConfig)
        """
        self.app_name = app_name
        self.app_version = app_version
        self.logger = logger
        self.event_config = event_config
        self.jwt_config = jwt_config
        self.success_handler = success_handler
        self.error_handler = error_handler
        self.headers_provider = headers_provider
        self.logging_types_blacklist = logging_types_blacklist
        self.set_application_config(application_config)

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def wrapper(*args, **kwargs):
            @timer
            @meiga
            @jwt(jwt_config=self.jwt_config)
            def run_controller(*args, **kwargs) -> Result:
                return func(*args, **kwargs)

            kwargs = add_headers(kwargs)
            info_id = InfoId.from_headers(kwargs.get("headers"))

            log_message = LogMessage(
                layer="controller", operation=f"{func.__name__}", info_id=info_id
            )

            http_response = DEFAULT_ERROR_MESSAGE
            is_success = False
            elapsed_time = None
            try:
                log_message.message = "Start"
                self.logger.log(INFO, log_message.to_json())
                result, elapsed_time = run_controller(*args, **kwargs)

                if result.is_success:
                    if isinstance(result.value, tuple(self.logging_types_blacklist)):
                        log_message.message = (
                            f"Success result of type: {type(result.value).__name__}"
                        )
                    else:
                        log_message.message = f"{result}"
                    self.logger.log(INFO, log_message.to_json())
                    http_response = (
                        self.success_handler(result)
                        if self.success_handler
                        else DEFAULT_SUCCESS_MESSAGE
                    )
                    is_success = True
                else:
                    log_message.message = f"{result}"
                    self.logger.log(ERROR, log_message.to_json())
                    known_result_failure_handler = KnownResultFailureHandler(result)

                    if not known_result_failure_handler.is_a_result_known_error:
                        if self.error_handler:
                            http_error = self.error_handler(result)

                            if not issubclass(http_error.__class__, HttpError):
                                raise TypeError(
                                    "Returned object from error_handler must be subclasses of HttpError"
                                )

                            http_response = http_error.handle()
                    else:
                        http_response = known_result_failure_handler.http_error.handle()

            except Exception as e:
                log_message.message = f"Error {func.__name__}: {repr(e.__class__)} {e} | {traceback.format_exc()}"
                self.logger.log(ERROR, log_message.to_json())
                http_response = InternalHttpError().handle()

            request_responded = RequestResponded(
                app_name=self.app_name,
                app_version=self.app_version,
                controller=f"{func.__name__}",
                is_success=is_success,
                http_response=http_response,
                elapsed_time=elapsed_time,
                additional_info=self.event_config.get_additional_info(kwargs),
            ).add_info_id(info_id)
            self.event_config.event_manager.publish(
                topic=self.event_config.event_topic, event=request_responded
            )

            return http_response

        def add_headers(kwargs):
            headers = self.headers_provider()
            kwargs = dict(kwargs, headers=headers)

            return kwargs

        return wrapper


controller_handler = _ControllerHandler
