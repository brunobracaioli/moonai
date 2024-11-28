#!/usr/bin/env python
import sys
import warnings

from {{folder_name}}.squad import {{squad_name}}

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# squad locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any missions and agents information

def run():
    """
    Run the squad.
    """
    inputs = {
        'topic': 'AI LLMs'
    }
    {{squad_name}}().squad().kickoff(inputs=inputs)


def train():
    """
    Train the squad for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        {{squad_name}}().squad().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the squad: {e}")

def replay():
    """
    Replay the squad execution from a specific mission.
    """
    try:
        {{squad_name}}().squad().replay(mission_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the squad: {e}")

def test():
    """
    Test the squad execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        {{squad_name}}().squad().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the squad: {e}")
