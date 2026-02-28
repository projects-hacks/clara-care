"""Queue for injecting context into the LLM during silence windows."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class InjectionQueue:
    """
    Queues InjectAgentMessage payloads for delivery during Clara's silence.
    Only sends the LATEST message if multiple are queued.
    """

    def __init__(self):
        self._queue: list[str] = []

    def enqueue(self, content: str):
        """Add a message to the queue."""
        self._queue.append(content)

    def drain(self) -> Optional[str]:
        """
        Return the latest queued message and clear the queue.
        Returns None if queue is empty.
        """
        if not self._queue:
            return None
        latest = self._queue[-1]
        self._queue.clear()
        return latest

    def clear(self):
        """Clear all queued messages."""
        self._queue.clear()

    @property
    def is_empty(self) -> bool:
        return len(self._queue) == 0
