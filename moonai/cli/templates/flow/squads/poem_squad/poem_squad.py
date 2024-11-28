from moonai import Agent, Squad, Process, Mission
from moonai.project import SquadBase, agent, squad, mission

@SquadBase
class PoemSquad():
	"""Poem Squad"""

	agents_config = 'config/agents.yaml'
	missions_config = 'config/missions.yaml'

	@agent
	def poem_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['poem_writer'],
		)

	@mission
	def write_poem(self) -> Mission:
		return Mission(
			config=self.missions_config['write_poem'],
		)

	@squad
	def squad(self) -> Squad:
		"""Creates the Research Squad"""
		return Squad(
			agents=self.agents, # Automatically created by the @agent decorator
			missions=self.missions, # Automatically created by the @mission decorator
			process=Process.sequential,
			verbose=True,
		)
