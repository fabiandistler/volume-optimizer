"""Calculate recommended training volume adjustments for muscle group."""

from src.volume_data import volume_landmarks


def recommend_volume(
    current_sets: int, training_level: str, progress: str, recovered: str
) -> str:
    """Calculate recommended training volume adjustments for muscle group."""
    if progress == "yes":
        return "No change needed"
    elif progress == "no":
        if (
            current_sets < volume_landmarks["chest"][training_level]["MAV"]
            and recovered == "yes"
        ):
            return f"Increase to at least {volume_landmarks['chest'][training_level]['MAV']} sets per week."
        elif (
            current_sets > volume_landmarks["chest"][training_level]["MRV"]
            and recovered == "no"
        ):
            return f"Decrease to at most {volume_landmarks['chest'][training_level]['MRV']} sets per week."
    else:
        return "Reassess in two weeks."
    return "Maintain current volume."
