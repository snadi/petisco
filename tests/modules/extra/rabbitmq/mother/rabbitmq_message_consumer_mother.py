from petisco.base.domain.message.chaos.message_chaos import MessageChaos
from petisco.extra.rabbitmq import RabbitMqMessageConsumer
from petisco.legacy import RabbitMqConnector

from petisco.legacy.logger.interface_logger import ILogger
from petisco.legacy.logger.not_implemented_logger import NotImplementedLogger
from tests.modules.extra.rabbitmq.mother.defaults import (
    DEFAULT_ORGANIZATION,
    DEFAULT_SERVICE,
    DEFAULT_MAX_RETRIES,
    DEFAULT_VERBOSE,
)


class RabbitMqMessageConsumerMother:
    @staticmethod
    def default(connector: RabbitMqConnector = None):
        connector = RabbitMqConnector() if not connector else connector
        return RabbitMqMessageConsumer(
            connector,
            DEFAULT_ORGANIZATION,
            DEFAULT_SERVICE,
            DEFAULT_MAX_RETRIES,
            DEFAULT_VERBOSE,
        )

    @staticmethod
    def with_service(service: str, connector: RabbitMqConnector = None):
        connector = RabbitMqConnector() if not connector else connector
        return RabbitMqMessageConsumer(
            connector,
            DEFAULT_ORGANIZATION,
            service,
            DEFAULT_MAX_RETRIES,
            DEFAULT_VERBOSE,
        )

    @staticmethod
    def with_max_retries(max_retries: int, connector: RabbitMqConnector = None):
        connector = RabbitMqConnector() if not connector else connector
        return RabbitMqMessageConsumer(
            connector,
            DEFAULT_ORGANIZATION,
            DEFAULT_SERVICE,
            max_retries,
            DEFAULT_VERBOSE,
        )

    @staticmethod
    def without_retry(connector: RabbitMqConnector = None):
        connector = RabbitMqConnector() if not connector else connector
        return RabbitMqMessageConsumer(
            connector, DEFAULT_ORGANIZATION, DEFAULT_SERVICE, 0, DEFAULT_VERBOSE
        )

    @staticmethod
    def with_chaos(
        chaos: MessageChaos,
        max_retries: int,
        logger: ILogger = NotImplementedLogger(),
        connector: RabbitMqConnector = None,
    ):
        connector = RabbitMqConnector() if not connector else connector
        return RabbitMqMessageConsumer(
            connector,
            DEFAULT_ORGANIZATION,
            DEFAULT_SERVICE,
            max_retries,
            DEFAULT_VERBOSE,
            chaos,
            logger,
        )
