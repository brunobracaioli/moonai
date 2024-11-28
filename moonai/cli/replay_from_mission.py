import subprocess

import click


def replay_mission_command(mission_id: str) -> None:
    """
    Replay the squad execution from a specific mission.

    Args:
      mission_id (str): The ID of the mission to replay from.
    """
    command = ["uv", "run", "replay", mission_id]

    try:
        result = subprocess.run(command, capture_output=False, text=True, check=True)
        if result.stderr:
            click.echo(result.stderr, err=True)

    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred while replaying the mission: {e}", err=True)
        click.echo(e.output, err=True)

    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
