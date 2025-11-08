"""Calculate recommended training volume adjustments for muscle group."""

from src.volume_data import volume_landmarks


def recommend_volume(
    current_sets: int,
    training_level: str,
    progress: str,
    recovered: str,
    muscle_group: str = "chest",
) -> str:
    """Calculate recommended training volume adjustments for muscle group.

    Args:
        current_sets: Current weekly set volume
        training_level: beginner, intermediate, or advanced
        progress: yes, no, or unclear
        recovered: yes or no
        muscle_group: Target muscle group (default: chest)

    Returns:
        Volume recommendation as a string
    """
    # Validate muscle group exists
    if muscle_group not in volume_landmarks:
        raise ValueError(
            f"Invalid muscle group. Available: {list(volume_landmarks.keys())}"
        )

    landmarks = volume_landmarks[muscle_group][training_level]

    if progress == "yes":
        return "No change needed - continue current volume"

    elif progress == "no":
        if current_sets < landmarks["MEV"]:
            return f"Increase to at least {landmarks['MEV']} sets per week (MEV)"

        elif current_sets < landmarks["MAV"] and recovered == "yes":
            return f"Increase to at least {landmarks['MAV']} sets per week (MAV)"

        elif current_sets > landmarks["MRV"] and recovered == "no":
            return f"Decrease to at most {landmarks['MRV']} sets per week (MRV)"

        else:
            return "Maintain current volume and reassess next week"

    else:  # progress == "unclear"
        return "Reassess in two weeks with clearer progress indicators"

    # Should not reach here
    raise ValueError("Invalid input parameters")
