from typing import Any, Dict, List

from moonai.memory.long_term.long_term_memory_item import LongTermMemoryItem
from moonai.memory.memory import Memory
from moonai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage


class LongTermMemory(Memory):
    """
    LongTermMemory class for managing cross runs data related to overall squad's
    execution and performance.
    Inherits from the Memory class and utilizes an instance of a class that
    adheres to the Storage for data storage, specifically working with
    LongTermMemoryItem instances.
    """

    def __init__(self, storage=None):
        storage = storage if storage else LTMSQLiteStorage()
        super().__init__(storage)

    def save(self, item: LongTermMemoryItem) -> None:  # type: ignore # BUG?: Signature of "save" incompatible with supertype "Memory"
        metadata = item.metadata
        metadata.update({"agent": item.agent, "expected_output": item.expected_output})
        self.storage.save(  # type: ignore # BUG?: Unexpected keyword argument "mission_description","score","datetime" for "save" of "Storage"
            mission_description=item.mission,
            score=metadata["quality"],
            metadata=metadata,
            datetime=item.datetime,
        )

    def search(self, mission: str, latest_n: int = 3) -> List[Dict[str, Any]]:  # type: ignore # signature of "search" incompatible with supertype "Memory"
        return self.storage.load(mission, latest_n)  # type: ignore # BUG?: "Storage" has no attribute "load"

    def reset(self) -> None:
        self.storage.reset()
