from abc import ABC, abstractmethod
from app.state.session_state import SessionState
from typing import Any


class BaseAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    @abstractmethod
    async def run(self, state: SessionState) -> dict[str, Any]:
        ...

    def narrate(self, message: str) -> dict[str, list[str]]:
        return {"narration": [message]}

    def error(self, message: str) -> dict[str, list[str]]:
        return {"errors": [f"[{self.name}] {message}"]}