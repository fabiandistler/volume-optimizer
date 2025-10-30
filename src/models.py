from pydantic import BaseModel, PositiveInt


class VolumeRequest(BaseModel):
    current_sets: PositiveInt
    training_level: str
    progress: str
    recovered: str
