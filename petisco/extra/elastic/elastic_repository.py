from typing import Any, Union

from meiga import BoolResult, Error, Failure, isSuccess

from petisco import Uuid
from petisco.base.application.patterns.repository import Repository
from petisco.base.domain.errors.defaults.already_exists import (
    AggregateAlreadyExistError,
)
from petisco.base.domain.errors.defaults.not_found import (
    AggregateNotFoundError,
    AggregatesNotFoundError,
)
from petisco.base.domain.persistence.databases import databases
from petisco.extra.elastic.elastic_database import ElasticDatabase, ElasticSessionScope


class ElasticRepository(Repository):
    session_scope: ElasticSessionScope

    def __init__(self, database_alias: str):
        """
        Constructs the ElasticRepository from a database_alias creating a session_scope (ElasticSessionScope)

        Args:
            database_alias (str): A str you defined in database_alias the DatabaseConfigurer
        """
        database = databases.get(ElasticDatabase, alias=database_alias)
        self.session_scope = database.get_session_scope()

    @classmethod
    def fail_if_aggregate_already_exist(
        cls, model: Any, aggregate_id: Uuid, result_error: Union[Error, None] = None
    ) -> BoolResult:
        if model:
            error = (
                AggregateAlreadyExistError(
                    aggregate_id, cls.__name__, model.__tablename__
                )
                if not result_error
                else result_error
            )
            return Failure(error)
        return isSuccess

    @classmethod
    def fail_if_aggregate_not_found(
        cls, model: Any, aggregate_id: Uuid, result_error: Union[Error, None] = None
    ) -> BoolResult:
        if not model:
            error = (
                AggregateNotFoundError(aggregate_id, cls.__name__)
                if not result_error
                else result_error
            )
            return Failure(error)
        return isSuccess

    @classmethod
    def fail_if_aggregates_not_found(
        cls, model: Any, result_error: Union[Error, None] = None
    ) -> BoolResult:
        if not model:
            error = (
                AggregatesNotFoundError(cls.__name__)
                if not result_error
                else result_error
            )
            return Failure(error)
        return isSuccess
