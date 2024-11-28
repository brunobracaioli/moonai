from moonai import Agent, Squad, Process, Mission
from moonai.project import SquadBase, agent, squad, mission

# Uncomment the following line to use an example of a custom tool
# from {{folder_name}}.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from moonai.moonai_tools import SerperDevTool

@SquadBase
class WriteLinkedInSquad():
	"""Research Squad"""
	agents_config = 'config/agents.yaml'
	missions_config = 'config/missions.yaml'

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True
		)

	@mission
	def research_mission(self) -> Mission:
		return Mission(
			config=self.missions_config['research_mission'],
		)

	@mission
	def reporting_mission(self) -> Mission:
		return Mission(
			config=self.missions_config['reporting_mission'],
			output_file='report.md'
		)

	@squad
	def squad(self) -> Squad:
		"""Creates the {{squad_name}} squad"""
		return Squad(
			agents=self.agents, # Automatically created by the @agent decorator
			missions=self.missions, # Automatically created by the @mission decorator
			process=Process.sequential,
			verbose=True,
		)