# moonai\telemetry\telemetry.py

from __future__ import annotations

import asyncio
import json
import os
import platform
import warnings
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Optional


@contextmanager
def suppress_warnings():
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        yield


with suppress_warnings():
    import pkg_resources


from opentelemetry import trace  # noqa: E402
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter # noqa: E402
from opentelemetry.sdk.resources import SERVICE_NAME, Resource  # noqa: E402
from opentelemetry.sdk.trace import TracerProvider  # noqa: E402
from opentelemetry.sdk.trace.export import BatchSpanProcessor  # noqa: E402
from opentelemetry.trace import Span, Status, StatusCode  # noqa: E402

if TYPE_CHECKING:
    from moonai.squad import Squad
    from moonai.mission import Mission


class Telemetry:
    """A class to handle anonymous telemetry for the moonai package.

    The data being collected is for development purpose, all data is anonymous.

    There is NO data being collected on the prompts, missions descriptions
    agents backstories or goals nor responses or any data that is being
    processed by the agents, nor any secrets and env vars.

    Users can opt-in to sharing more complete data using the `share_squad`
    attribute in the Squad class.
    """

    def __init__(self):
        self.ready = False
        self.trace_set = False

        if os.getenv("OTEL_SDK_DISABLED", "false").lower() == "true":
            return

        try:
            telemetry_endpoint = "https://telemetry.moonai.dev:4319"
            self.resource = Resource(
                attributes={SERVICE_NAME: "moonai-telemetry"},
            )
            with suppress_warnings():
                self.provider = TracerProvider(resource=self.resource)

            processor = BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=f"{telemetry_endpoint}/v1/traces",
                    timeout=30,
                )
            )

            self.provider.add_span_processor(processor)
            self.ready = True
        except Exception as e:
            if isinstance(
                e,
                (SystemExit, KeyboardInterrupt, GeneratorExit, asyncio.CancelledError),
            ):
                raise  # Re-raise the exception to not interfere with system signals
            self.ready = False

    def set_tracer(self):
        if self.ready and not self.trace_set:
            try:
                with suppress_warnings():
                    trace.set_tracer_provider(self.provider)
                    self.trace_set = True
            except Exception:
                self.ready = False
                self.trace_set = False

    def _safe_telemetry_operation(self, operation):
        if not self.ready:
            return
        try:
            operation()
        except Exception:
            pass

    def squad_creation(self, squad: Squad, inputs: dict[str, Any] | None):
        """Records the creation of a squad."""

        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Squad Created")
            self._add_attribute(
                span,
                "moonai_version",
                pkg_resources.get_distribution("moonai").version,
            )
            self._add_attribute(span, "python_version", platform.python_version())
            self._add_attribute(span, "squad_key", squad.key)
            self._add_attribute(span, "squad_id", str(squad.id))
            self._add_attribute(span, "squad_process", squad.process)
            self._add_attribute(span, "squad_memory", squad.memory)
            self._add_attribute(span, "squad_number_of_missions", len(squad.missions))
            self._add_attribute(span, "squad_number_of_agents", len(squad.agents))
            if squad.share_squad:
                self._add_attribute(
                    span,
                    "squad_agents",
                    json.dumps(
                        [
                            {
                                "key": agent.key,
                                "id": str(agent.id),
                                "role": agent.role,
                                "goal": agent.goal,
                                "backstory": agent.backstory,
                                "verbose?": agent.verbose,
                                "max_iter": agent.max_iter,
                                "max_rpm": agent.max_rpm,
                                "i18n": agent.i18n.prompt_file,
                                "function_calling_llm": (
                                    agent.function_calling_llm.model
                                    if agent.function_calling_llm
                                    else ""
                                ),
                                "llm": agent.llm.model,
                                "delegation_enabled?": agent.allow_delegation,
                                "allow_code_execution?": agent.allow_code_execution,
                                "max_retry_limit": agent.max_retry_limit,
                                "tools_names": [
                                    tool.name.casefold() for tool in agent.tools or []
                                ],
                            }
                            for agent in squad.agents
                        ]
                    ),
                )
                self._add_attribute(
                    span,
                    "squad_missions",
                    json.dumps(
                        [
                            {
                                "key": mission.key,
                                "id": str(mission.id),
                                "description": mission.description,
                                "expected_output": mission.expected_output,
                                "async_execution?": mission.async_execution,
                                "human_input?": mission.human_input,
                                "agent_role": (
                                    mission.agent.role if mission.agent else "None"
                                ),
                                "agent_key": mission.agent.key if mission.agent else None,
                                "context": (
                                    [mission.description for mission in mission.context]
                                    if mission.context
                                    else None
                                ),
                                "tools_names": [
                                    tool.name.casefold() for tool in mission.tools or []
                                ],
                            }
                            for mission in squad.missions
                        ]
                    ),
                )
                self._add_attribute(span, "platform", platform.platform())
                self._add_attribute(span, "platform_release", platform.release())
                self._add_attribute(span, "platform_system", platform.system())
                self._add_attribute(span, "platform_version", platform.version())
                self._add_attribute(span, "cpus", os.cpu_count())
                self._add_attribute(
                    span, "squad_inputs", json.dumps(inputs) if inputs else None
                )
            else:
                self._add_attribute(
                    span,
                    "squad_agents",
                    json.dumps(
                        [
                            {
                                "key": agent.key,
                                "id": str(agent.id),
                                "role": agent.role,
                                "verbose?": agent.verbose,
                                "max_iter": agent.max_iter,
                                "max_rpm": agent.max_rpm,
                                "function_calling_llm": (
                                    agent.function_calling_llm.model
                                    if agent.function_calling_llm
                                    else ""
                                ),
                                "llm": agent.llm.model,
                                "delegation_enabled?": agent.allow_delegation,
                                "allow_code_execution?": agent.allow_code_execution,
                                "max_retry_limit": agent.max_retry_limit,
                                "tools_names": [
                                    tool.name.casefold() for tool in agent.tools or []
                                ],
                            }
                            for agent in squad.agents
                        ]
                    ),
                )
                self._add_attribute(
                    span,
                    "squad_missions",
                    json.dumps(
                        [
                            {
                                "key": mission.key,
                                "id": str(mission.id),
                                "async_execution?": mission.async_execution,
                                "human_input?": mission.human_input,
                                "agent_role": (
                                    mission.agent.role if mission.agent else "None"
                                ),
                                "agent_key": mission.agent.key if mission.agent else None,
                                "tools_names": [
                                    tool.name.casefold() for tool in mission.tools or []
                                ],
                            }
                            for mission in squad.missions
                        ]
                    ),
                )
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def mission_started(self, squad: Squad, mission: Mission) -> Span | None:
        """Records mission started in a squad."""

        def operation():
            tracer = trace.get_tracer("moonai.telemetry")

            created_span = tracer.start_span("Mission Created")

            self._add_attribute(created_span, "squad_key", squad.key)
            self._add_attribute(created_span, "squad_id", str(squad.id))
            self._add_attribute(created_span, "mission_key", mission.key)
            self._add_attribute(created_span, "mission_id", str(mission.id))

            if squad.share_squad:
                self._add_attribute(
                    created_span, "formatted_description", mission.description
                )
                self._add_attribute(
                    created_span, "formatted_expected_output", mission.expected_output
                )

            created_span.set_status(Status(StatusCode.OK))
            created_span.end()

            span = tracer.start_span("Mission Execution")

            self._add_attribute(span, "squad_key", squad.key)
            self._add_attribute(span, "squad_id", str(squad.id))
            self._add_attribute(span, "mission_key", mission.key)
            self._add_attribute(span, "mission_id", str(mission.id))

            if squad.share_squad:
                self._add_attribute(span, "formatted_description", mission.description)
                self._add_attribute(
                    span, "formatted_expected_output", mission.expected_output
                )

            return span

        return self._safe_telemetry_operation(operation)

    def mission_ended(self, span: Span, mission: Mission, squad: Squad):
        """Records mission execution in a squad."""

        def operation():
            if squad.share_squad:
                self._add_attribute(
                    span,
                    "mission_output",
                    mission.output.raw if mission.output else "",
                )

            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def tool_repeated_usage(self, llm: Any, tool_name: str, attempts: int):
        """Records the repeated usage 'error' of a tool by an agent."""

        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Tool Repeated Usage")
            self._add_attribute(
                span,
                "moonai_version",
                pkg_resources.get_distribution("moonai").version,
            )
            self._add_attribute(span, "tool_name", tool_name)
            self._add_attribute(span, "attempts", attempts)
            if llm:
                self._add_attribute(span, "llm", llm.model)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def tool_usage(self, llm: Any, tool_name: str, attempts: int):
        """Records the usage of a tool by an agent."""

        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Tool Usage")
            self._add_attribute(
                span,
                "moonai_version",
                pkg_resources.get_distribution("moonai").version,
            )
            self._add_attribute(span, "tool_name", tool_name)
            self._add_attribute(span, "attempts", attempts)
            if llm:
                self._add_attribute(span, "llm", llm.model)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def tool_usage_error(self, llm: Any):
        """Records the usage of a tool by an agent."""

        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Tool Usage Error")
            self._add_attribute(
                span,
                "moonai_version",
                pkg_resources.get_distribution("moonai").version,
            )
            if llm:
                self._add_attribute(span, "llm", llm.model)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def individual_test_result_span(
        self, squad: Squad, quality: float, exec_time: int, model_name: str
    ):
        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Squad Individual Test Result")

            self._add_attribute(
                span,
                "moonai_version",
                pkg_resources.get_distribution("moonai").version,
            )
            self._add_attribute(span, "squad_key", squad.key)
            self._add_attribute(span, "squad_id", str(squad.id))
            self._add_attribute(span, "quality", str(quality))
            self._add_attribute(span, "exec_time", str(exec_time))
            self._add_attribute(span, "model_name", model_name)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def test_execution_span(
        self,
        squad: Squad,
        iterations: int,
        inputs: dict[str, Any] | None,
        model_name: str,
    ):
        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Squad Test Execution")

            self._add_attribute(
                span,
                "moonai_version",
                pkg_resources.get_distribution("moonai").version,
            )
            self._add_attribute(span, "squad_key", squad.key)
            self._add_attribute(span, "squad_id", str(squad.id))
            self._add_attribute(span, "iterations", str(iterations))
            self._add_attribute(span, "model_name", model_name)

            if squad.share_squad:
                self._add_attribute(
                    span, "inputs", json.dumps(inputs) if inputs else None
                )

            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def deploy_signup_error_span(self):
        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Deploy Signup Error")
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def start_deployment_span(self, uuid: Optional[str] = None):
        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Start Deployment")
            if uuid:
                self._add_attribute(span, "uuid", uuid)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def create_squad_deployment_span(self):
        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Create Squad Deployment")
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def get_squad_logs_span(self, uuid: Optional[str], log_type: str = "deployment"):
        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Get Squad Logs")
            self._add_attribute(span, "log_type", log_type)
            if uuid:
                self._add_attribute(span, "uuid", uuid)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def remove_squad_span(self, uuid: Optional[str] = None):
        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Remove Squad")
            if uuid:
                self._add_attribute(span, "uuid", uuid)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def squad_execution_span(self, squad: Squad, inputs: dict[str, Any] | None):
        """Records the complete execution of a squad.
        This is only collected if the user has opted-in to share the squad.
        """
        self.squad_creation(squad, inputs)

        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Squad Execution")
            self._add_attribute(
                span,
                "moonai_version",
                pkg_resources.get_distribution("moonai").version,
            )
            self._add_attribute(span, "squad_key", squad.key)
            self._add_attribute(span, "squad_id", str(squad.id))
            self._add_attribute(
                span, "squad_inputs", json.dumps(inputs) if inputs else None
            )
            self._add_attribute(
                span,
                "squad_agents",
                json.dumps(
                    [
                        {
                            "key": agent.key,
                            "id": str(agent.id),
                            "role": agent.role,
                            "goal": agent.goal,
                            "backstory": agent.backstory,
                            "verbose?": agent.verbose,
                            "max_iter": agent.max_iter,
                            "max_rpm": agent.max_rpm,
                            "i18n": agent.i18n.prompt_file,
                            "llm": agent.llm.model,
                            "delegation_enabled?": agent.allow_delegation,
                            "tools_names": [
                                tool.name.casefold() for tool in agent.tools or []
                            ],
                        }
                        for agent in squad.agents
                    ]
                ),
            )
            self._add_attribute(
                span,
                "squad_missions",
                json.dumps(
                    [
                        {
                            "id": str(mission.id),
                            "description": mission.description,
                            "expected_output": mission.expected_output,
                            "async_execution?": mission.async_execution,
                            "human_input?": mission.human_input,
                            "agent_role": mission.agent.role if mission.agent else "None",
                            "agent_key": mission.agent.key if mission.agent else None,
                            "context": (
                                [mission.description for mission in mission.context]
                                if mission.context
                                else None
                            ),
                            "tools_names": [
                                tool.name.casefold() for tool in mission.tools or []
                            ],
                        }
                        for mission in squad.missions
                    ]
                ),
            )
            return span

        if squad.share_squad:
            return self._safe_telemetry_operation(operation)
        return None

    def end_squad(self, squad, final_string_output):
        def operation():
            self._add_attribute(
                squad._execution_span,
                "moonai_version",
                pkg_resources.get_distribution("moonai").version,
            )
            self._add_attribute(
                squad._execution_span, "squad_output", final_string_output
            )
            self._add_attribute(
                squad._execution_span,
                "squad_missions_output",
                json.dumps(
                    [
                        {
                            "id": str(mission.id),
                            "description": mission.description,
                            "output": mission.output.raw_output,
                        }
                        for mission in squad.missions
                    ]
                ),
            )
            squad._execution_span.set_status(Status(StatusCode.OK))
            squad._execution_span.end()

        if squad.share_squad:
            self._safe_telemetry_operation(operation)

    def _add_attribute(self, span, key, value):
        """Add an attribute to a span."""

        def operation():
            return span.set_attribute(key, value)

        self._safe_telemetry_operation(operation)

    def flow_creation_span(self, flow_name: str):
        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Flow Creation")
            self._add_attribute(span, "flow_name", flow_name)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def flow_plotting_span(self, flow_name: str, node_names: list[str]):
        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Flow Plotting")
            self._add_attribute(span, "flow_name", flow_name)
            self._add_attribute(span, "node_names", json.dumps(node_names))
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def flow_execution_span(self, flow_name: str, node_names: list[str]):
        def operation():
            tracer = trace.get_tracer("moonai.telemetry")
            span = tracer.start_span("Flow Execution")
            self._add_attribute(span, "flow_name", flow_name)
            self._add_attribute(span, "node_names", json.dumps(node_names))
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)
