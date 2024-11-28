from moonai import Agent, Squad, Process, Mission
from moonai.project import SquadBase, agent, squad, mission, before_kickoff, after_kickoff

# Uncomment the following line to use an example of a custom tool
# from {{folder_name}}.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from moonai.moonai_tools import SerperDevTool

@SquadBase
class {{squad_name}}():
	"""{{squad_name}} squad"""

	agents_config = 'config/agents.yaml'
	missions_config = 'config/missions.yaml'

	@before_kickoff # Optional hook to be executed before the squad starts
	def pull_data_example(self, inputs):
		# Example of pulling data from an external API, dynamically changing the inputs
		inputs['extra_data'] = "This is extra data"
		return inputs

	@after_kickoff # Optional hook to be executed after the squad has finished
	def log_results(self, output):
		# Example of logging results, dynamically changing the output
		print(f"Results: {output}")
		return output

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			# tools=[MyCustomTool()], # Example of custom tool, loaded on the beginning of file
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
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.moonai.dev/how-to/Hierarchical/
		)
