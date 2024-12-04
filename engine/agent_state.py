from dataclasses import dataclass
from turtle import RawTurtle
from typing import Tuple


@dataclass
class AgentState:
    turtle: RawTurtle
    position: Tuple[float, float]
    heading: float
    speed: float
    selected: bool = False
    moving_forward: bool = False
    moving_backward: bool = False
    turning_left: bool = False
    turning_right: bool = False