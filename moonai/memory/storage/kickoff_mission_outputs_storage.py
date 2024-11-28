import json
import sqlite3
from typing import Any, Dict, List, Optional

from moonai.mission import Mission
from moonai.utilities import Printer
from moonai.utilities.squad_json_encoder import SquadJSONEncoder
from moonai.utilities.paths import db_storage_path


class KickoffMissionOutputsSQLiteStorage:
    """
    An updated SQLite storage class for kickoff mission outputs storage.
    """

    def __init__(
        self, db_path: str = f"{db_storage_path()}/latest_kickoff_mission_outputs.db"
    ) -> None:
        self.db_path = db_path
        self._printer: Printer = Printer()
        self._initialize_db()

    def _initialize_db(self):
        """
        Initializes the SQLite database and creates LTM table
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS latest_kickoff_mission_outputs (
                        mission_id TEXT PRIMARY KEY,
                        expected_output TEXT,
                        output JSON,
                        mission_index INTEGER,
                        inputs JSON,
                        was_replayed BOOLEAN,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                conn.commit()
        except sqlite3.Error as e:
            self._printer.print(
                content=f"SAVING KICKOFF MISSION OUTPUTS ERROR: An error occurred during database initialization: {e}",
                color="red",
            )

    def add(
        self,
        mission: Mission,
        output: Dict[str, Any],
        mission_index: int,
        was_replayed: bool = False,
        inputs: Dict[str, Any] = {},
    ):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                INSERT OR REPLACE INTO latest_kickoff_mission_outputs
                (mission_id, expected_output, output, mission_index, inputs, was_replayed)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                    (
                        str(mission.id),
                        mission.expected_output,
                        json.dumps(output, cls=SquadJSONEncoder),
                        mission_index,
                        json.dumps(inputs, cls=SquadJSONEncoder),
                        was_replayed,
                    ),
                )
                conn.commit()
        except sqlite3.Error as e:
            self._printer.print(
                content=f"SAVING KICKOFF MISSION OUTPUTS ERROR: An error occurred during database initialization: {e}",
                color="red",
            )

    def update(
        self,
        mission_index: int,
        **kwargs,
    ):
        """
        Updates an existing row in the latest_kickoff_mission_outputs table based on mission_index.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                fields = []
                values = []
                for key, value in kwargs.items():
                    fields.append(f"{key} = ?")
                    values.append(
                        json.dumps(value, cls=SquadJSONEncoder)
                        if isinstance(value, dict)
                        else value
                    )

                query = f"UPDATE latest_kickoff_mission_outputs SET {', '.join(fields)} WHERE mission_index = ?"  # nosec
                values.append(mission_index)

                cursor.execute(query, tuple(values))
                conn.commit()

                if cursor.rowcount == 0:
                    self._printer.print(
                        f"No row found with mission_index {mission_index}. No update performed.",
                        color="red",
                    )
        except sqlite3.Error as e:
            self._printer.print(f"UPDATE KICKOFF MISSION OUTPUTS ERROR: {e}", color="red")

    def load(self) -> Optional[List[Dict[str, Any]]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT *
                FROM latest_kickoff_mission_outputs
                ORDER BY mission_index
                """)

                rows = cursor.fetchall()
                results = []
                for row in rows:
                    result = {
                        "mission_id": row[0],
                        "expected_output": row[1],
                        "output": json.loads(row[2]),
                        "mission_index": row[3],
                        "inputs": json.loads(row[4]),
                        "was_replayed": row[5],
                        "timestamp": row[6],
                    }
                    results.append(result)

                return results

        except sqlite3.Error as e:
            self._printer.print(
                content=f"LOADING KICKOFF MISSION OUTPUTS ERROR: An error occurred while querying kickoff mission outputs: {e}",
                color="red",
            )
            return None

    def delete_all(self):
        """
        Deletes all rows from the latest_kickoff_mission_outputs table.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM latest_kickoff_mission_outputs")
                conn.commit()
        except sqlite3.Error as e:
            self._printer.print(
                content=f"ERROR: Failed to delete all kickoff mission outputs: {e}",
                color="red",
            )
