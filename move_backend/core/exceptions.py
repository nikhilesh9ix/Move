from __future__ import annotations


class AgentError(Exception):
    """Raised when an individual agent fails to produce output."""

    def __init__(self, agent_name: str, reason: str) -> None:
        self.agent_name = agent_name
        self.reason = reason
        super().__init__(f"Agent '{agent_name}' failed: {reason}")


class PipelineError(Exception):
    """Raised when the orchestration pipeline cannot complete."""

    def __init__(self, stage: str, reason: str) -> None:
        self.stage = stage
        self.reason = reason
        super().__init__(f"Pipeline failed at stage '{stage}': {reason}")
