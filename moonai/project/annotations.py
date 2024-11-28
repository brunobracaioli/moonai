from functools import wraps
from typing import Callable

from moonai import Squad
from moonai.project.utils import memoize


def before_kickoff(func):
    func.is_before_kickoff = True
    return func


def after_kickoff(func):
    func.is_after_kickoff = True
    return func


def mission(func):
    func.is_mission = True

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not result.name:
            result.name = func.__name__
        return result

    return memoize(wrapper)


def agent(func):
    func.is_agent = True
    func = memoize(func)
    return func


def llm(func):
    func.is_llm = True
    func = memoize(func)
    return func


def output_json(cls):
    cls.is_output_json = True
    return cls


def output_pydantic(cls):
    cls.is_output_pydantic = True
    return cls


def tool(func):
    func.is_tool = True
    return memoize(func)


def callback(func):
    func.is_callback = True
    return memoize(func)


def cache_handler(func):
    func.is_cache_handler = True
    return memoize(func)


def stage(func):
    func.is_stage = True
    return memoize(func)


def router(func):
    func.is_router = True
    return memoize(func)


def pipeline(func):
    func.is_pipeline = True
    return memoize(func)


def squad(func) -> Callable[..., Squad]:
    def wrapper(self, *args, **kwargs) -> Squad:
        instantiated_missions = []
        instantiated_agents = []
        agent_roles = set()

        # Use the preserved mission and agent information
        missions = self._original_missions.items()
        agents = self._original_agents.items()

        # Instantiate missions in order
        for mission_name, mission_method in missions:
            mission_instance = mission_method(self)
            instantiated_missions.append(mission_instance)
            agent_instance = getattr(mission_instance, "agent", None)
            if agent_instance and agent_instance.role not in agent_roles:
                instantiated_agents.append(agent_instance)
                agent_roles.add(agent_instance.role)

        # Instantiate agents not included by missions
        for agent_name, agent_method in agents:
            agent_instance = agent_method(self)
            if agent_instance.role not in agent_roles:
                instantiated_agents.append(agent_instance)
                agent_roles.add(agent_instance.role)

        self.agents = instantiated_agents
        self.missions = instantiated_missions

        squad = func(self, *args, **kwargs)

        def callback_wrapper(callback, instance):
            def wrapper(*args, **kwargs):
                return callback(instance, *args, **kwargs)

            return wrapper

        for _, callback in self._before_kickoff.items():
            squad.before_kickoff_callbacks.append(callback_wrapper(callback, self))
        for _, callback in self._after_kickoff.items():
            squad.after_kickoff_callbacks.append(callback_wrapper(callback, self))

        return squad

    return memoize(wrapper)
