import inspect
from pathlib import Path
from typing import Any, Callable, Dict, TypeVar, cast

import yaml
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T", bound=type)


def SquadBase(cls: T) -> T:
    class WrappedClass(cls):  # type: ignore
        is_squad_class: bool = True  # type: ignore

        # Get the directory of the class being decorated
        base_directory = Path(inspect.getfile(cls)).parent

        original_agents_config_path = getattr(
            cls, "agents_config", "config/agents.yaml"
        )
        original_missions_config_path = getattr(cls, "missions_config", "config/missions.yaml")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            agents_config_path = self.base_directory / self.original_agents_config_path
            missions_config_path = self.base_directory / self.original_missions_config_path

            self.agents_config = self.load_yaml(agents_config_path)
            self.missions_config = self.load_yaml(missions_config_path)

            self.map_all_agent_variables()
            self.map_all_mission_variables()

            # Preserve all decorated functions
            self._original_functions = {
                name: method
                for name, method in cls.__dict__.items()
                if any(
                    hasattr(method, attr)
                    for attr in [
                        "is_mission",
                        "is_agent",
                        "is_before_kickoff",
                        "is_after_kickoff",
                        "is_kickoff",
                    ]
                )
            }

            # Store specific function types
            self._original_missions = self._filter_functions(
                self._original_functions, "is_mission"
            )
            self._original_agents = self._filter_functions(
                self._original_functions, "is_agent"
            )
            self._before_kickoff = self._filter_functions(
                self._original_functions, "is_before_kickoff"
            )
            self._after_kickoff = self._filter_functions(
                self._original_functions, "is_after_kickoff"
            )
            self._kickoff = self._filter_functions(
                self._original_functions, "is_kickoff"
            )

        @staticmethod
        def load_yaml(config_path: Path):
            try:
                with open(config_path, "r", encoding="utf-8") as file:
                    return yaml.safe_load(file)
            except FileNotFoundError:
                print(f"File not found: {config_path}")
                raise

        def _get_all_functions(self):
            return {
                name: getattr(self, name)
                for name in dir(self)
                if callable(getattr(self, name))
            }

        def _filter_functions(
            self, functions: Dict[str, Callable], attribute: str
        ) -> Dict[str, Callable]:
            return {
                name: func
                for name, func in functions.items()
                if hasattr(func, attribute)
            }

        def map_all_agent_variables(self) -> None:
            all_functions = self._get_all_functions()
            llms = self._filter_functions(all_functions, "is_llm")
            tool_functions = self._filter_functions(all_functions, "is_tool")
            cache_handler_functions = self._filter_functions(
                all_functions, "is_cache_handler"
            )
            callbacks = self._filter_functions(all_functions, "is_callback")
            agents = self._filter_functions(all_functions, "is_agent")

            for agent_name, agent_info in self.agents_config.items():
                self._map_agent_variables(
                    agent_name,
                    agent_info,
                    agents,
                    llms,
                    tool_functions,
                    cache_handler_functions,
                    callbacks,
                )

        def _map_agent_variables(
            self,
            agent_name: str,
            agent_info: Dict[str, Any],
            agents: Dict[str, Callable],
            llms: Dict[str, Callable],
            tool_functions: Dict[str, Callable],
            cache_handler_functions: Dict[str, Callable],
            callbacks: Dict[str, Callable],
        ) -> None:
            if llm := agent_info.get("llm"):
                try:
                    self.agents_config[agent_name]["llm"] = llms[llm]()
                except KeyError:
                    self.agents_config[agent_name]["llm"] = llm

            if tools := agent_info.get("tools"):
                self.agents_config[agent_name]["tools"] = [
                    tool_functions[tool]() for tool in tools
                ]

            if function_calling_llm := agent_info.get("function_calling_llm"):
                self.agents_config[agent_name]["function_calling_llm"] = agents[
                    function_calling_llm
                ]()

            if step_callback := agent_info.get("step_callback"):
                self.agents_config[agent_name]["step_callback"] = callbacks[
                    step_callback
                ]()

            if cache_handler := agent_info.get("cache_handler"):
                self.agents_config[agent_name]["cache_handler"] = (
                    cache_handler_functions[cache_handler]()
                )

        def map_all_mission_variables(self) -> None:
            all_functions = self._get_all_functions()
            agents = self._filter_functions(all_functions, "is_agent")
            missions = self._filter_functions(all_functions, "is_mission")
            output_json_functions = self._filter_functions(
                all_functions, "is_output_json"
            )
            tool_functions = self._filter_functions(all_functions, "is_tool")
            callback_functions = self._filter_functions(all_functions, "is_callback")
            output_pydantic_functions = self._filter_functions(
                all_functions, "is_output_pydantic"
            )

            for mission_name, mission_info in self.missions_config.items():
                self._map_mission_variables(
                    mission_name,
                    mission_info,
                    agents,
                    missions,
                    output_json_functions,
                    tool_functions,
                    callback_functions,
                    output_pydantic_functions,
                )

        def _map_mission_variables(
            self,
            mission_name: str,
            mission_info: Dict[str, Any],
            agents: Dict[str, Callable],
            missions: Dict[str, Callable],
            output_json_functions: Dict[str, Callable],
            tool_functions: Dict[str, Callable],
            callback_functions: Dict[str, Callable],
            output_pydantic_functions: Dict[str, Callable],
        ) -> None:
            if context_list := mission_info.get("context"):
                self.missions_config[mission_name]["context"] = [
                    missions[context_mission_name]() for context_mission_name in context_list
                ]

            if tools := mission_info.get("tools"):
                self.missions_config[mission_name]["tools"] = [
                    tool_functions[tool]() for tool in tools
                ]

            if agent_name := mission_info.get("agent"):
                self.missions_config[mission_name]["agent"] = agents[agent_name]()

            if output_json := mission_info.get("output_json"):
                self.missions_config[mission_name]["output_json"] = output_json_functions[
                    output_json
                ]

            if output_pydantic := mission_info.get("output_pydantic"):
                self.missions_config[mission_name]["output_pydantic"] = (
                    output_pydantic_functions[output_pydantic]
                )

            if callbacks := mission_info.get("callbacks"):
                self.missions_config[mission_name]["callbacks"] = [
                    callback_functions[callback]() for callback in callbacks
                ]

    return cast(T, WrappedClass)
