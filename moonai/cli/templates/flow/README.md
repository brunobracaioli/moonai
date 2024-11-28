# {{squad_name}} Squad

Welcome to the {{squad_name}} Squad project, powered by [moonai](https://moonai.dev). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by moonai. Our goal is to enable your agents to collaborate effectively on complex missions, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <=3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
moonai install
```

### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/{{folder_name}}/config/agents.yaml` to define your agents
- Modify `src/{{folder_name}}/config/missions.yaml` to define your missions
- Modify `src/{{folder_name}}/squad.py` to add your own logic, tools and specific args
- Modify `src/{{folder_name}}/main.py` to add custom inputs for your agents and missions

## Running the Project

To kickstart your squad of AI agents and begin mission execution, run this from the root folder of your project:

```bash
moonai run
```

This command initializes the {{name}} Squad, assembling the agents and assigning them missions as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Squad

The {{name}} Squad is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of missions, defined in `config/missions.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your squad.

## Support

For support, questions, or feedback regarding the {{squad_name}} Squad or moonai.

- Visit our [documentation](https://docs.moonai.dev)
- Reach out to us through our [GitHub repository](https://github.com/brunobracaioli/moonai)

Let's create wonders together with the power and simplicity of moonai.
