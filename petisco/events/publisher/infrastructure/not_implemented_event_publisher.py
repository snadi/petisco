from typing import Dict

from petisco.events.event import Event
from petisco.events.publisher.domain.interface_event_publisher import IEventPublisher


class NotImplementedEventPublisher(IEventPublisher):
    def info(self) -> Dict:
        return {"name": self.__class__.__name__}

    def publish(self, event: Event):
        pass

    def stop(self):
        pass
