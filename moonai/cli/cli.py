from typing import Optional

import click
import pkg_resources

from moonai.cli.add_squad_to_flow import add_squad_to_flow
from moonai.cli.create_squad import create_squad
from moonai.cli.create_flow import create_flow
from moonai.cli.create_pipeline import create_pipeline
from moonai.memory.storage.kickoff_mission_outputs_storage import (
    KickoffMissionOutputsSQLiteStorage,
)

from .authentication.main import AuthenticationCommand
from .deploy.main import DeployCommand
from .evaluate_squad import evaluate_squad
from .install_squad import install_squad
from .kickoff_flow import kickoff_flow
from .plot_flow import plot_flow
from .replay_from_mission import replay_mission_command
from .reset_memories_command import reset_memories_command
from .run_squad import run_squad
from .tools.main import ToolCommand
from .train_squad import train_squad
from .update_squad import update_squad


@click.group()
def moonai():
    """Top-level command group for moonai."""


@moonai.devmand()
@click.argument("type", type=click.Choice(["squad", "pipeline", "flow"]))
@click.argument("name")
@click.option("--provider", type=str, help="The provider to use for the squad")
@click.option("--skip_provider", is_flag=True, help="Skip provider validation")
def create(type, name, provider, skip_provider=False):
    """Create a new squad, pipeline, or flow."""
    if type == "squad":
        create_squad(name, provider, skip_provider)
    elif type == "pipeline":
        create_pipeline(name)
    elif type == "flow":
        create_flow(name)
    else:
        click.secho(
            "Error: Invalid type. Must be 'squad', 'pipeline', or 'flow'.", fg="red"
        )


@moonai.devmand()
@click.option(
    "--tools", is_flag=True, help="Show the installed version of moonai tools"
)
def version(tools):
    """Show the installed version of moonai."""
    moonai_version = pkg_resources.get_distribution("moonai").version
    click.echo(f"moonai version: {moonai_version}")

    if tools:
        try:
            tools_version = pkg_resources.get_distribution("moonai_tools").version
            click.echo(f"moonai tools version: {tools_version}")
        except pkg_resources.DistributionNotFound:
            click.echo("moonai tools not installed")


@moonai.devmand()
@click.option(
    "-n",
    "--n_iterations",
    type=int,
    default=5,
    help="Number of iterations to train the squad",
)
@click.option(
    "-f",
    "--filename",
    type=str,
    default="trained_agents_data.pkl",
    help="Path to a custom file for training",
)
def train(n_iterations: int, filename: str):
    """Train the squad."""
    click.echo(f"Training the Squad for {n_iterations} iterations")
    train_squad(n_iterations, filename)


@moonai.devmand()
@click.option(
    "-t",
    "--mission_id",
    type=str,
    help="Replay the squad from this mission ID, including all subsequent missions.",
)
def replay(mission_id: str) -> None:
    """
    Replay the squad execution from a specific mission.

    Args:
        mission_id (str): The ID of the mission to replay from.
    """
    try:
        click.echo(f"Replaying the squad from mission {mission_id}")
        replay_mission_command(mission_id)
    except Exception as e:
        click.echo(f"An error occurred while replaying: {e}", err=True)


@moonai.devmand()
def log_missions_outputs() -> None:
    """
    Retrieve your latest squad.kickoff() mission outputs.
    """
    try:
        storage = KickoffMissionOutputsSQLiteStorage()
        missions = storage.load()

        if not missions:
            click.echo(
                "No mission outputs found. Only squad kickoff mission outputs are logged."
            )
            return

        for index, mission in enumerate(missions, 1):
            click.echo(f"Mission {index}: {mission['mission_id']}")
            click.echo(f"Description: {mission['expected_output']}")
            click.echo("------")

    except Exception as e:
        click.echo(f"An error occurred while logging mission outputs: {e}", err=True)


@moonai.devmand()
@click.option("-l", "--long", is_flag=True, help="Reset LONG TERM memory")
@click.option("-s", "--short", is_flag=True, help="Reset SHORT TERM memory")
@click.option("-e", "--entities", is_flag=True, help="Reset ENTITIES memory")
@click.option("-kn", "--knowledge", is_flag=True, help="Reset KNOWLEDGE storage")
@click.option(
    "-k",
    "--kickoff-outputs",
    is_flag=True,
    help="Reset LATEST KICKOFF MISSION OUTPUTS",
)
@click.option("-a", "--all", is_flag=True, help="Reset ALL memories")
def reset_memories(
    long: bool,
    short: bool,
    entities: bool,
    knowledge: bool,
    kickoff_outputs: bool,
    all: bool,
) -> None:
    """
    Reset the squad memories (long, short, entity, latest_squad_kickoff_ouputs). This will delete all the data saved.
    """
    try:
        if not all and not (long or short or entities or knowledge or kickoff_outputs):
            click.echo(
                "Please specify at least one memory type to reset using the appropriate flags."
            )
            return
        reset_memories_command(long, short, entities, knowledge, kickoff_outputs, all)
    except Exception as e:
        click.echo(f"An error occurred while resetting memories: {e}", err=True)


