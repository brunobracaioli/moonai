from moonai.moonai_tools import MetaUpdateCampaignBudgetTool, MetaMetricsTool, MetaUpdateCampaignStatusTool, FileReadTool, FileWriterTool
from moonai import Agent, Mission, Squad
from dotenv import load_dotenv

load_dotenv()

# TOOLS
meta_budget_tool = MetaUpdateCampaignBudgetTool()
meta_status_tool = MetaUpdateCampaignStatusTool()
meta_get_data_tool = MetaMetricsTool()
file_read_tool = FileReadTool()
file_write_tool = FileWriterTool()


# FILE PATHS
budget_file_path = "campaign.txt" 
status_file_path = "status_updates.txt"
data_ads = "data_ads.txt"
meta_analysis = "meta_analysis.txt"


# AGENTS

get_data_agent = Agent(
    role="Data Getter",
    goal=f"Use the {meta_get_data_tool} tool to obtain data from active meta campaigns and save the content to the file {data_ads}",
    backstory="Expert in activating tools and saving files",
    llm="gpt-4o-mini",
    verbose=True,
    tools=[meta_get_data_tool]
)

analytics_agent = Agent(
    role="Meta Ads Analyst",
    goal=f"Analyze Meta Ads metrics from the last 7 days and provide key insights. Then save the insights in the {meta_analysis} file",
    backstory="Specialist in analyzing Meta Ads performance",
    llm="gpt-4o-mini",
    verbose=True,
    tools=[file_read_tool, file_write_tool]
)

updater_budget_agent = Agent(
    role="Meta Ads Budget Updater",
    goal=f"activate the {meta_budget_tool} tool using the {budget_file_path} file to get the campaign id and budget.",
    backstory="expert in using tools to update Meta Ads budgets",
    llm="gpt-4o-mini",
    verbose=True,
    tools=[meta_budget_tool]
)

updater_status_agent = Agent(
    role="Meta Ads Status Updater",
    goal=f"activate the {meta_status_tool} tool using the {status_file_path} file to get the campaign id and status.",
    backstory="expert in using tools to update Meta Ads budgets",
    llm="gpt-4o-mini",
    verbose=True,
    tools=[meta_status_tool]
)

# MISSIONS
get_data_ads = Mission(
    description=f"Use the {meta_get_data_tool} tool to obtain data from active meta campaigns and save the content to the file {data_ads}",
    expected_output=f"Data saved in file {data_ads}",
    agent=get_data_agent,
    tools=[meta_get_data_tool],
    output_file=f"{data_ads}"
)

analyze_ads = Mission(
    description=f"Analyze Meta Ads metrics from the last 7 days and provide key insights. Then save the insights in the {meta_analysis} file",
    expected_output="",
    agent=analytics_agent,
    tools=[file_read_tool, file_write_tool],
    output_file=f"{meta_analysis}"
)

update_budget = Mission(
    description=f"activate the {meta_budget_tool} tool using the {budget_file_path} file to get the campaign id and budget.",
    expected_output="Confirmation that the campaign had its budget changed",
    agent=updater_budget_agent,
    tools=[meta_budget_tool]
)

update_status = Mission(
    description=f"activate the {meta_status_tool} tool using the {status_file_path} file to get the campaign id and status.",
    expected_output="Confirmation that the campaign had its status changed",
    agent=updater_status_agent,
    tools=[meta_status_tool]
)


# SQUAD
squad = Squad(
    agents=[get_data_agent, analytics_agent, updater_status_agent, updater_budget_agent],
    missions=[get_data_ads, analyze_ads, update_status, update_budget],
    verbose=True
)

squad.kickoff()

# python test_MetaUpdateCampaignBudgetTool.py