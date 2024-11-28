
# moonai/__init__.py

import warnings

from moonai.agent import Agent
from moonai.squad import Squad
from moonai.flow.flow import Flow
from moonai.knowledge.knowledge import Knowledge
from moonai.llm import LLM
from moonai.pipeline import Pipeline
from moonai.process import Process
from moonai.routers import Router
from moonai.mission import Mission
from moonai.moonai_tools import tools
from moonai.moonai_tools.tools.base_tool import BaseTool


_banner_shown = False

def show_banner():
    global _banner_shown
    if not _banner_shown:
        banner = r"""
 __  __                         _    ___ 
|  \/  | ___   ___  _ __       / \  |_ _|
| |\/| |/ _ \ / _ \| '_ \     / _ \  | | 
| |  | | (_) | (_) | | | |   / ___ \ | | 
|_|  |_|\___/ \___/|_| |_|  /_/   \_\___|
        """
        print("\n\n")
        print("\033[1m\033[97m" + banner + "\033[0m")
        print("\033[1m\033[97mStarting Moon AI. Launching Rockets towards the Moon!\033[0m")
        print("\n\n\n")
        _banner_shown = True

warnings.filterwarnings(
    "ignore",
    message="Pydantic serializer warnings:",
    category=UserWarning,
    module="pydantic.main",
)
__version__ = "0.2.0"
__all__ = [
    "Agent",
    "Squad",
    "Process",
    "Mission",
    "Pipeline",
    "Router",
    "LLM",
    "Flow",
    "Knowledge",
    "tools",
    "BaseTool",
]