@moonai.devmand()
@click.option(
    "-n",
    "--n_iterations",
    type=int,
    default=3,
    help="Number of iterations to Test the squad",
)
@click.option(
    "-m",
    "--model",
    type=str,
    default="gpt-4o-mini",
    help="LLM Model to run the tests on the Squad. For now only accepting only OpenAI models.",
)
def test(n_iterations: int, model: str):
    """Test the squad and evaluate the results."""
    click.echo(f"Testing the squad for {n_iterations} iterations with model {model}")
    evaluate_squad(n_iterations, model)


@moonai.devmand(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.pass_context
def install(context):
    """Install the Squad."""
    install_squad(context.args)


@moonai.devmand()
def run():
    """Run the Squad."""
    click.echo("Running the Squad")
    run_squad()


@moonai.devmand()
def update():
    """Update the pyproject.toml of the Squad project to use uv."""
    update_squad()


@moonai.devmand()
def signup():
    """Sign Up/Login to moonai+."""
    AuthenticationCommand().signup()


@moonai.devmand()
def login():
    """Sign Up/Login to moonai+."""
    AuthenticationCommand().signup()


# DEPLOY moonai+ COMMANDS
@moonai.group()
def deploy():
    """Deploy the Squad CLI group."""
    pass


@moonai.group()
def tool():
    """Tool Repository related commands."""
    pass


@deploy.command(name="create")
@click.option("-y", "--yes", is_flag=True, help="Skip the confirmation prompt")
def deploy_create(yes: bool):
    """Create a Squad deployment."""
    deploy_cmd = DeployCommand()
    deploy_cmd.create_squad(yes)


@deploy.command(name="list")
def deploy_list():
    """List all deployments."""
    deploy_cmd = DeployCommand()
    deploy_cmd.list_squads()


@deploy.command(name="push")
@click.option("-u", "--uuid", type=str, help="Squad UUID parameter")
def deploy_push(uuid: Optional[str]):
    """Deploy the Squad."""
    deploy_cmd = DeployCommand()
    deploy_cmd.deploy(uuid=uuid)


@deploy.command(name="status")
@click.option("-u", "--uuid", type=str, help="Squad UUID parameter")
def deply_status(uuid: Optional[str]):
    """Get the status of a deployment."""
    deploy_cmd = DeployCommand()
    deploy_cmd.get_squad_status(uuid=uuid)


@deploy.command(name="logs")
@click.option("-u", "--uuid", type=str, help="Squad UUID parameter")
def deploy_logs(uuid: Optional[str]):
    """Get the logs of a deployment."""
    deploy_cmd = DeployCommand()
    deploy_cmd.get_squad_logs(uuid=uuid)


@deploy.command(name="remove")
@click.option("-u", "--uuid", type=str, help="Squad UUID parameter")
def deploy_remove(uuid: Optional[str]):
    """Remove a deployment."""
    deploy_cmd = DeployCommand()
    deploy_cmd.remove_squad(uuid=uuid)


@tool.command(name="create")
@click.argument("handle")
def tool_create(handle: str):
    tool_cmd = ToolCommand()
    tool_cmd.create(handle)


@tool.command(name="install")
@click.argument("handle")
def tool_install(handle: str):
    tool_cmd = ToolCommand()
    tool_cmd.login()
    tool_cmd.install(handle)


@tool.command(name="publish")
@click.option(
    "--force",
    is_flag=True,
    show_default=True,
    default=False,
    help="Bypasses Git remote validations",
)
@click.option("--public", "is_public", flag_value=True, default=False)
@click.option("--private", "is_public", flag_value=False)
def tool_publish(is_public: bool, force: bool):
    tool_cmd = ToolCommand()
    tool_cmd.login()
    tool_cmd.publish(is_public, force)


@moonai.group()
def flow():
    """Flow related commands."""
    pass


@flow.command(name="kickoff")
def flow_run():
    """Kickoff the Flow."""
    click.echo("Running the Flow")
    kickoff_flow()


@flow.command(name="plot")
def flow_plot():
    """Plot the Flow."""
    click.echo("Plotting the Flow")
    plot_flow()


@flow.command(name="add-squad")
@click.argument("squad_name")
def flow_add_squad(squad_name):
    """Add a squad to an existing flow."""
    click.echo(f"Adding squad {squad_name} to the flow")
    add_squad_to_flow(squad_name)


if __name__ == "__main__":
    moonai()
