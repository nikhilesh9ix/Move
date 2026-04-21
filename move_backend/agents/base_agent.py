from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """
    Abstract base for all pipeline agents.

    Each concrete agent declares its input/output types via the Generic params
    and implements a single async `run()` entry point. This keeps agent
    contracts explicit and enables uniform orchestration.
    """

    #: Identifies the agent in logs and error messages.
    name: str = "base"

    @abstractmethod
    async def run(self, input_data: InputT) -> OutputT:
        """Execute the agent and return a typed result."""
        ...
