from moonai.tools.agent_tools.base_agent_tools import BaseAgentTool
from typing import Optional

from pydantic import BaseModel, Field


class DelegateWorkToolSchema(BaseModel):
    mission: str = Field(..., description="The mission to delegate")
    context: str = Field(..., description="The context for the mission")
    coworker: str = Field(
        ..., description="The role/name of the coworker to delegate to"
    )


class DelegateWorkTool(BaseAgentTool):
    """Tool for delegating work to coworkers"""

    name: str = "Delegate work to coworker"
    args_schema: type[BaseModel] = DelegateWorkToolSchema

    def _run(
        self,
        mission: str,
        context: str,
        coworker: Optional[str] = None,
        **kwargs,
    ) -> str:
        coworker = self._get_coworker(coworker, **kwargs)
        return self._execute(coworker, mission, context)
