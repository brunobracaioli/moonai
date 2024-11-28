import asyncio
import json
import os
import uuid
import warnings
from concurrent.futures import Future
from hashlib import md5
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

from pydantic import (
    UUID4,
    BaseModel,
    Field,
    InstanceOf,
    Json,
    PrivateAttr,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError

from moonai.agent import Agent
from moonai.agents.agent_builder.base_agent import BaseAgent
from moonai.agents.cache import CacheHandler
from moonai.squads.squad_output import SquadOutput
from moonai.llm import LLM
from moonai.memory.entity.entity_memory import EntityMemory
from moonai.memory.long_term.long_term_memory import LongTermMemory
from moonai.memory.short_term.short_term_memory import ShortTermMemory
from moonai.knowledge.knowledge import Knowledge
from moonai.memory.user.user_memory import UserMemory
from moonai.process import Process
from moonai.mission import Mission
from moonai.missions.conditional_mission import ConditionalMission
from moonai.missions.mission_output import MissionOutput
from moonai.telemetry import Telemetry
from moonai.tools.agent_tools.agent_tools import AgentTools
from moonai.types.usage_metrics import UsageMetrics
from moonai.utilities import I18N, FileHandler, Logger, RPMController
from moonai.utilities.constants import TRAINING_DATA_FILE
from moonai.utilities.evaluators.squad_evaluator_handler import SquadEvaluator
from moonai.utilities.evaluators.mission_evaluator import MissionEvaluator
from moonai.utilities.formatter import (
    aggregate_raw_outputs_from_mission_outputs,
    aggregate_raw_outputs_from_missions,
)
from moonai.utilities.planning_handler import SquadPlanner
from moonai.utilities.mission_output_storage_handler import MissionOutputStorageHandler
from moonai.utilities.training_handler import SquadTrainingHandler

agentops = None
if os.environ.get("AGENTOPS_API_KEY"):
    try:
        import agentops  # type: ignore
    except ImportError:
        pass

if TYPE_CHECKING:
    from moonai.pipeline.pipeline import Pipeline

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


class Squad(BaseModel):
    """
    Represents a group of agents, defining how they should collaborate and the missions they should perform.

    Attributes:
        missions: List of missions assigned to the squad.
        agents: List of agents part of this squad.
        manager_llm: The language model that will run manager agent.
        manager_agent: Custom agent that will be used as manager.
        memory: Whether the squad should use memory to store memories of it's execution.
        memory_config: Configuration for the memory to be used for the squad.
        cache: Whether the squad should use a cache to store the results of the tools execution.
        function_calling_llm: The language model that will run the tool calling for all the agents.
        process: The process flow that the squad will follow (e.g., sequential, hierarchical).
        verbose: Indicates the verbosity level for logging during execution.
        config: Configuration settings for the squad.
        max_rpm: Maximum number of requests per minute for the squad execution to be respected.
        prompt_file: Path to the prompt json file to be used for the squad.
        id: A unique identifier for the squad instance.
        mission_callback: Callback to be executed after each mission for every agents execution.
        step_callback: Callback to be executed after each step for every agents execution.
        share_squad: Whether you want to share the complete squad information and execution with moonai to make the library better, and allow us to train models.
        planning: Plan the squad execution and add the plan to the squad.
    """

    __hash__ = object.__hash__  # type: ignore
    _execution_span: Any = PrivateAttr()
    _rpm_controller: RPMController = PrivateAttr()
    _logger: Logger = PrivateAttr()
    _file_handler: FileHandler = PrivateAttr()
    _cache_handler: InstanceOf[CacheHandler] = PrivateAttr(default=CacheHandler())
    _short_term_memory: Optional[InstanceOf[ShortTermMemory]] = PrivateAttr()
    _long_term_memory: Optional[InstanceOf[LongTermMemory]] = PrivateAttr()
    _entity_memory: Optional[InstanceOf[EntityMemory]] = PrivateAttr()
    _user_memory: Optional[InstanceOf[UserMemory]] = PrivateAttr()
    _train: Optional[bool] = PrivateAttr(default=False)
    _train_iteration: Optional[int] = PrivateAttr()
    _inputs: Optional[Dict[str, Any]] = PrivateAttr(default=None)
    _logging_color: str = PrivateAttr(
        default="bold_purple",
    )
    _mission_output_handler: MissionOutputStorageHandler = PrivateAttr(
        default_factory=MissionOutputStorageHandler
    )

    name: Optional[str] = Field(default=None)
    cache: bool = Field(default=True)
    missions: List[Mission] = Field(default_factory=list)
    agents: List[BaseAgent] = Field(default_factory=list)
    process: Process = Field(default=Process.sequential)
    verbose: bool = Field(default=False)
    memory: bool = Field(
        default=False,
        description="Whether the squad should use memory to store memories of it's execution",
    )
    memory_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Configuration for the memory to be used for the squad.",
    )
    short_term_memory: Optional[InstanceOf[ShortTermMemory]] = Field(
        default=None,
        description="An Instance of the ShortTermMemory to be used by the Squad",
    )
    long_term_memory: Optional[InstanceOf[LongTermMemory]] = Field(
        default=None,
        description="An Instance of the LongTermMemory to be used by the Squad",
    )
    entity_memory: Optional[InstanceOf[EntityMemory]] = Field(
        default=None,
        description="An Instance of the EntityMemory to be used by the Squad",
    )
    user_memory: Optional[InstanceOf[UserMemory]] = Field(
        default=None,
        description="An instance of the UserMemory to be used by the Squad to store/fetch memories of a specific user.",
    )
    embedder: Optional[dict] = Field(
        default=None,
        description="Configuration for the embedder to be used for the squad.",
    )
    usage_metrics: Optional[UsageMetrics] = Field(
        default=None,
        description="Metrics for the LLM usage during all missions execution.",
    )
    manager_llm: Optional[Any] = Field(
        description="Language model that will run the agent.", default=None
    )
    manager_agent: Optional[BaseAgent] = Field(
        description="Custom agent that will be used as manager.", default=None
    )
    function_calling_llm: Optional[Any] = Field(
        description="Language model that will run the agent.", default=None
    )
    config: Optional[Union[Json, Dict[str, Any]]] = Field(default=None)
    id: UUID4 = Field(default_factory=uuid.uuid4, frozen=True)
    share_squad: Optional[bool] = Field(default=False)
    step_callback: Optional[Any] = Field(
        default=None,
        description="Callback to be executed after each step for all agents execution.",
    )
    mission_callback: Optional[Any] = Field(
        default=None,
        description="Callback to be executed after each mission for all agents execution.",
    )
    before_kickoff_callbacks: List[
        Callable[[Optional[Dict[str, Any]]], Optional[Dict[str, Any]]]
    ] = Field(
        default_factory=list,
        description="List of callbacks to be executed before squad kickoff. It may be used to adjust inputs before the squad is executed.",
    )
    after_kickoff_callbacks: List[Callable[[SquadOutput], SquadOutput]] = Field(
        default_factory=list,
        description="List of callbacks to be executed after squad kickoff. It may be used to adjust the output of the squad.",
    )
    max_rpm: Optional[int] = Field(
        default=None,
        description="Maximum number of requests per minute for the squad execution to be respected.",
    )
    prompt_file: str = Field(
        default=None,
        description="Path to the prompt json file to be used for the squad.",
    )
    output_log_file: Optional[str] = Field(
        default=None,
        description="output_log_file",
    )
    planning: Optional[bool] = Field(
        default=False,
        description="Plan the squad execution and add the plan to the squad.",
    )
    planning_llm: Optional[Any] = Field(
        default=None,
        description="Language model that will run the AgentPlanner if planning is True.",
    )
    mission_execution_output_json_files: Optional[List[str]] = Field(
        default=None,
        description="List of file paths for mission execution JSON files.",
    )
    execution_logs: List[Dict[str, Any]] = Field(
        default=[],
        description="List of execution logs for missions",
    )
    knowledge: Optional[Dict[str, Any]] = Field(
        default=None, description="Knowledge for the squad. Add knowledge sources to the knowledge object."
    )


    @field_validator("id", mode="before")
    @classmethod
    def _deny_user_set_id(cls, v: Optional[UUID4]) -> None:
        """Prevent manual setting of the 'id' field by users."""
        if v:
            raise PydanticCustomError(
                "may_not_set_field", "The 'id' field cannot be set by the user.", {}
            )

    @field_validator("config", mode="before")
    @classmethod
    def check_config_type(
        cls, v: Union[Json, Dict[str, Any]]
    ) -> Union[Json, Dict[str, Any]]:
        """Validates that the config is a valid type.
        Args:
            v: The config to be validated.
        Returns:
            The config if it is valid.
        """

        # TODO: Improve typing
        return json.loads(v) if isinstance(v, Json) else v  # type: ignore

    @model_validator(mode="after")
    def set_private_attrs(self) -> "Squad":
        """Set private attributes."""
        self._cache_handler = CacheHandler()
        self._logger = Logger(verbose=self.verbose)
        if self.output_log_file:
            self._file_handler = FileHandler(self.output_log_file)
        self._rpm_controller = RPMController(max_rpm=self.max_rpm, logger=self._logger)
        if self.function_calling_llm:
            if isinstance(self.function_calling_llm, str):
                self.function_calling_llm = LLM(model=self.function_calling_llm)
            elif not isinstance(self.function_calling_llm, LLM):
                self.function_calling_llm = LLM(
                    model=getattr(self.function_calling_llm, "model_name", None)
                    or getattr(self.function_calling_llm, "deployment_name", None)
                    or str(self.function_calling_llm)
                )
        self._telemetry = Telemetry()
        self._telemetry.set_tracer()
        return self

    @model_validator(mode="after")
    def create_squad_memory(self) -> "Squad":
        """Set private attributes."""
        if self.memory:
            self._long_term_memory = (
                self.long_term_memory if self.long_term_memory else LongTermMemory()
            )
            self._short_term_memory = (
                self.short_term_memory
                if self.short_term_memory
                else ShortTermMemory(
                    squad=self,
                    embedder_config=self.embedder,
                )
            )
            self._entity_memory = (
                self.entity_memory
                if self.entity_memory
                else EntityMemory(squad=self, embedder_config=self.embedder)
            )
            if hasattr(self, "memory_config") and self.memory_config is not None:
                self._user_memory = (
                    self.user_memory if self.user_memory else UserMemory(squad=self)
                )
            else:
                self._user_memory = None
        return self

    @model_validator(mode="after")
    def create_squad_knowledge(self) -> "Squad":
        if self.knowledge:
            try:
                self.knowledge = Knowledge(**self.knowledge) if isinstance(self.knowledge, dict) else self.knowledge
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid knowledge configuration: {str(e)}")
        return self

    @model_validator(mode="after")
    def check_manager_llm(self):
        """Validates that the language model is set when using hierarchical process."""
        if self.process == Process.hierarchical:
            if not self.manager_llm and not self.manager_agent:
                raise PydanticCustomError(
                    "missing_manager_llm_or_manager_agent",
                    "Attribute `manager_llm` or `manager_agent` is required when using hierarchical process.",
                    {},
                )

            if (self.manager_agent is not None) and (
                self.agents.count(self.manager_agent) > 0
            ):
                raise PydanticCustomError(
                    "manager_agent_in_agents",
                    "Manager agent should not be included in agents list.",
                    {},
                )

        return self

    @model_validator(mode="after")
    def check_config(self):
        """Validates that the squad is properly configured with agents and missions."""
        if not self.config and not self.missions and not self.agents:
            raise PydanticCustomError(
                "missing_keys",
                "Either 'agents' and 'missions' need to be set or 'config'.",
                {},
            )

        if self.config:
            self._setup_from_config()

        if self.agents:
            for agent in self.agents:
                if self.cache:
                    agent.set_cache_handler(self._cache_handler)
                if self.max_rpm:
                    agent.set_rpm_controller(self._rpm_controller)
        return self

    @model_validator(mode="after")
    def validate_missions(self):
        if self.process == Process.sequential:
            for mission in self.missions:
                if mission.agent is None:
                    raise PydanticCustomError(
                        "missing_agent_in_mission",
                        f"Sequential process error: Agent is missing in the mission with the following description: {mission.description}",  # type: ignore # Argument of type "str" cannot be assigned to parameter "message_template" of type "LiteralString"
                        {},
                    )

        return self

    @model_validator(mode="after")
    def validate_end_with_at_most_one_async_mission(self):
        """Validates that the squad ends with at most one asynchronous mission."""
        final_async_mission_count = 0

        # Traverse missions backward
        for mission in reversed(self.missions):
            if mission.async_execution:
                final_async_mission_count += 1
            else:
                break  # Stop traversing as soon as a non-async mission is encountered

        if final_async_mission_count > 1:
            raise PydanticCustomError(
                "async_mission_count",
                "The squad must end with at most one asynchronous mission.",
                {},
            )

        return self

    @model_validator(mode="after")
    def validate_first_mission(self) -> "Squad":
        """Ensure the first mission is not a ConditionalMission."""
        if self.missions and isinstance(self.missions[0], ConditionalMission):
            raise PydanticCustomError(
                "invalid_first_mission",
                "The first mission cannot be a ConditionalMission.",
                {},
            )
        return self

    @model_validator(mode="after")
    def validate_async_missions_not_async(self) -> "Squad":
        """Ensure that ConditionalMission is not async."""
        for mission in self.missions:
            if mission.async_execution and isinstance(mission, ConditionalMission):
                raise PydanticCustomError(
                    "invalid_async_conditional_mission",
                    f"Conditional Mission: {mission.description} , cannot be executed asynchronously.",  # type: ignore # Argument of type "str" cannot be assigned to parameter "message_template" of type "LiteralString"
                    {},
                )
        return self

    @model_validator(mode="after")
    def validate_async_mission_cannot_include_sequential_async_missions_in_context(self):
        """
        Validates that if a mission is set to be executed asynchronously,
        it cannot include other asynchronous missions in its context unless
        separated by a synchronous mission.
        """
        for i, mission in enumerate(self.missions):
            if mission.async_execution and mission.context:
                for context_mission in mission.context:
                    if context_mission.async_execution:
                        for j in range(i - 1, -1, -1):
                            if self.missions[j] == context_mission:
                                raise ValueError(
                                    f"Mission '{mission.description}' is asynchronous and cannot include other sequential asynchronous missions in its context."
                                )
                            if not self.missions[j].async_execution:
                                break
        return self

    @model_validator(mode="after")
    def validate_context_no_future_missions(self):
        """Validates that a mission's context does not include future missions."""
        mission_indices = {id(mission): i for i, mission in enumerate(self.missions)}

        for mission in self.missions:
            if mission.context:
                for context_mission in mission.context:
                    if id(context_mission) not in mission_indices:
                        continue  # Skip context missions not in the main missions list
                    if mission_indices[id(context_mission)] > mission_indices[id(mission)]:
                        raise ValueError(
                            f"Mission '{mission.description}' has a context dependency on a future mission '{context_mission.description}', which is not allowed."
                        )
        return self

    @property
    def key(self) -> str:
        source = [agent.key for agent in self.agents] + [
            mission.key for mission in self.missions
        ]
        return md5("|".join(source).encode(), usedforsecurity=False).hexdigest()

    def _setup_from_config(self):
        assert self.config is not None, "Config should not be None."

        """Initializes agents and missions from the provided config."""
        if not self.config.get("agents") or not self.config.get("missions"):
            raise PydanticCustomError(
                "missing_keys_in_config", "Config should have 'agents' and 'missions'.", {}
            )

        self.process = self.config.get("process", self.process)
        self.agents = [Agent(**agent) for agent in self.config["agents"]]
        self.missions = [self._create_mission(mission) for mission in self.config["missions"]]

    def _create_mission(self, mission_config: Dict[str, Any]) -> Mission:
        """Creates a mission instance from its configuration.

        Args:
            mission_config: The configuration of the mission.

        Returns:
            A mission instance.
        """
        mission_agent = next(
            agt for agt in self.agents if agt.role == mission_config["agent"]
        )
        del mission_config["agent"]
        return Mission(**mission_config, agent=mission_agent)

    def _setup_for_training(self, filename: str) -> None:
        """Sets up the squad for training."""
        self._train = True

        for mission in self.missions:
            mission.human_input = True

        for agent in self.agents:
            agent.allow_delegation = False

        SquadTrainingHandler(TRAINING_DATA_FILE).initialize_file()
        SquadTrainingHandler(filename).initialize_file()

    def train(
        self, n_iterations: int, filename: str, inputs: Optional[Dict[str, Any]] = {}
    ) -> None:
        """Trains the squad for a given number of iterations."""
        train_squad = self.copy()
        train_squad._setup_for_training(filename)

        for n_iteration in range(n_iterations):
            train_squad._train_iteration = n_iteration
            train_squad.kickoff(inputs=inputs)

        training_data = SquadTrainingHandler(TRAINING_DATA_FILE).load()

        for agent in train_squad.agents:
            if training_data.get(str(agent.id)):
                result = MissionEvaluator(agent).evaluate_training_data(
                    training_data=training_data, agent_id=str(agent.id)
                )

                SquadTrainingHandler(filename).save_trained_data(
                    agent_id=str(agent.role), trained_data=result.model_dump()
                )

    def kickoff(
        self,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> SquadOutput:
        from moonai import show_banner
        show_banner()
        for before_callback in self.before_kickoff_callbacks:
            inputs = before_callback(inputs)

        """Starts the squad to work on its assigned missions."""
        self._execution_span = self._telemetry.squad_execution_span(self, inputs)
        self._mission_output_handler.reset()
        self._logging_color = "bold_purple"

        if inputs is not None:
            self._inputs = inputs
            self._interpolate_inputs(inputs)
        self._set_missions_callbacks()

        i18n = I18N(prompt_file=self.prompt_file)

        for agent in self.agents:
            agent.i18n = i18n
            # type: ignore[attr-defined] # Argument 1 to "_interpolate_inputs" of "Squad" has incompatible type "dict[str, Any] | None"; expected "dict[str, Any]"
            agent.squad = self  # type: ignore[attr-defined]
            # TODO: Create an AgentFunctionCalling protocol for future refactoring
            if not agent.function_calling_llm:  # type: ignore # "BaseAgent" has no attribute "function_calling_llm"
                agent.function_calling_llm = self.function_calling_llm  # type: ignore # "BaseAgent" has no attribute "function_calling_llm"

            if agent.allow_code_execution:  # type: ignore # BaseAgent" has no attribute "allow_code_execution"
                agent.tools += agent.get_code_execution_tools()  # type: ignore # "BaseAgent" has no attribute "get_code_execution_tools"; maybe "get_delegation_tools"?

            if not agent.step_callback:  # type: ignore # "BaseAgent" has no attribute "step_callback"
                agent.step_callback = self.step_callback  # type: ignore # "BaseAgent" has no attribute "step_callback"

            agent.create_agent_executor()

        if self.planning:
            self._handle_squad_planning()

        metrics: List[UsageMetrics] = []

        if self.process == Process.sequential:
            result = self._run_sequential_process()
        elif self.process == Process.hierarchical:
            result = self._run_hierarchical_process()
        else:
            raise NotImplementedError(
                f"The process '{self.process}' is not implemented yet."
            )

        for after_callback in self.after_kickoff_callbacks:
            result = after_callback(result)

        metrics += [agent._token_process.get_summary() for agent in self.agents]

        self.usage_metrics = UsageMetrics()
        for metric in metrics:
            self.usage_metrics.add_usage_metrics(metric)

        return result

    def kickoff_for_each(self, inputs: List[Dict[str, Any]]) -> List[SquadOutput]:
        """Executes the Squad's workflow for each input in the list and aggregates results."""
        results: List[SquadOutput] = []

        # Initialize the parent squad's usage metrics
        total_usage_metrics = UsageMetrics()

        for input_data in inputs:
            squad = self.copy()

            output = squad.kickoff(inputs=input_data)

            if squad.usage_metrics:
                total_usage_metrics.add_usage_metrics(squad.usage_metrics)

            results.append(output)

        self.usage_metrics = total_usage_metrics
        self._mission_output_handler.reset()
        return results

    async def kickoff_async(self, inputs: Optional[Dict[str, Any]] = {}) -> SquadOutput:
        """Asynchronous kickoff method to start the squad execution."""
        return await asyncio.to_thread(self.kickoff, inputs)

    async def kickoff_for_each_async(self, inputs: List[Dict]) -> List[SquadOutput]:
        squad_copies = [self.copy() for _ in inputs]

        async def run_squad(squad, input_data):
            return await squad.kickoff_async(inputs=input_data)

        missions = [
            asyncio.create_mission(run_squad(squad_copies[i], inputs[i]))
            for i in range(len(inputs))
        ]

        results = await asyncio.gather(*missions)

        total_usage_metrics = UsageMetrics()
        for squad in squad_copies:
            if squad.usage_metrics:
                total_usage_metrics.add_usage_metrics(squad.usage_metrics)

        self.usage_metrics = total_usage_metrics
        self._mission_output_handler.reset()
        return results

    def _handle_squad_planning(self):
        """Handles the Squad planning."""
        self._logger.log("info", "Planning the squad execution")
        result = SquadPlanner(
            missions=self.missions, planning_agent_llm=self.planning_llm
        )._handle_squad_planning()

        for mission, step_plan in zip(self.missions, result.list_of_plans_per_mission):
            mission.description += step_plan.plan

    def _store_execution_log(
        self,
        mission: Mission,
        output: MissionOutput,
        mission_index: int,
        was_replayed: bool = False,
    ):
        if self._inputs:
            inputs = self._inputs
        else:
            inputs = {}

        log = {
            "mission": mission,
            "output": {
                "description": output.description,
                "summary": output.summary,
                "raw": output.raw,
                "pydantic": output.pydantic,
                "json_dict": output.json_dict,
                "output_format": output.output_format,
                "agent": output.agent,
            },
            "mission_index": mission_index,
            "inputs": inputs,
            "was_replayed": was_replayed,
        }
        self._mission_output_handler.update(mission_index, log)

    def _run_sequential_process(self) -> SquadOutput:
        """Executes missions sequentially and returns the final output."""
        return self._execute_missions(self.missions)

    def _run_hierarchical_process(self) -> SquadOutput:
        """Creates and assigns a manager agent to make sure the squad completes the missions."""
        self._create_manager_agent()
        return self._execute_missions(self.missions)

    def _create_manager_agent(self):
        i18n = I18N(prompt_file=self.prompt_file)
        if self.manager_agent is not None:
            self.manager_agent.allow_delegation = True
            manager = self.manager_agent
            if manager.tools is not None and len(manager.tools) > 0:
                self._logger.log(
                    "warning", "Manager agent should not have tools", color="orange"
                )
                manager.tools = []
                raise Exception("Manager agent should not have tools")
            manager.tools = self.manager_agent.get_delegation_tools(self.agents)
        else:
            self.manager_llm = (
                getattr(self.manager_llm, "model_name", None)
                or getattr(self.manager_llm, "deployment_name", None)
                or self.manager_llm
            )
            manager = Agent(
                role=i18n.retrieve("hierarchical_manager_agent", "role"),
                goal=i18n.retrieve("hierarchical_manager_agent", "goal"),
                backstory=i18n.retrieve("hierarchical_manager_agent", "backstory"),
                tools=AgentTools(agents=self.agents).tools(),
                llm=self.manager_llm,
                verbose=self.verbose,
            )
            self.manager_agent = manager
        manager.squad = self

    def _execute_missions(
        self,
        missions: List[Mission],
        start_index: Optional[int] = 0,
        was_replayed: bool = False,
    ) -> SquadOutput:
        """Executes missions sequentially and returns the final output.

        Args:
            missions (List[Mission]): List of missions to execute
            manager (Optional[BaseAgent], optional): Manager agent to use for delegation. Defaults to None.

        Returns:
            SquadOutput: Final output of the squad
        """

        mission_outputs: List[MissionOutput] = []
        futures: List[Tuple[Mission, Future[MissionOutput], int]] = []
        last_sync_output: Optional[MissionOutput] = None

        for mission_index, mission in enumerate(missions):
            if start_index is not None and mission_index < start_index:
                if mission.output:
                    if mission.async_execution:
                        mission_outputs.append(mission.output)
                    else:
                        mission_outputs = [mission.output]
                        last_sync_output = mission.output
                continue

            agent_to_use = self._get_agent_to_use(mission)
            if agent_to_use is None:
                raise ValueError(
                    f"No agent available for mission: {mission.description}. Ensure that either the mission has an assigned agent or a manager agent is provided."
                )

            self._prepare_agent_tools(mission)
            self._log_mission_start(mission, agent_to_use.role)

            if isinstance(mission, ConditionalMission):
                skipped_mission_output = self._handle_conditional_mission(
                    mission, mission_outputs, futures, mission_index, was_replayed
                )
                if skipped_mission_output:
                    continue

            if mission.async_execution:
                context = self._get_context(
                    mission, [last_sync_output] if last_sync_output else []
                )
                future = mission.execute_async(
                    agent=agent_to_use,
                    context=context,
                    tools=agent_to_use.tools,
                )
                futures.append((mission, future, mission_index))
            else:
                if futures:
                    mission_outputs = self._process_async_missions(futures, was_replayed)
                    futures.clear()

                context = self._get_context(mission, mission_outputs)
                mission_output = mission.execute_sync(
                    agent=agent_to_use,
                    context=context,
                    tools=agent_to_use.tools,
                )
                mission_outputs = [mission_output]
                self._process_mission_result(mission, mission_output)
                self._store_execution_log(mission, mission_output, mission_index, was_replayed)

        if futures:
            mission_outputs = self._process_async_missions(futures, was_replayed)

        return self._create_squad_output(mission_outputs)

    def _handle_conditional_mission(
        self,
        mission: ConditionalMission,
        mission_outputs: List[MissionOutput],
        futures: List[Tuple[Mission, Future[MissionOutput], int]],
        mission_index: int,
        was_replayed: bool,
    ) -> Optional[MissionOutput]:
        if futures:
            mission_outputs = self._process_async_missions(futures, was_replayed)
            futures.clear()

        previous_output = mission_outputs[mission_index - 1] if mission_outputs else None
        if previous_output is not None and not mission.should_execute(previous_output):
            self._logger.log(
                "debug",
                f"Skipping conditional mission: {mission.description}",
                color="yellow",
            )
            skipped_mission_output = mission.get_skipped_mission_output()

            if not was_replayed:
                self._store_execution_log(mission, skipped_mission_output, mission_index)
            return skipped_mission_output
        return None

    def _prepare_agent_tools(self, mission: Mission):
        if self.process == Process.hierarchical:
            if self.manager_agent:
                self._update_manager_tools(mission)
            else:
                raise ValueError("Manager agent is required for hierarchical process.")
        elif mission.agent and mission.agent.allow_delegation:
            self._add_delegation_tools(mission)

    def _get_agent_to_use(self, mission: Mission) -> Optional[BaseAgent]:
        if self.process == Process.hierarchical:
            return self.manager_agent
        return mission.agent

    def _add_delegation_tools(self, mission: Mission):
        agents_for_delegation = [agent for agent in self.agents if agent != mission.agent]
        if len(self.agents) > 1 and len(agents_for_delegation) > 0 and mission.agent:
            delegation_tools = mission.agent.get_delegation_tools(agents_for_delegation)

            # Add tools if they are not already in mission.tools
            for new_tool in delegation_tools:
                # Find the index of the tool with the same name
                existing_tool_index = next(
                    (
                        index
                        for index, tool in enumerate(mission.tools or [])
                        if tool.name == new_tool.name
                    ),
                    None,
                )
                if not mission.tools:
                    mission.tools = []

                if existing_tool_index is not None:
                    # Replace the existing tool
                    mission.tools[existing_tool_index] = new_tool
                else:
                    # Add the new tool
                    mission.tools.append(new_tool)

    def _log_mission_start(self, mission: Mission, role: str = "None"):
        if self.output_log_file:
            self._file_handler.log(
                mission_name=mission.name, mission=mission.description, agent=role, status="started"
            )

    def _update_manager_tools(self, mission: Mission):
        if self.manager_agent:
            if mission.agent:
                self.manager_agent.tools = mission.agent.get_delegation_tools([mission.agent])
            else:
                self.manager_agent.tools = self.manager_agent.get_delegation_tools(
                    self.agents
                )

    def _get_context(self, mission: Mission, mission_outputs: List[MissionOutput]):
        context = (
            aggregate_raw_outputs_from_missions(mission.context)
            if mission.context
            else aggregate_raw_outputs_from_mission_outputs(mission_outputs)
        )
        return context

    def _process_mission_result(self, mission: Mission, output: MissionOutput) -> None:
        role = mission.agent.role if mission.agent is not None else "None"
        if self.output_log_file:
            self._file_handler.log(
                mission_name=mission.name,
                mission=mission.description,
                agent=role,
                status="completed",
                output=output.raw,
            )

    def _create_squad_output(self, mission_outputs: List[MissionOutput]) -> SquadOutput:
        if len(mission_outputs) != 1:
            raise ValueError(
                "Something went wrong. Kickoff should return only one mission output."
            )
        final_mission_output = mission_outputs[0]
        final_string_output = final_mission_output.raw
        self._finish_execution(final_string_output)
        token_usage = self.calculate_usage_metrics()

        return SquadOutput(
            raw=final_mission_output.raw,
            pydantic=final_mission_output.pydantic,
            json_dict=final_mission_output.json_dict,
            missions_output=[mission.output for mission in self.missions if mission.output],
            token_usage=token_usage,
        )

    def _process_async_missions(
        self,
        futures: List[Tuple[Mission, Future[MissionOutput], int]],
        was_replayed: bool = False,
    ) -> List[MissionOutput]:
        mission_outputs: List[MissionOutput] = []
        for future_mission, future, mission_index in futures:
            mission_output = future.result()
            mission_outputs.append(mission_output)
            self._process_mission_result(future_mission, mission_output)
            self._store_execution_log(
                future_mission, mission_output, mission_index, was_replayed
            )
        return mission_outputs

    def _find_mission_index(
        self, mission_id: str, stored_outputs: List[Any]
    ) -> Optional[int]:
        return next(
            (
                index
                for (index, d) in enumerate(stored_outputs)
                if d["mission_id"] == str(mission_id)
            ),
            None,
        )

    def replay(
        self, mission_id: str, inputs: Optional[Dict[str, Any]] = None
    ) -> SquadOutput:
        stored_outputs = self._mission_output_handler.load()
        if not stored_outputs:
            raise ValueError(f"Mission with id {mission_id} not found in the squad's missions.")

        start_index = self._find_mission_index(mission_id, stored_outputs)

        if start_index is None:
            raise ValueError(f"Mission with id {mission_id} not found in the squad's missions.")

        replay_inputs = (
            inputs if inputs is not None else stored_outputs[start_index]["inputs"]
        )
        self._inputs = replay_inputs

        if replay_inputs:
            self._interpolate_inputs(replay_inputs)

        if self.process == Process.hierarchical:
            self._create_manager_agent()

        for i in range(start_index):
            stored_output = stored_outputs[i][
                "output"
            ]  # for adding context to the mission
            mission_output = MissionOutput(
                description=stored_output["description"],
                agent=stored_output["agent"],
                raw=stored_output["raw"],
                pydantic=stored_output["pydantic"],
                json_dict=stored_output["json_dict"],
                output_format=stored_output["output_format"],
            )
            self.missions[i].output = mission_output

        self._logging_color = "bold_blue"
        result = self._execute_missions(self.missions, start_index, True)
        return result

    def copy(self):
        """Create a deep copy of the Squad."""

        exclude = {
            "id",
            "_rpm_controller",
            "_logger",
            "_execution_span",
            "_file_handler",
            "_cache_handler",
            "_short_term_memory",
            "_long_term_memory",
            "_entity_memory",
            "_telemetry",
            "agents",
            "missions",
        }

        cloned_agents = [agent.copy() for agent in self.agents]

        mission_mapping = {}

        cloned_missions = []
        for mission in self.missions:
            cloned_mission = mission.copy(cloned_agents, mission_mapping)
            cloned_missions.append(cloned_mission)
            mission_mapping[mission.key] = cloned_mission

        for cloned_mission, original_mission in zip(cloned_missions, self.missions):
            if original_mission.context:
                cloned_context = [
                    mission_mapping[context_mission.key]
                    for context_mission in original_mission.context
                ]
                cloned_mission.context = cloned_context

        copied_data = self.model_dump(exclude=exclude)
        copied_data = {k: v for k, v in copied_data.items() if v is not None}

        copied_data.pop("agents", None)
        copied_data.pop("missions", None)

        copied_squad = Squad(**copied_data, agents=cloned_agents, missions=cloned_missions)

        return copied_squad

    def _set_missions_callbacks(self) -> None:
        """Sets callback for every mission suing mission_callback"""
        for mission in self.missions:
            if not mission.callback:
                mission.callback = self.mission_callback

    def _interpolate_inputs(self, inputs: Dict[str, Any]) -> None:
        """Interpolates the inputs in the missions and agents."""
        [
            mission.interpolate_inputs(
                # type: ignore # "interpolate_inputs" of "Mission" does not return a value (it only ever returns None)
                inputs
            )
            for mission in self.missions
        ]
        # type: ignore # "interpolate_inputs" of "Agent" does not return a value (it only ever returns None)
        for agent in self.agents:
            agent.interpolate_inputs(inputs)

    def _finish_execution(self, final_string_output: str) -> None:
        if self.max_rpm:
            self._rpm_controller.stop_rpm_counter()
        if agentops:
            agentops.end_session(
                end_state="Success",
                end_state_reason="Finished Execution",
            )
        self._telemetry.end_squad(self, final_string_output)

    def calculate_usage_metrics(self) -> UsageMetrics:
        """Calculates and returns the usage metrics."""
        total_usage_metrics = UsageMetrics()
        for agent in self.agents:
            if hasattr(agent, "_token_process"):
                token_sum = agent._token_process.get_summary()
                total_usage_metrics.add_usage_metrics(token_sum)
        if self.manager_agent and hasattr(self.manager_agent, "_token_process"):
            token_sum = self.manager_agent._token_process.get_summary()
            total_usage_metrics.add_usage_metrics(token_sum)
        self.usage_metrics = total_usage_metrics
        return total_usage_metrics

    def test(
        self,
        n_iterations: int,
        openai_model_name: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Test and evaluate the Squad with the given inputs for n iterations concurrently using concurrent.futures."""
        test_squad = self.copy()

        self._test_execution_span = test_squad._telemetry.test_execution_span(
            test_squad,
            n_iterations,
            inputs,
            openai_model_name,  # type: ignore[arg-type]
        )  # type: ignore[arg-type]
        evaluator = SquadEvaluator(test_squad, openai_model_name)  # type: ignore[arg-type]

        for i in range(1, n_iterations + 1):
            evaluator.set_iteration(i)
            test_squad.kickoff(inputs=inputs)

        evaluator.print_squad_evaluation_result()

    def __rshift__(self, other: "Squad") -> "Pipeline":
        """
        Implements the >> operator to add another Squad to an existing Pipeline.
        """
        from moonai.pipeline.pipeline import Pipeline

        if not isinstance(other, Squad):
            raise TypeError(
                f"Unsupported operand type for >>: '{type(self).__name__}' and '{type(other).__name__}'"
            )
        return Pipeline(stages=[self, other])

    def __repr__(self):
        return f"Squad(id={self.id}, process={self.process}, number_of_agents={len(self.agents)}, number_of_missions={len(self.missions)})"
