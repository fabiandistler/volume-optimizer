"""Calculate recommended training volume adjustments for muscle group."""

from .volume_data import volume_landmarks


def recommend_volume(current_sets, progress, recovered):
    if progress == "yes":
        return "No change needed"
    elif progress == "no":
        if (
            current_sets < volume_landmarks["chest"]["beginner"]["MAV"]
            and recovered == "yes"
        ):
            return f"Increase to at least {volume_landmarks['chest']['beginner']['MAV']} sets per week."
        else (
            current_sets > volume_landmarks["chest"]["beginner"]["MRV"]
            and recovered == "no"
        ):
            return f"Decrease to at most {volume_landmarks['chest']['beginner']['MRV']} sets per week."
    else:        return "Reassess in two weeks."
        return "Reassess in two weeks."
