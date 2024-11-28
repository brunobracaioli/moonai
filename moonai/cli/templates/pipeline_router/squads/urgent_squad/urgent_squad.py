from moonai import Agent, Squad, Process, Mission
from moonai.project import SquadBase, agent, squad, mission

# Uncomment the following line to use an example of a custom tool
# from demo_pipeline.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from moonai.moonai_tools import SerperDevTool


@SquadBase
class UrgentSquad:
    """Urgent Email Squad"""

    agents_config = "config/agents.yaml"
    missions_config = "config/missions.yaml"

    @agent
    def urgent_handler(self) -> Agent:
        return Agent(config=self.agents_config["urgent_handler"], verbose=True)

    @mission
    def urgent_mission(self) -> Mission:
        return Mission(
            config=self.missions_config["urgent_mission"],
        )

    @squad
    def squad(self) -> Squad:
        """Creates the Urgent Email Squad"""
        return Squad(
            agents=self.agents,  # Automatically created by the @agent decorator
            missions=self.missions,  # Automatically created by the @mission decorator
            process=Process.sequential,
            verbose=True,
        )
