from enum import Enum


class Process(str, Enum):
    """
    Class representing the different processes that can be used to tackle missions
    """

    sequential = "sequential"
    hierarchical = "hierarchical"
    # TODO: consensual = 'consensual'
