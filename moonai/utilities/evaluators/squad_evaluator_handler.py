from collections import defaultdict

from moonai.agent import Agent
from moonai.mission import Mission
from moonai.missions.mission_output import MissionOutput
from moonai.telemetry import Telemetry
from pydantic import BaseModel, Field
from rich.box import HEAVY_EDGE
from rich.console import Console
from rich.table import Table


class MissionEvaluationPydanticOutput(BaseModel):
    quality: float = Field(
        description="A score from 1 to 10 evaluating on completion, quality, and overall performance from the mission_description and mission_expected_output to the actual Mission Output."
    )


class SquadEvaluator:
    """
    A class to evaluate the performance of the agents in the squad based on the missions they have performed.

    Attributes:
        squad (Squad): The squad of agents to evaluate.
        openai_model_name (str): The model to use for evaluating the performance of the agents (for now ONLY OpenAI accepted).
        missions_scores (defaultdict): A dictionary to store the scores of the agents for each mission.
        iteration (int): The current iteration of the evaluation.
    """

    missions_scores: defaultdict = defaultdict(list)
    run_execution_times: defaultdict = defaultdict(list)
    iteration: int = 0

    def __init__(self, squad, openai_model_name: str):
        self.squad = squad
        self.openai_model_name = openai_model_name
        self._telemetry = Telemetry()
        self._setup_for_evaluating()

    def _setup_for_evaluating(self) -> None:
        """Sets up the squad for evaluating."""
        for mission in self.squad.missions:
            mission.callback = self.evaluate

    def _evaluator_agent(self):
        return Agent(
            role="Mission Execution Evaluator",
            goal=(
                "Your goal is to evaluate the performance of the agents in the squad based on the missions they have performed using score from 1 to 10 evaluating on completion, quality, and overall performance."
            ),
            backstory="Evaluator agent for squad evaluation with precise capabilities to evaluate the performance of the agents in the squad based on the missions they have performed",
            verbose=False,
            llm=self.openai_model_name,
        )

    def _evaluation_mission(
        self, evaluator_agent: Agent, mission_to_evaluate: Mission, mission_output: str
    ) -> Mission:
        return Mission(
            description=(
                "Based on the mission description and the expected output, compare and evaluate the performance of the agents in the squad based on the Mission Output they have performed using score from 1 to 10 evaluating on completion, quality, and overall performance."
                f"mission_description: {mission_to_evaluate.description} "
                f"mission_expected_output: {mission_to_evaluate.expected_output} "
                f"agent: {mission_to_evaluate.agent.role if mission_to_evaluate.agent else None} "
                f"agent_goal: {mission_to_evaluate.agent.goal if mission_to_evaluate.agent else None} "
                f"Mission Output: {mission_output}"
            ),
            expected_output="Evaluation Score from 1 to 10 based on the performance of the agents on the missions",
            agent=evaluator_agent,
            output_pydantic=MissionEvaluationPydanticOutput,
        )

    def set_iteration(self, iteration: int) -> None:
        self.iteration = iteration

    def print_squad_evaluation_result(self) -> None:
        """
        Prints the evaluation result of the squad in a table.
        A Squad with 2 missions using the command moonai test -n 3
        will output the following table:

                        missions Scores
                    (1-10 Higher is better)
        ┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ missions/Squad/Agents  ┃ Run 1 ┃ Run 2 ┃ Run 3 ┃ Avg. Total ┃ Agents                       ┃
        ┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
        │ Mission 1             │ 9.0   │ 10.0  │ 9.0   │ 9.3        │ - AI LLMs Senior Researcher  │
        │                    │       │       │       │            │ - AI LLMs Reporting Analyst  │
        │                    │       │       │       │            │                              │
        │ Mission 2             │ 9.0   │ 9.0   │ 9.0   │ 9.0        │ - AI LLMs Senior Researcher  │
        │                    │       │       │       │            │ - AI LLMs Reporting Analyst  │
        │                    │       │       │       │            │                              │
        │ Squad               │ 9.0   │ 9.5   │ 9.0   │ 9.2        │                              │
        │ Execution Time (s) │ 42    │ 79    │ 52    │ 57         │                              │
        └────────────────────┴───────┴───────┴───────┴────────────┴──────────────────────────────┘
        """
        mission_averages = [
            sum(scores) / len(scores) for scores in zip(*self.missions_scores.values())
        ]
        squad_average = sum(mission_averages) / len(mission_averages)

        table = Table(title="missions Scores \n (1-10 Higher is better)", box=HEAVY_EDGE)

        table.add_column("missions/Squad/Agents", style="cyan")
        for run in range(1, len(self.missions_scores) + 1):
            table.add_column(f"Run {run}", justify="center")
        table.add_column("Avg. Total", justify="center")
        table.add_column("Agents", style="green")

        for mission_index, mission in enumerate(self.squad.missions):
            mission_scores = [
                self.missions_scores[run][mission_index]
                for run in range(1, len(self.missions_scores) + 1)
            ]
            avg_score = mission_averages[mission_index]
            agents = list(mission.processed_by_agents)

            # Add the mission row with the first agent
            table.add_row(
                f"Mission {mission_index + 1}",
                *[f"{score:.1f}" for score in mission_scores],
                f"{avg_score:.1f}",
                f"- {agents[0]}" if agents else "",
            )

            # Add rows for additional agents
            for agent in agents[1:]:
                table.add_row("", "", "", "", "", f"- {agent}")

            # Add a blank separator row if it's not the last mission
            if mission_index < len(self.squad.missions) - 1:
                table.add_row("", "", "", "", "", "")

        # Add Squad and Execution Time rows
        squad_scores = [
            sum(self.missions_scores[run]) / len(self.missions_scores[run])
            for run in range(1, len(self.missions_scores) + 1)
        ]
        table.add_row(
            "Squad",
            *[f"{score:.2f}" for score in squad_scores],
            f"{squad_average:.1f}",
            "",
        )

        run_exec_times = [
            int(sum(missions_exec_times))
            for _, missions_exec_times in self.run_execution_times.items()
        ]
        execution_time_avg = int(sum(run_exec_times) / len(run_exec_times))
        table.add_row(
            "Execution Time (s)", *map(str, run_exec_times), f"{execution_time_avg}", ""
        )

        console = Console()
        console.print(table)

    def evaluate(self, mission_output: MissionOutput):
        """Evaluates the performance of the agents in the squad based on the missions they have performed."""
        current_mission = None
        for mission in self.squad.missions:
            if mission.description == mission_output.description:
                current_mission = mission
                break

        if not current_mission or not mission_output:
            raise ValueError(
                "Mission to evaluate and mission output are required for evaluation"
            )

        evaluator_agent = self._evaluator_agent()
        evaluation_mission = self._evaluation_mission(
            evaluator_agent, current_mission, mission_output.raw
        )

        evaluation_result = evaluation_mission.execute_sync()

        if isinstance(evaluation_result.pydantic, MissionEvaluationPydanticOutput):
            self._test_result_span = self._telemetry.individual_test_result_span(
                self.squad,
                evaluation_result.pydantic.quality,
                current_mission._execution_time,
                self.openai_model_name,
            )
            self.missions_scores[self.iteration].append(evaluation_result.pydantic.quality)
            self.run_execution_times[self.iteration].append(
                current_mission._execution_time
            )
        else:
            raise ValueError("Evaluation result is not in the expected format")
