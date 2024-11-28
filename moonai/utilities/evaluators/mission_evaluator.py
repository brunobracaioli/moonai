import os
from typing import List

from pydantic import BaseModel, Field

from moonai.utilities import Converter
from moonai.utilities.pydantic_schema_parser import PydanticSchemaParser


def mock_agent_ops_provider():
    def track_agent(*args, **kwargs):
        def noop(f):
            return f

        return noop

    return track_agent


agentops = None

if os.environ.get("AGENTOPS_API_KEY"):
    try:
        from agentops import track_agent
    except ImportError:
        track_agent = mock_agent_ops_provider()
else:
    track_agent = mock_agent_ops_provider()


class Entity(BaseModel):
    name: str = Field(description="The name of the entity.")
    type: str = Field(description="The type of the entity.")
    description: str = Field(description="Description of the entity.")
    relationships: List[str] = Field(description="Relationships of the entity.")


class MissionEvaluation(BaseModel):
    suggestions: List[str] = Field(
        description="Suggestions to improve future similar missions."
    )
    quality: float = Field(
        description="A score from 0 to 10 evaluating on completion, quality, and overall performance, all taking into account the mission description, expected output, and the result of the mission."
    )
    entities: List[Entity] = Field(
        description="Entities extracted from the mission output."
    )


class TrainingMissionEvaluation(BaseModel):
    suggestions: List[str] = Field(
        description="List of clear, actionable instructions derived from the Human Feedbacks to enhance the Agent's performance. Analyze the differences between Initial Outputs and Improved Outputs to generate specific action items for future missions. Ensure all key and specific points from the human feedback are incorporated into these instructions."
    )
    quality: float = Field(
        description="A score from 0 to 10 evaluating on completion, quality, and overall performance from the improved output to the initial output based on the human feedback."
    )
    final_summary: str = Field(
        description="A step by step action items to improve the next Agent based on the human-feedback and improved output."
    )


@track_agent(name="Mission Evaluator")
class MissionEvaluator:
    def __init__(self, original_agent):
        self.llm = original_agent.llm

    def evaluate(self, mission, output) -> MissionEvaluation:
        evaluation_query = (
            f"Assess the quality of the mission completed based on the description, expected output, and actual results.\n\n"
            f"Mission Description:\n{mission.description}\n\n"
            f"Expected Output:\n{mission.expected_output}\n\n"
            f"Actual Output:\n{output}\n\n"
            "Please provide:\n"
            "- Bullet points suggestions to improve future similar missions\n"
            "- A score from 0 to 10 evaluating on completion, quality, and overall performance"
            "- Entities extracted from the mission output, if any, their type, description, and relationships"
        )

        instructions = "Convert all responses into valid JSON output."

        if not self.llm.supports_function_calling():
            model_schema = PydanticSchemaParser(model=MissionEvaluation).get_schema()
            instructions = f"{instructions}\n\nReturn only valid JSON with the following schema:\n```json\n{model_schema}\n```"

        converter = Converter(
            llm=self.llm,
            text=evaluation_query,
            model=MissionEvaluation,
            instructions=instructions,
        )

        return converter.to_pydantic()

    def evaluate_training_data(
        self, training_data: dict, agent_id: str
    ) -> TrainingMissionEvaluation:
        """
        Evaluate the training data based on the llm output, human feedback, and improved output.

        Parameters:
            - training_data (dict): The training data to be evaluated.
            - agent_id (str): The ID of the agent.
        """

        output_training_data = training_data[agent_id]

        final_aggregated_data = ""
        for _, data in output_training_data.items():
            final_aggregated_data += (
                f"Initial Output:\n{data['initial_output']}\n\n"
                f"Human Feedback:\n{data['human_feedback']}\n\n"
                f"Improved Output:\n{data['improved_output']}\n\n"
            )

        evaluation_query = (
            "Assess the quality of the training data based on the llm output, human feedback , and llm output improved result.\n\n"
            f"{final_aggregated_data}"
            "Please provide:\n"
            "- Provide a list of clear, actionable instructions derived from the Human Feedbacks to enhance the Agent's performance. Analyze the differences between Initial Outputs and Improved Outputs to generate specific action items for future missions. Ensure all key and specificpoints from the human feedback are incorporated into these instructions.\n"
            "- A score from 0 to 10 evaluating on completion, quality, and overall performance from the improved output to the initial output based on the human feedback\n"
        )
        instructions = "I'm gonna convert this raw text into valid JSON."

        if not self.llm.supports_function_calling():
            model_schema = PydanticSchemaParser(
                model=TrainingMissionEvaluation
            ).get_schema()
            instructions = f"{instructions}\n\nThe json should have the following structure, with the following keys:\n{model_schema}"

        converter = Converter(
            llm=self.llm,
            text=evaluation_query,
            model=TrainingMissionEvaluation,
            instructions=instructions,
        )

        pydantic_result = converter.to_pydantic()
        return pydantic_result
