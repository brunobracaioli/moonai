import subprocess

import click
from packaging import version

from moonai.cli.utils import get_moonai_version, read_toml


def run_squad() -> None:
    """
    Run the squad by running a command in the UV environment.
    """
    command = ["uv", "run", "run_squad"]
    moonai_version = get_moonai_version()
    min_required_version = "0.71.0"

    pyproject_data = read_toml()

    if pyproject_data.get("tool", {}).get("poetry") and (
        version.parse(moonai_version) < version.parse(min_required_version)
    ):
        click.secho(
            f"You are running an older version of moonai ({moonai_version}) that uses poetry pyproject.toml. "
            f"Please run `moonai update` to update your pyproject.toml to use uv.",
            fg="red",
        )

    try:
        subprocess.run(command, capture_output=False, text=True, check=True)

    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred while running the squad: {e}", err=True)
        click.echo(e.output, err=True, nl=True)

        if pyproject_data.get("tool", {}).get("poetry"):
            click.secho(
                "It's possible that you are using an old version of moonai that uses poetry, please run `moonai update` to update your pyproject.toml to use uv.",
                fg="yellow",
            )

    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
