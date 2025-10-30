from pydantic import BaseModel, PositiveInt
from typing import Literal


class VolumeRequest(BaseModel):
    current_sets: PositiveInt
    training_level: Literal["beginner", "intermediate", "advanced"]
    progress: Literal["yes", "no"]
    recovered: Literal["yes", "no"]
