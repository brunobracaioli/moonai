<div align="center">

![Logo of Moon AI](https://raw.githubusercontent.com/brunobracaioli/moonai/main/moonai_logo.png)


# **Moon AI**

🤖 **Moon AI**: State-of-the-art platform designed to coordinate role-playing autonomous AI agents. Moon AI enables agents to collaborate effortlessly, combining their strengths to address intricate challenges with precision and efficiency.

<h3>

[Homepage](https://www.moonai.dev/) | [Documentation](https://docs.moonai.dev/) | [Chat with Docs](https://chatgpt.com/g/g-6748df2d1f508191873ca87cf954322a-moon-ai-assistant) | [Examples](https://github.com/brunobracaioli/moonai/moonai-examples) | [Discourse](https://community.moonai.dev)

</h3>

[![GitHub Repo stars](https://img.shields.io/github/stars/brunobracaioli/moonai)](https://github.com/brunobracaioli/moonai)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

</div>

## Table of contents

- [Why Moon AI?](#why-moonai)
- [Getting Started](#getting-started)
- [Key Features](#key-features)
- [Examples](#examples)
  - [Quick Tutorial](#quick-tutorial)
  - [Write Job Descriptions](#write-job-descriptions)
  - [Trip Planner](#trip-planner)
  - [Stock Analysis](#stock-analysis)
- [Connecting Your Squad to a Model](#connecting-your-squad-to-a-model)
- [How Moon AI Compares](#how-moonai-compares)
- [Contribution](#contribution)
- [Telemetry](#telemetry)
- [License](#license)

## Why Moon AI?

The power of AI collaboration has too much to offer.
Moon AI is designed to enable AI agents to assume roles, share goals, and operate in a cohesive unit - much like a well-oiled squad. Whether you're building a smart assistant platform, an automated customer service ensemble, or a multi-agent research team, Moon AI provides the backbone for sophisticated multi-agent interactions.

## Getting Started

To get started with moonai, follow these simple steps:

### 1. Installation

Ensure you have Python >=3.10 <=3.13 installed on your system. Moon AI uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, install moonai:

```shell
pip install moonai
```

If you want to install the 'moonai' package along with its optional features that include additional tools for agents, you can do so by using the following command:

```shell
pip install 'moonai.moonai_tools'
```
The command above installs the basic package and also adds extra components which require more dependencies to function.

### 2. Setting Up Your Squad with the YAML Configuration

To create a new Moon AI project, run the following CLI (Command Line Interface) command:

```shell
moonai create squad <project_name>
```

This command creates a new project folder with the following structure:

```
my_project/
├── .gitignore
├── pyproject.toml
├── README.md
├── .env
└── src/
    └── my_project/
        ├── __init__.py
        ├── main.py
        ├── squad.py
        ├── tools/
        │   ├── custom_tool.py
        │   └── __init__.py
        └── config/
            ├── agents.yaml
            └── missions.yaml
```

You can now start developing your squad by editing the files in the `src/my_project` folder. The `main.py` file is the entry point of the project, the `squad.py` file is where you define your squad, the `agents.yaml` file is where you define your agents, and the `missions.yaml` file is where you define your missions.

#### To customize your project, you can:

- Modify `src/my_project/config/agents.yaml` to define your agents.
- Modify `src/my_project/config/missions.yaml` to define your missions.
- Modify `src/my_project/squad.py` to add your own logic, tools, and specific arguments.
- Modify `src/my_project/main.py` to add custom inputs for your agents and missions.
- Add your environment variables into the `.env` file.

#### Example of a simple squad with a sequential process:

Instantiate your squad:

```shell
moonai create squad latest-ai-development
```

Modify the files as needed to fit your use case:

**agents.yaml**

```yaml
# src/my_project/config/agents.yaml
researcher:
  role: >
    {topic} Senior Data Researcher
  goal: >
    Uncover cutting-edge developments in {topic}
  backstory: >
    You're a seasoned researcher with a knack for uncovering the latest
    developments in {topic}. Known for your ability to find the most relevant
    information and present it in a clear and concise manner.
      
reporting_analyst:
  role: >
    {topic} Reporting Analyst
  goal: >
    Create detailed reports based on {topic} data analysis and research findings
  backstory: >
    You're a meticulous analyst with a keen eye for detail. You're known for
    your ability to turn complex data into clear and concise reports, making
    it easy for others to understand and act on the information you provide.
```

**missions.yaml**

```yaml
# src/my_project/config/missions.yaml
research_mission:
  description: >
    Conduct a thorough research about {topic}
    Make sure you find any interesting and relevant information given
    the current year is 2024.
  expected_output: >
    A list with 10 bullet points of the most relevant information about {topic}
  agent: researcher

reporting_mission:
  description: >
    Review the context you got and expand each topic into a full section for a report.
    Make sure the report is detailed and contains any and all relevant information.
  expected_output: >
    A fully fledge reports with the mains topics, each with a full section of information.
    Formatted as markdown without '```'
  agent: reporting_analyst
  output_file: report.md
```

**squad.py**

```python
# src/my_project/squad.py
from moonai import Agent, Squad, Process, Mission
from moonai.project import SquadBase, agent, squad, mission
from moonai.moonai_tools import SerperDevTool

@SquadBase
class LatestAiDevelopmentSquad():
	"""LatestAiDevelopment squad"""

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True,
			tools=[SerperDevTool()]
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
		"""Creates the LatestAiDevelopment squad"""
		return Squad(
			agents=self.agents, # Automatically created by the @agent decorator
			missions=self.missions, # Automatically created by the @mission decorator
			process=Process.sequential,
			verbose=True,
		) 
```

**main.py**

```python
#!/usr/bin/env python
# src/my_project/main.py
import sys
from latest_ai_development.squad import LatestAiDevelopmentSquad

def run():
    """
    Run the squad.
    """
    inputs = {
        'topic': 'AI Agents'
    }
    LatestAiDevelopmentSquad().squad().kickoff(inputs=inputs)
```

### 3. Running Your Squad

Before running your squad, make sure you have the following keys set as environment variables in your `.env` file:

- An [OpenAI API key](https://platform.openai.com/account/api-keys) (or other LLM API key): `OPENAI_API_KEY=sk-...`
- A [Serper.dev](https://serper.dev/) API key: `SERPER_API_KEY=YOUR_KEY_HERE`

Lock the dependencies and install them by using the CLI command but first, navigate to your project directory:

```shell
cd my_project
moonai install (Optional)
```

To run your squad, execute the following command in the root of your project:

```bash
moonai run
```

or

```bash
python src/my_project/main.py
```

If an error happens due to the usage of poetry, please run the following command to update your Moon AI package:

```bash
moonai update
```

You should see the output in the console and the `report.md` file should be created in the root of your project with the full final report.

In addition to the sequential process, you can use the hierarchical process, which automatically assigns a manager to the defined squad to properly coordinate the planning and execution of missions through delegation and validation of results. [See more about the processes here](https://docs.moonai.dev/core-concepts/Processes/).

## Key Features

- **Role-Based Agent Design**: Customize agents with specific roles, goals, and tools.
- **Autonomous Inter-Agent Delegation**: Agents can autonomously delegate missions and inquire amongst themselves, enhancing problem-solving efficiency.
- **Flexible Mission Management**: Define missions with customizable tools and assign them to agents dynamically.
- **Processes Driven**: Currently only supports `sequential` mission execution and `hierarchical` processes, but more complex processes like consensual and autonomous are being worked on.
- **Save output as file**: Save the output of individual missions as a file, so you can use it later.
- **Parse output as Pydantic or Json**: Parse the output of individual missions as a Pydantic model or as a Json if you want to.
- **Works with Open Source Models**: Run your squad using Open AI or open source models refer to the [Connect Moon AI to LLMs](https://docs.moonai.dev/how-to/LLM-Connections/) page for details on configuring your agents' connections to models, even ones running locally!

![Moon AI Mind Map](./docs/moonai-mindmap.png "Moon AI Mind Map")

## Examples

You can test different real life examples of AI squads in the [moonai-examples repo](https://github.com/brunobracaioli/moonai/moonai-examples?tab=readme-ov-file):

- [Landing Page Generator](https://github.com/brunobracaioli/moonai/moonai-examples/tree/main/landing_page_generator)
- [Having Human input on the execution](https://docs.moonai.dev/how-to/Human-Input-on-Execution)
- [Trip Planner](https://github.com/brunobracaioli/moonai/moonai-examples/tree/main/trip_planner)
- [Stock Analysis](https://github.com/brunobracaioli/moonai/moonai-examples/tree/main/stock_analysis)

### Quick Tutorial

[![Moon AI Tutorial](https://img.youtube.com/vi/tnejrr-0a94/maxresdefault.jpg)](https://www.youtube.com/watch?v=tnejrr-0a94 "Moon AI Tutorial")

### Write Job Descriptions

[Check out code for this example](https://github.com/brunobracaioli/moonai/moonai-examples/tree/main/job-posting) or watch a video below:

[![Jobs postings](https://img.youtube.com/vi/u98wEMz-9to/maxresdefault.jpg)](https://www.youtube.com/watch?v=u98wEMz-9to "Jobs postings")

### Trip Planner

[Check out code for this example](https://github.com/brunobracaioli/moonai/moonai-examples/tree/main/trip_planner) or watch a video below:

[![Trip Planner](https://img.youtube.com/vi/xis7rWp-hjs/maxresdefault.jpg)](https://www.youtube.com/watch?v=xis7rWp-hjs "Trip Planner")

### Stock Analysis

[Check out code for this example](https://github.com/brunobracaioli/moonai/moonai-examples/tree/main/stock_analysis) or watch a video below:

[![Stock Analysis](https://img.youtube.com/vi/e0Uj4yWdaAg/maxresdefault.jpg)](https://www.youtube.com/watch?v=e0Uj4yWdaAg "Stock Analysis")

## Connecting Your Squad to a Model

Moon AI supports using various LLMs through a variety of connection options. By default your agents will use the OpenAI API when querying the model. However, there are several other ways to allow your agents to connect to models. For example, you can configure your agents to use a local model via the Ollama tool.

Please refer to the [Connect Moon AI to LLMs](https://docs.moonai.dev/how-to/LLM-Connections/) page for details on configuring you agents' connections to models.

## How Moon AI Compares

**moonai's Advantage**: Moon AI is built with production in mind. It offers the flexibility of Autogen's conversational agents and the structured process approach of ChatDev, but without the rigidity. moonai's processes are designed to be dynamic and adaptable, fitting seamlessly into both development and production workflows.

- **Autogen**: While Autogen does good in creating conversational agents capable of working together, it lacks an inherent concept of process. In Autogen, orchestrating agents' interactions requires additional programming, which can become complex and cumbersome as the scale of missions grows.

- **ChatDev**: ChatDev introduced the idea of processes into the realm of AI agents, but its implementation is quite rigid. Customizations in ChatDev are limited and not geared towards production environments, which can hinder scalability and flexibility in real-world applications.

## Contribution

Moon AI is open-source and we welcome contributions. If you're looking to contribute, please:

- Fork the repository.
- Create a new branch for your feature.
- Add your feature or improvement.
- Send a pull request.
- We appreciate your input!

### Installing Dependencies

```bash
uv lock
uv sync
```

### Virtual Env

```bash
uv venv
```

### Pre-commit hooks

```bash
pre-commit install
```

### Running Tests

```bash
uv run pytest .
```

### Running static type checks

```bash
uvx mypy
```

### Packaging

```bash
uv build
```

### Installing Locally

```bash
pip install dist/*.tar.gz
```

## Telemetry

Moon AI uses anonymous telemetry to collect usage data with the main purpose of helping us improve the library by focusing our efforts on the most used features, integrations and tools.

It's pivotal to understand that **NO data is collected** concerning prompts, mission descriptions, agents' backstories or goals, usage of tools, API calls, responses, any data processed by the agents, or secrets and environment variables, with the exception of the conditions mentioned. When the `share_squad` feature is enabled, detailed data including mission descriptions, agents' backstories or goals, and other specific attributes are collected to provide deeper insights while respecting user privacy. We don't offer a way to disable it now, but we will in the future.

Data collected includes:

- Version of moonai
  - So we can understand how many users are using the latest version
- Version of Python
  - So we can decide on what versions to better support
- General OS (e.g. number of CPUs, macOS/Windows/Linux)
  - So we know what OS we should focus on and if we could build specific OS related features
- Number of agents and missions in a squad
  - So we make sure we are testing internally with similar use cases and educate people on the best practices
- Squad Process being used
  - Understand where we should focus our efforts
- If Agents are using memory or allowing delegation
  - Understand if we improved the features or maybe even drop them
- If Missions are being executed in parallel or sequentially
  - Understand if we should focus more on parallel execution
- Language model being used
  - Improved support on most used languages
- Roles of agents in a squad
  - Understand high level use cases so we can build better tools, integrations and examples about it
- Tools names available
  - Understand out of the publicly available tools, which ones are being used the most so we can improve them

Users can opt-in to Further Telemetry, sharing the complete telemetry data by setting the `share_squad` attribute to `True` on their Squads. Enabling `share_squad` results in the collection of detailed squad and mission execution data, including `goal`, `backstory`, `context`, and `output` of missions. This enables a deeper insight into usage patterns while respecting the user's choice to share.

## License

Moon AI is released under the [MIT License](https://github.com/brunobracaioli/moonai/blob/main/LICENSE).

## Frequently Asked Questions (FAQ)

### Q: What is Moon AI?
A: Moon AI aiis a cutting-edge framework for orchestrating role-playing, autonomous AI agents. It enables agents to work together seamlessly, tackling complex missions through collaborative intelligence.

### Q: How do I install Moon AI?
A: You can install Moon AI aiusing pip:
```shell
pip install moonai
```
For additional tools, use:
```shell
pip install 'moonai.moonai_tools'
```

### Q: Can I use Moon AI with local models?
A: Yes, Moon AI supports various LLMs, including local models. You can configure your agents to use local models via tools like Ollama & LM Studio. Check the [LLM Connections documentation](https://docs.moonai.dev/how-to/LLM-Connections/) for more details.

### Q: What are the key features of Moon AI?
A: Key features include role-based agent design, autonomous inter-agent delegation, flexible mission management, process-driven execution, output saving as files, and compatibility with both open-source and proprietary models.

### Q: How does Moon AI compare to other AI orchestration tools?
A: Moon AI is designed with production in mind, offering flexibility similar to Autogen's conversational agents and structured processes like ChatDev, but with more adaptability for real-world applications.

### Q: Is Moon AI open-source?
A: Yes, Moon AI is open-source and welcomes contributions from the community.

### Q: Does Moon AI collect any data?
A: Moon AI uses anonymous telemetry to collect usage data for improvement purposes. No sensitive data (like prompts, mission descriptions, or API calls) is collected. Users can opt-in to share more detailed data by setting `share_squad=True` on their Squads.

### Q: Where can I find examples of Moon AI in action?
A: You can find various real-life examples in the [moonai-examples repository](https://github.com/brunobracaioli/moonai/moonai-examples), including trip planners, stock analysis tools, and more.

### Q: How can I contribute to Moon AI?
A: Contributions are welcome! You can fork the repository, create a new branch for your feature, add your improvement, and send a pull request. Check the Contribution section in the README for more details.

# Moon AI
Moon AI