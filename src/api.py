from fastapi import FastAPI
from src.volume_calculator import recommend_volume

app = FastAPI()


@app.get("/health_check")
async def health_check():
    return {"message": "Everything is working fine!"}


@app.get("/predict-volume/{current_sets}/{training_level}/{progress}/{recovered}")
async def predict_volume_get(
    current_sets: int, training_level: str, progress: str, recovered: str
):
    result = recommend_volume(current_sets, training_level, progress, recovered)
    return {"volume_prediction": result}


# @app.post("/predict-volume")
# async def predict_volume_post(request: VolumeRequest):
#   result = "TODO"
#  return {"volume_prediction": result}
