from meiga import Result

from petisco import (
    controller_handler,
    JwtConfig,
    HttpError,
    ApplicationConfig,
    InfoId,
    UserId,
)
from petisco.domain.value_objects.name import Name
from petisco.domain.errors.given_input_is_not_valid_error import (
    GivenInputIsNotValidError,
)
from petisco.domain.errors.given_name_is_not_valid_error import GivenNameIsNotValidError
from tests.integration.flask_app.toy_app.application.use_cases.use_case_builder import (
    UseCaseBuilder,
)


def success_handler(result: Result):
    return {"user_id": result.value}, 200


class GivenInputIsNotValidHttpError(HttpError):
    def __init__(self, message: str = "Given input is not valid", code: int = 409):
        super(GivenInputIsNotValidHttpError, self).__init__(message=message, code=code)


def error_handler(result: Result):
    domain_error = result.value
    if isinstance(domain_error, (GivenNameIsNotValidError, GivenInputIsNotValidError)):
        return GivenInputIsNotValidHttpError()


@controller_handler(
    success_handler=success_handler,
    error_handler=error_handler,
    jwt_config=JwtConfig(token_type="ADMIN_TOKEN"),
    application_config=ApplicationConfig.get_instance(),
)
def create_user(client_id, body, headers=None, *args, **kwargs):  # noqa: E501

    info_id = InfoId.from_strings(
        client_id, UserId.generate(), headers.get("X-Correlation-Id")
    )
    name = Name(body.get("name")).guard()

    use_case = UseCaseBuilder.create_user()
    return use_case.execute(info_id=info_id, name=name)
