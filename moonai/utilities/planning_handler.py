from typing import Any, List, Optional
from pydantic import BaseModel, Field

from moonai.agent import Agent
from moonai.mission import Mission


class PlanPerMission(BaseModel):
    mission: str = Field(..., description="The mission for which the plan is created")
    plan: str = Field(
        ...,
        description="The step by step plan on how the agents can execute their missions using the available tools with mastery",
    )


class PlannerMissionPydanticOutput(BaseModel):
    list_of_plans_per_mission: List[PlanPerMission] = Field(
        ...,
        description="Step by step plan on how the agents can execute their missions using the available tools with mastery",
    )


class SquadPlanner:
    def __init__(self, missions: List[Mission], planning_agent_llm: Optional[Any] = None):
        self.missions = missions

        if planning_agent_llm is None:
            self.planning_agent_llm = "gpt-4o-mini"
        else:
            self.planning_agent_llm = planning_agent_llm

    def _handle_squad_planning(self) -> PlannerMissionPydanticOutput:
        """Handles the Squad planning by creating detailed step-by-step plans for each mission."""
        planning_agent = self._create_planning_agent()
        missions_summary = self._create_missions_summary()

        planner_mission = self._create_planner_mission(planning_agent, missions_summary)

        result = planner_mission.execute_sync()

        if isinstance(result.pydantic, PlannerMissionPydanticOutput):
            return result.pydantic

        raise ValueError("Failed to get the Planning output")

    def _create_planning_agent(self) -> Agent:
        """Creates the planning agent for the squad planning."""
        return Agent(
            role="Mission Execution Planner",
            goal=(
                "Your goal is to create an extremely detailed, step-by-step plan based on the missions and tools "
                "available to each agent so that they can perform the missions in an exemplary manner"
            ),
            backstory="Planner agent for squad planning",
            llm=self.planning_agent_llm,
        )

    def _create_planner_mission(self, planning_agent: Agent, missions_summary: str) -> Mission:
        """Creates the planner mission using the given agent and missions summary."""
        return Mission(
            description=(
                f"Based on these missions summary: {missions_summary} \n Create the most descriptive plan based on the missions "
                "descriptions, tools available, and agents' goals for them to execute their goals with perfection."
            ),
            expected_output="Step by step plan on how the agents can execute their missions using the available tools with mastery",
            agent=planning_agent,
            output_pydantic=PlannerMissionPydanticOutput,
        )

    def _create_missions_summary(self) -> str:
        """Creates a summary of all missions."""
        missions_summary = []
        for idx, mission in enumerate(self.missions):
            missions_summary.append(
                f"""
                Mission Number {idx + 1} - {mission.description}
                "mission_description": {mission.description}
                "mission_expected_output": {mission.expected_output}
                "agent": {mission.agent.role if mission.agent else "None"}
                "agent_goal": {mission.agent.goal if mission.agent else "None"}
                "mission_tools": {mission.tools}
                "agent_tools": {mission.agent.tools if mission.agent else "None"}
                """
            )
        return " ".join(missions_summary)
