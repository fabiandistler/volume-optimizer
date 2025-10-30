from fastapi import FastAPI
from src.volume_calculator import recommend_volume

app = FastAPI()


@app.get("/health_check")
async def health_check():
    return {"message": "Everything is working fine!"}


@app.get("/recommend/{current_sets}/{training_level}/{progress}/{recovered}")
async def recommend(
    current_sets: int, training_level: str, progress: str, recovered: str
):
    result = recommend_volume(current_sets, training_level, progress, recovered)
    return {"recommendation": result}
