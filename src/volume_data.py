"""Muscle volume landmarks for all major muscle groups.

MEV = Minimum Effective Volume (minimum to see gains)
MAV = Maximum Adaptive Volume (optimal for most people)
MRV = Maximum Recoverable Volume (maximum before overtraining)
"""

volume_landmarks = {
    # Free tier - Chest only
    "chest": {
        "beginner": {"MEV": 8, "MAV": 12, "MRV": 16},
        "intermediate": {"MEV": 10, "MAV": 15, "MRV": 20},
        "advanced": {"MEV": 12, "MAV": 18, "MRV": 24},
    },
    # Pro tier - All muscle groups
    "back": {
        "beginner": {"MEV": 10, "MAV": 14, "MRV": 18},
        "intermediate": {"MEV": 12, "MAV": 16, "MRV": 22},
        "advanced": {"MEV": 14, "MAV": 20, "MRV": 26},
    },
    "shoulders": {
        "beginner": {"MEV": 8, "MAV": 12, "MRV": 16},
        "intermediate": {"MEV": 10, "MAV": 14, "MRV": 20},
        "advanced": {"MEV": 12, "MAV": 16, "MRV": 24},
    },
    "biceps": {
        "beginner": {"MEV": 6, "MAV": 10, "MRV": 14},
        "intermediate": {"MEV": 8, "MAV": 12, "MRV": 18},
        "advanced": {"MEV": 10, "MAV": 14, "MRV": 22},
    },
    "triceps": {
        "beginner": {"MEV": 6, "MAV": 10, "MRV": 14},
        "intermediate": {"MEV": 8, "MAV": 12, "MRV": 18},
        "advanced": {"MEV": 10, "MAV": 14, "MRV": 22},
    },
    "quads": {
        "beginner": {"MEV": 8, "MAV": 12, "MRV": 16},
        "intermediate": {"MEV": 10, "MAV": 14, "MRV": 20},
        "advanced": {"MEV": 12, "MAV": 18, "MRV": 24},
    },
    "hamstrings": {
        "beginner": {"MEV": 6, "MAV": 10, "MRV": 14},
        "intermediate": {"MEV": 8, "MAV": 12, "MRV": 18},
        "advanced": {"MEV": 10, "MAV": 14, "MRV": 22},
    },
    "glutes": {
        "beginner": {"MEV": 6, "MAV": 10, "MRV": 14},
        "intermediate": {"MEV": 8, "MAV": 12, "MRV": 18},
        "advanced": {"MEV": 10, "MAV": 14, "MRV": 22},
    },
    "calves": {
        "beginner": {"MEV": 8, "MAV": 12, "MRV": 16},
        "intermediate": {"MEV": 10, "MAV": 14, "MRV": 20},
        "advanced": {"MEV": 12, "MAV": 16, "MRV": 24},
    },
    "abs": {
        "beginner": {"MEV": 6, "MAV": 10, "MRV": 14},
        "intermediate": {"MEV": 8, "MAV": 12, "MRV": 18},
        "advanced": {"MEV": 10, "MAV": 14, "MRV": 22},
    },
}


def get_available_muscle_groups(subscription_tier: str) -> list[str]:
    """Get available muscle groups based on subscription tier."""
    if subscription_tier == "free":
        return ["chest"]
    else:  # pro or enterprise
        return list(volume_landmarks.keys())
