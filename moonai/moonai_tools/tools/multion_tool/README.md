# MultiOnTool Documentation

## Description
The MultiOnTool, integrated within the moonai.moonai_tools package, empowers moonai agents with the capability to navigate and interact with the web through natural language instructions. Leveraging the Multion API, this tool facilitates seamless web browsing, making it an essential asset for projects requiring dynamic web data interaction.

## Installation
Ensure the `moonai.moonai_tools` package is installed in your environment to use the MultiOnTool. If it's not already installed, you can add it using the command below:
```shell
pip install 'moonai.moonai_tools'
```

## Example
The following example demonstrates how to initialize the tool and execute a search with a given query:

```python
from moonai import Agent, Mission, Squad
from moonai.moonai_tools import MultiOnTool

# Initialize the tool from a MultiOn Tool
multion_tool = MultiOnTool(api_key= "YOUR_MULTION_API_KEY", local=False)

Browser = Agent(
    role="Browser Agent",
    goal="control web browsers using natural language ",
    backstory="An expert browsing agent.",
    tools=[multion_remote_tool],
    verbose=True,
)

# example mission to search and summarize news
browse = Mission(
    description="Summarize the top 3 trending AI News headlines",
    expected_output="A summary of the top 3 trending AI News headlines",
    agent=Browser,
)

squad = Squad(agents=[Browser], missions=[browse])

squad.kickoff()
```

## Arguments

- `api_key`: Specifies Browserbase API key. Defaults is the `BROWSERBASE_API_KEY` environment variable.
- `local`: Use the local flag set as "true" to run the agent locally on your browser. Make sure the multion browser extension is installed and API Enabled is checked.
- `max_steps`: Optional. Set the max_steps the multion agent can take for a command

## Steps to Get Started
To effectively use the `MultiOnTool`, follow these steps:

1. **Install moonai**: Confirm that the `moonai.moonai_tools` package is installed in your Python environment.
2. **Install and use MultiOn**: Follow MultiOn documentation for installing the MultiOn Browser Extension (https://docs.multion.ai/learn/browser-extension).
3. **Enable API Usage**: Click on the MultiOn extension in the extensions folder of your browser (not the hovering MultiOn icon on the web page) to open the extension configurations. Click the API Enabled toggle to enable the API                             

