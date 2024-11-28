import time
from typing import TYPE_CHECKING, Optional

from moonai.memory.entity.entity_memory_item import EntityMemoryItem
from moonai.memory.long_term.long_term_memory_item import LongTermMemoryItem
from moonai.utilities.converter import ConverterError
from moonai.utilities.evaluators.mission_evaluator import MissionEvaluator
from moonai.utilities import I18N
from moonai.utilities.printer import Printer


if TYPE_CHECKING:
    from moonai.squad import Squad
    from moonai.mission import Mission
    from moonai.agents.agent_builder.base_agent import BaseAgent


class SquadAgentExecutorMixin:
    squad: Optional["Squad"]
    agent: Optional["BaseAgent"]
    mission: Optional["Mission"]
    iterations: int
    have_forced_answer: bool
    max_iter: int
    _i18n: I18N
    _printer: Printer = Printer()

    def _should_force_answer(self) -> bool:
        """Determine if a forced answer is required based on iteration count."""
        return (self.iterations >= self.max_iter) and not self.have_forced_answer

    def _create_short_term_memory(self, output) -> None:
        """Create and save a short-term memory item if conditions are met."""
        if (
            self.squad
            and self.agent
            and self.mission
            and "Action: Delegate work to coworker" not in output.text
        ):
            try:
                if (
                    hasattr(self.squad, "_short_term_memory")
                    and self.squad._short_term_memory
                ):
                    self.squad._short_term_memory.save(
                        value=output.text,
                        metadata={
                            "observation": self.mission.description,
                        },
                        agent=self.agent.role,
                    )
            except Exception as e:
                print(f"Failed to add to short term memory: {e}")
                pass

    def _create_long_term_memory(self, output) -> None:
        """Create and save long-term and entity memory items based on evaluation."""
        if (
            self.squad
            and self.squad.memory
            and self.squad._long_term_memory
            and self.squad._entity_memory
            and self.mission
            and self.agent
        ):
            try:
                ltm_agent = MissionEvaluator(self.agent)
                evaluation = ltm_agent.evaluate(self.mission, output.text)

                if isinstance(evaluation, ConverterError):
                    return

                long_term_memory = LongTermMemoryItem(
                    mission=self.mission.description,
                    agent=self.agent.role,
                    quality=evaluation.quality,
                    datetime=str(time.time()),
                    expected_output=self.mission.expected_output,
                    metadata={
                        "suggestions": evaluation.suggestions,
                        "quality": evaluation.quality,
                    },
                )
                self.squad._long_term_memory.save(long_term_memory)

                for entity in evaluation.entities:
                    entity_memory = EntityMemoryItem(
                        name=entity.name,
                        type=entity.type,
                        description=entity.description,
                        relationships="\n".join(
                            [f"- {r}" for r in entity.relationships]
                        ),
                    )
                    self.squad._entity_memory.save(entity_memory)
            except AttributeError as e:
                print(f"Missing attributes for long term memory: {e}")
                pass
            except Exception as e:
                print(f"Failed to add to long term memory: {e}")
                pass

    def _ask_human_input(self, final_answer: dict) -> str:
        """Prompt human input for final decision making."""
        self._printer.print(
            content=f"\033[1m\033[95m ## Final Result:\033[00m \033[92m{final_answer}\033[00m"
        )

        self._printer.print(
            content="\n\n=====\n## Please provide feedback on the Final Result and the Agent's actions:",
            color="bold_yellow",
        )
        return input()
