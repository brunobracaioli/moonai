from typing import List

from moonai.mission import Mission
from moonai.missions.mission_output import MissionOutput


def aggregate_raw_outputs_from_mission_outputs(mission_outputs: List[MissionOutput]) -> str:
    """Generate string context from the mission outputs."""
    dividers = "\n\n----------\n\n"

    # Join mission outputs with dividers
    context = dividers.join(output.raw for output in mission_outputs)
    return context


def aggregate_raw_outputs_from_missions(missions: List[Mission]) -> str:
    """Generate string context from the missions."""
    mission_outputs = [mission.output for mission in missions if mission.output is not None]

    return aggregate_raw_outputs_from_mission_outputs(mission_outputs)
