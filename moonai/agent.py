import os
import shutil
import subprocess
from typing import Any, List, Literal, Optional, Union

from pydantic import Field, InstanceOf, PrivateAttr, model_validator

from moonai.agents import CacheHandler
from moonai.agents.agent_builder.base_agent import BaseAgent
from moonai.agents.squad_agent_executor import SquadAgentExecutor
from moonai.cli.constants import ENV_VARS
from moonai.llm import LLM
from moonai.memory.contextual.contextual_memory import ContextualMemory
from moonai.tools import BaseTool
from moonai.tools.agent_tools.agent_tools import AgentTools
from moonai.utilities import Converter, Prompts
from moonai.utilities.constants import TRAINED_AGENTS_DATA_FILE, TRAINING_DATA_FILE
from moonai.utilities.token_counter_callback import TokenCalcHandler
from moonai.utilities.training_handler import SquadTrainingHandler


def mock_agent_ops_provider():
    def track_agent(*args, **kwargs):
        def noop(f):
            return f

        return noop

    return track_agent


agentops = None

if os.environ.get("AGENTOPS_API_KEY"):
    try:
        from agentops import track_agent
    except ImportError:
        track_agent = mock_agent_ops_provider()
else:
    track_agent = mock_agent_ops_provider()


@track_agent()
class Agent(BaseAgent):
    """Represents an agent in a system.

    Each agent has a role, a goal, a backstory, and an optional language model (llm).
    The agent can also have memory, can operate in verbose mode, and can delegate missions to other agents.

    Attributes:
            agent_executor: An instance of the SquadAgentExecutor class.
            role: The role of the agent.
            goal: The objective of the agent.
            backstory: The backstory of the agent.
            knowledge: The knowledge base of the agent.
            config: Dict representation of agent configuration.
            llm: The language model that will run the agent.
            function_calling_llm: The language model that will handle the tool calling for this agent, it overrides the squad function_calling_llm.
            max_iter: Maximum number of iterations for an agent to execute a mission.
            memory: Whether the agent should have memory or not.
            max_rpm: Maximum number of requests per minute for the agent execution to be respected.
            verbose: Whether the agent execution should be in verbose mode.
            allow_delegation: Whether the agent is allowed to delegate missions to other agents.
            tools: Tools at agents disposal
            step_callback: Callback to be executed after each step of the agent execution.
    """

    _times_executed: int = PrivateAttr(default=0)
    max_execution_time: Optional[int] = Field(
        default=None,
        description="Maximum execution time for an agent to execute a mission",
    )
    agent_ops_agent_name: str = None  # type: ignore # Incompatible types in assignment (expression has type "None", variable has type "str")
    agent_ops_agent_id: str = None  # type: ignore # Incompatible types in assignment (expression has type "None", variable has type "str")
    cache_handler: InstanceOf[CacheHandler] = Field(
        default=None, description="An instance of the CacheHandler class."
    )
    step_callback: Optional[Any] = Field(
        default=None,
        description="Callback to be executed after each step of the agent execution.",
    )
    use_system_prompt: Optional[bool] = Field(
        default=True,
        description="Use system prompt for the agent.",
    )
    llm: Union[str, InstanceOf[LLM], Any] = Field(
        description="Language model that will run the agent.", default=None
    )
    function_calling_llm: Optional[Any] = Field(
        description="Language model that will run the agent.", default=None
    )
    system_template: Optional[str] = Field(
        default=None, description="System format for the agent."
    )
    prompt_template: Optional[str] = Field(
        default=None, description="Prompt format for the agent."
    )
    response_template: Optional[str] = Field(
        default=None, description="Response format for the agent."
    )
    tools_results: Optional[List[Any]] = Field(
        default=[], description="Results of the tools used by the agent."
    )
    allow_code_execution: Optional[bool] = Field(
        default=False, description="Enable code execution for the agent."
    )
    respect_context_window: bool = Field(
        default=True,
        description="Keep messages under the context window size by summarizing content.",
    )
    max_iter: int = Field(
        default=20,
        description="Maximum number of iterations for an agent to execute a mission before giving it's best answer",
    )
    max_retry_limit: int = Field(
        default=2,
        description="Maximum number of retries for an agent to execute a mission when an error occurs.",
    )
    code_execution_mode: Literal["safe", "unsafe"] = Field(
        default="safe",
        description="Mode for code execution: 'safe' (using Docker) or 'unsafe' (direct execution).",
    )

    @model_validator(mode="after")
    def post_init_setup(self):
        self.agent_ops_agent_name = self.role
        unnacepted_attributes = [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_REGION_NAME",
        ]

        # Handle different cases for self.llm
        if isinstance(self.llm, str):
            # If it's a string, create an LLM instance
            self.llm = LLM(model=self.llm)
        elif isinstance(self.llm, LLM):
            # If it's already an LLM instance, keep it as is
            pass
        elif self.llm is None:
            # Determine the model name from environment variables or use default
            model_name = (
                os.environ.get("OPENAI_MODEL_NAME")
                or os.environ.get("MODEL")
                or "gpt-4o-mini"
            )
            llm_params = {"model": model_name}

            api_base = os.environ.get("OPENAI_API_BASE") or os.environ.get(
                "OPENAI_BASE_URL"
            )
            if api_base:
                llm_params["base_url"] = api_base

            set_provider = model_name.split("/")[0] if "/" in model_name else "openai"

            # Iterate over all environment variables to find matching API keys or use defaults
            for provider, env_vars in ENV_VARS.items():
                if provider == set_provider:
                    for env_var in env_vars:
                        if env_var["key_name"] in unnacepted_attributes:
                            continue
                        # Check if the environment variable is set
                        if "key_name" in env_var:
                            env_value = os.environ.get(env_var["key_name"])
                            if env_value:
                                # Map key names containing "API_KEY" to "api_key"
                                key_name = (
                                    "api_key"
                                    if "API_KEY" in env_var["key_name"]
                                    else env_var["key_name"]
                                )
                                # Map key names containing "API_BASE" to "api_base"
                                key_name = (
                                    "api_base"
                                    if "API_BASE" in env_var["key_name"]
                                    else key_name
                                )
                                # Map key names containing "API_VERSION" to "api_version"
                                key_name = (
                                    "api_version"
                                    if "API_VERSION" in env_var["key_name"]
                                    else key_name
                                )
                                llm_params[key_name] = env_value
                        # Check for default values if the environment variable is not set
                        elif env_var.get("default", False):
                            for key, value in env_var.items():
                                if key not in ["prompt", "key_name", "default"]:
                                    # Only add default if the key is already set in os.environ
                                    if key in os.environ:
                                        llm_params[key] = value

            self.llm = LLM(**llm_params)
        else:
            # For any other type, attempt to extract relevant attributes
            llm_params = {
                "model": getattr(self.llm, "model_name", None)
                or getattr(self.llm, "deployment_name", None)
                or str(self.llm),
                "temperature": getattr(self.llm, "temperature", None),
                "max_tokens": getattr(self.llm, "max_tokens", None),
                "logprobs": getattr(self.llm, "logprobs", None),
                "timeout": getattr(self.llm, "timeout", None),
                "max_retries": getattr(self.llm, "max_retries", None),
                "api_key": getattr(self.llm, "api_key", None),
                "base_url": getattr(self.llm, "base_url", None),
                "organization": getattr(self.llm, "organization", None),
            }
            # Remove None values to avoid passing unnecessary parameters
            llm_params = {k: v for k, v in llm_params.items() if v is not None}
            self.llm = LLM(**llm_params)

        # Similar handling for function_calling_llm
        if self.function_calling_llm:
            if isinstance(self.function_calling_llm, str):
                self.function_calling_llm = LLM(model=self.function_calling_llm)
            elif not isinstance(self.function_calling_llm, LLM):
                self.function_calling_llm = LLM(
                    model=getattr(self.function_calling_llm, "model_name", None)
                    or getattr(self.function_calling_llm, "deployment_name", None)
                    or str(self.function_calling_llm)
                )

        if not self.agent_executor:
            self._setup_agent_executor()

        if self.allow_code_execution:
            self._validate_docker_installation()

        return self

    def _setup_agent_executor(self):
        if not self.cache_handler:
            self.cache_handler = CacheHandler()
        self.set_cache_handler(self.cache_handler)

    def execute_mission(
        self,
        mission: Any,
        context: Optional[str] = None,
        tools: Optional[List[BaseTool]] = None,
    ) -> str:
        """Execute a mission with the agent.

        Args:
            mission: Mission to execute.
            context: Context to execute the mission in.
            tools: Tools to use for the mission.

        Returns:
            Output of the agent
        """
        if self.tools_handler:
            self.tools_handler.last_used_tool = {}  # type: ignore # Incompatible types in assignment (expression has type "dict[Never, Never]", variable has type "ToolCalling")

        mission_prompt = mission.prompt()

        if context:
            mission_prompt = self.i18n.slice("mission_with_context").format(
                mission=mission_prompt, context=context
            )

        if self.squad and self.squad.memory:
            contextual_memory = ContextualMemory(
                self.squad.memory_config,
                self.squad._short_term_memory,
                self.squad._long_term_memory,
                self.squad._entity_memory,
                self.squad._user_memory,
            )
            memory = contextual_memory.build_context_for_mission(mission, context)
            if memory.strip() != "":
                mission_prompt += self.i18n.slice("memory").format(memory=memory)

        # Integrate the knowledge base
        if self.squad and self.squad.knowledge:
            knowledge_snippets = self.squad.knowledge.query([mission.prompt()])
            valid_snippets = [
                result["context"] 
                for result in knowledge_snippets 
                if result and result.get("context")
            ]
            if valid_snippets:
                formatted_knowledge = "\n".join(valid_snippets)
                mission_prompt += f"\n\nAdditional Information:\n{formatted_knowledge}"

        tools = tools or self.tools or []
        self.create_agent_executor(tools=tools, mission=mission)

        if self.squad and self.squad._train:
            mission_prompt = self._training_handler(mission_prompt=mission_prompt)
        else:
            mission_prompt = self._use_trained_data(mission_prompt=mission_prompt)

        try:
            result = self.agent_executor.invoke(
                {
                    "input": mission_prompt,
                    "tool_names": self.agent_executor.tools_names,
                    "tools": self.agent_executor.tools_description,
                    "ask_for_human_input": mission.human_input,
                }
            )["output"]
        except Exception as e:
            self._times_executed += 1
            if self._times_executed > self.max_retry_limit:
                raise e
            result = self.execute_mission(mission, context, tools)

        if self.max_rpm and self._rpm_controller:
            self._rpm_controller.stop_rpm_counter()

        # If there was any tool in self.tools_results that had result_as_answer
        # set to True, return the results of the last tool that had
        # result_as_answer set to True
        for tool_result in self.tools_results:  # type: ignore # Item "None" of "list[Any] | None" has no attribute "__iter__" (not iterable)
            if tool_result.get("result_as_answer", False):
                result = tool_result["result"]

        return result

    def create_agent_executor(
        self, tools: Optional[List[BaseTool]] = None, mission=None
    ) -> None:
        """Create an agent executor for the agent.

        Returns:
            An instance of the SquadAgentExecutor class.
        """
        tools = tools or self.tools or []
        parsed_tools = self._parse_tools(tools)

        prompt = Prompts(
            agent=self,
            tools=tools,
            i18n=self.i18n,
            use_system_prompt=self.use_system_prompt,
            system_template=self.system_template,
            prompt_template=self.prompt_template,
            response_template=self.response_template,
        ).mission_execution()

        stop_words = [self.i18n.slice("observation")]

        if self.response_template:
            stop_words.append(
                self.response_template.split("{{ .Response }}")[1].strip()
            )

        self.agent_executor = SquadAgentExecutor(
            llm=self.llm,
            mission=mission,
            agent=self,
            squad=self.squad,
            tools=parsed_tools,
            prompt=prompt,
            original_tools=tools,
            stop_words=stop_words,
            max_iter=self.max_iter,
            tools_handler=self.tools_handler,
            tools_names=self.__tools_names(parsed_tools),
            tools_description=self._render_text_description_and_args(parsed_tools),
            step_callback=self.step_callback,
            function_calling_llm=self.function_calling_llm,
            respect_context_window=self.respect_context_window,
            request_within_rpm_limit=(
                self._rpm_controller.check_or_wait if self._rpm_controller else None
            ),
            callbacks=[TokenCalcHandler(self._token_process)],
        )

    def get_delegation_tools(self, agents: List[BaseAgent]):
        agent_tools = AgentTools(agents=agents)
        tools = agent_tools.tools()
        return tools

    def get_code_execution_tools(self):
        try:
            from moonai.moonai_tools import CodeInterpreterTool

            # Set the unsafe_mode based on the code_execution_mode attribute
            unsafe_mode = self.code_execution_mode == "unsafe"
            return [CodeInterpreterTool(unsafe_mode=unsafe_mode)]
        except ModuleNotFoundError:
            self._logger.log(
                "info", "Coding tools not available. Install moonai.moonai_tools. "
            )

    def get_output_converter(self, llm, text, model, instructions):
        return Converter(llm=llm, text=text, model=model, instructions=instructions)

    def _parse_tools(self, tools: List[Any]) -> List[Any]:  # type: ignore
        """Parse tools to be used for the mission."""
        tools_list = []
        try:
            # tentatively try to import from moonai.moonai_tools import BaseTool as moonaiTool
            from moonai.tools import BaseTool as moonaiTool

            for tool in tools:
                if isinstance(tool, moonaiTool):
                    tools_list.append(tool.to_langchain())
                else:
                    tools_list.append(tool)
        except ModuleNotFoundError:
            tools_list = []
            for tool in tools:
                tools_list.append(tool)

        return tools_list

    def _training_handler(self, mission_prompt: str) -> str:
        """Handle training data for the agent mission prompt to improve output on Training."""
        if data := SquadTrainingHandler(TRAINING_DATA_FILE).load():
            agent_id = str(self.id)

            if data.get(agent_id):
                human_feedbacks = [
                    i["human_feedback"] for i in data.get(agent_id, {}).values()
                ]
                mission_prompt += (
                    "\n\nYou MUST follow these instructions: \n "
                    + "\n - ".join(human_feedbacks)
                )

        return mission_prompt

    def _use_trained_data(self, mission_prompt: str) -> str:
        """Use trained data for the agent mission prompt to improve output."""
        if data := SquadTrainingHandler(TRAINED_AGENTS_DATA_FILE).load():
            if trained_data_output := data.get(self.role):
                mission_prompt += (
                    "\n\nYou MUST follow these instructions: \n - "
                    + "\n - ".join(trained_data_output["suggestions"])
                )
        return mission_prompt

    def _render_text_description(self, tools: List[Any]) -> str:
        """Render the tool name and description in plain text.

        Output will be in the format of:

        .. code-block:: markdown

            search: This tool is used for search
            calculator: This tool is used for math
        """
        description = "\n".join(
            [
                f"Tool name: {tool.name}\nTool description:\n{tool.description}"
                for tool in tools
            ]
        )

        return description

    def _render_text_description_and_args(self, tools: List[BaseTool]) -> str:
        """Render the tool name, description, and args in plain text.

            Output will be in the format of:

            .. code-block:: markdown

            search: This tool is used for search, args: {"query": {"type": "string"}}
            calculator: This tool is used for math, \
            args: {"expression": {"type": "string"}}
        """
        tool_strings = []
        for tool in tools:
            tool_strings.append(tool.description)

        return "\n".join(tool_strings)

    def _validate_docker_installation(self) -> None:
        """Check if Docker is installed and running."""
        if not shutil.which("docker"):
            raise RuntimeError(
                f"Docker is not installed. Please install Docker to use code execution with agent: {self.role}"
            )

        try:
            subprocess.run(
                ["docker", "info"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError:
            raise RuntimeError(
                f"Docker is not running. Please start Docker to use code execution with agent: {self.role}"
            )

    @staticmethod
    def __tools_names(tools) -> str:
        return ", ".join([t.name for t in tools])

    def __repr__(self):
        return f"Agent(role={self.role}, goal={self.goal}, backstory={self.backstory})"