from pathlib import Path

import click

from moonai.cli.utils import copy_template


def add_squad_to_flow(squad_name: str) -> None:
    """Add a new squad to the current flow."""
    # Check if pyproject.toml exists in the current directory
    if not Path("pyproject.toml").exists():
        print("This command must be run from the root of a flow project.")
        raise click.ClickException(
            "This command must be run from the root of a flow project."
        )

    # Determine the flow folder based on the current directory
    flow_folder = Path.cwd()
    squads_folder = flow_folder / "src" / flow_folder.name / "squads"

    if not squads_folder.exists():
        print("Squads folder does not exist in the current flow.")
        raise click.ClickException("Squads folder does not exist in the current flow.")

    # Create the squad within the flow's squads directory
    create_embedded_squad(squad_name, parent_folder=squads_folder)

    click.echo(
        f"Squad {squad_name} added to the current flow successfully!",
    )


def create_embedded_squad(squad_name: str, parent_folder: Path) -> None:
    """Create a new squad within an existing flow project."""
    folder_name = squad_name.replace(" ", "_").replace("-", "_").lower()
    class_name = squad_name.replace("_", " ").replace("-", " ").title().replace(" ", "")

    squad_folder = parent_folder / folder_name

    if squad_folder.exists():
        if not click.confirm(
            f"Squad {folder_name} already exists. Do you want to override it?"
        ):
            click.secho("Operation cancelled.", fg="yellow")
            return
        click.secho(f"Overriding squad {folder_name}...", fg="green", bold=True)
    else:
        click.secho(f"Creating squad {folder_name}...", fg="green", bold=True)
        squad_folder.mkdir(parents=True)

    # Create config and squad.py files
    config_folder = squad_folder / "config"
    config_folder.mkdir(exist_ok=True)

    templates_dir = Path(__file__).parent / "templates" / "squad"
    config_template_files = ["agents.yaml", "missions.yaml"]
    squad_template_file = f"{folder_name}.py"  # Updated file name

    for file_name in config_template_files:
        src_file = templates_dir / "config" / file_name
        dst_file = config_folder / file_name
        copy_template(src_file, dst_file, squad_name, class_name, folder_name)

    src_file = templates_dir / "squad.py"
    dst_file = squad_folder / squad_template_file
    copy_template(src_file, dst_file, squad_name, class_name, folder_name)

    click.secho(
        f"Squad {squad_name} added to the flow successfully!", fg="green", bold=True
    )
