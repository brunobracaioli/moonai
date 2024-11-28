from typing import Any, Callable

from pydantic import Field

from moonai.mission import Mission
from moonai.missions.output_format import OutputFormat
from moonai.missions.mission_output import MissionOutput


class ConditionalMission(Mission):
    """
    A mission that can be conditionally executed based on the output of another mission.
    Note: This cannot be the only mission you have in your squad and cannot be the first since its needs context from the previous mission.
    """

    condition: Callable[[MissionOutput], bool] = Field(
        default=None,
        description="Maximum number of retries for an agent to execute a mission when an error occurs.",
    )

    def __init__(
        self,
        condition: Callable[[Any], bool],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.condition = condition

    def should_execute(self, context: MissionOutput) -> bool:
        """
        Determines whether the conditional mission should be executed based on the provided context.

        Args:
            context (Any): The context or output from the previous mission that will be evaluated by the condition.

        Returns:
            bool: True if the mission should be executed, False otherwise.
        """
        return self.condition(context)

    def get_skipped_mission_output(self):
        return MissionOutput(
            description=self.description,
            raw="",
            agent=self.agent.role if self.agent else "",
            output_format=OutputFormat.RAW,
        )
