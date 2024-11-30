from moonai.moonai_tools import MetaMetricsTool
from moonai import Agent, Mission, Squad
from dotenv import load_dotenv

load_dotenv()

meta_tool = MetaMetricsTool()

analytics_agent = Agent(
    role="Meta Ads Analyst",
    goal="Analyze Meta Ads metrics and provide insights",
    backstory="Specialist in analyzing Meta Ads performance",
    llm="gpt-4o-mini",
    verbose=True,
    tools=[meta_tool]
)

analyze_ads = Mission(
    description="Analyze Meta Ads metrics for the last 7 days and provide key insights",
    expected_output="",
    agent=analytics_agent,
    tools=[meta_tool],
    output_file="meta_analysis.txt"
)

squad = Squad(
    agents=[analytics_agent],
    missions=[analyze_ads],
    verbose=True
)

squad.kickoff()

# python test_MetaMetricsTool.py