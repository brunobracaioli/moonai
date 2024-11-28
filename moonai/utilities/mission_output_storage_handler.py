from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional, List
from moonai.memory.storage.kickoff_mission_outputs_storage import (
    KickoffMissionOutputsSQLiteStorage,
)
from moonai.mission import Mission


class ExecutionLog(BaseModel):
    mission_id: str
    expected_output: Optional[str] = None
    output: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    mission_index: int
    inputs: Dict[str, Any] = Field(default_factory=dict)
    was_replayed: bool = False

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class MissionOutputStorageHandler:
    def __init__(self) -> None:
        self.storage = KickoffMissionOutputsSQLiteStorage()

    def update(self, mission_index: int, log: Dict[str, Any]):
        saved_outputs = self.load()
        if saved_outputs is None:
            raise ValueError("Logs cannot be None")

        if log.get("was_replayed", False):
            replayed = {
                "mission_id": str(log["mission"].id),
                "expected_output": log["mission"].expected_output,
                "output": log["output"],
                "was_replayed": log["was_replayed"],
                "inputs": log["inputs"],
            }
            self.storage.update(
                mission_index,
                **replayed,
            )
        else:
            self.storage.add(**log)

    def add(
        self,
        mission: Mission,
        output: Dict[str, Any],
        mission_index: int,
        inputs: Dict[str, Any] = {},
        was_replayed: bool = False,
    ):
        self.storage.add(mission, output, mission_index, was_replayed, inputs)

    def reset(self):
        self.storage.delete_all()

    def load(self) -> Optional[List[Dict[str, Any]]]:
        return self.storage.load()
