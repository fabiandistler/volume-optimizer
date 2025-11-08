"""Tests for volume calculator functionality."""

import pytest
from src.volume_calculator import recommend_volume


def test_intermediate_making_progress():
    """When making progress, no change needed."""
    result = recommend_volume(
        current_sets=12,
        training_level="intermediate",
        progress="yes",
        recovered="yes",
    )
    assert result == "No change needed - continue current volume"


def test_beginner_no_progress_below_mev():
    """When below MEV and no progress, increase to MEV."""
    result = recommend_volume(
        current_sets=6,
        training_level="beginner",
        progress="no",
        recovered="yes",
    )
    assert "8 sets per week (MEV)" in result


def test_beginner_no_progress_at_mev():
    """When at MEV and no progress with recovery, increase to MAV."""
    result = recommend_volume(
        current_sets=8,
        training_level="beginner",
        progress="no",
        recovered="yes",
    )
    assert "12 sets per week (MAV)" in result


def test_advanced_stalled_above_mrv():
    """When above MRV and not recovered, decrease to MRV."""
    result = recommend_volume(
        current_sets=25,
        training_level="advanced",
        progress="no",
        recovered="no",
    )
    assert "24 sets per week (MRV)" in result


def test_progress_yes():
    """When making progress, no change needed."""
    result = recommend_volume(
        current_sets=15,
        training_level="advanced",
        progress="yes",
        recovered="yes",
    )
    assert result == "No change needed - continue current volume"


def test_unclear_progress():
    """When progress is unclear, reassess."""
    result = recommend_volume(
        current_sets=15,
        training_level="intermediate",
        progress="unclear",
        recovered="yes",
    )
    assert "Reassess in two weeks" in result


def test_multiple_muscle_groups():
    """Test that different muscle groups work."""
    # Test chest
    chest_result = recommend_volume(
        current_sets=12,
        training_level="intermediate",
        progress="yes",
        recovered="yes",
        muscle_group="chest",
    )
    assert "No change needed" in chest_result

    # Test back
    back_result = recommend_volume(
        current_sets=5,
        training_level="beginner",
        progress="no",
        recovered="yes",
        muscle_group="back",
    )
    assert "10 sets per week (MEV)" in back_result

    # Test biceps
    biceps_result = recommend_volume(
        current_sets=4,
        training_level="beginner",
        progress="no",
        recovered="yes",
        muscle_group="biceps",
    )
    assert "6 sets per week (MEV)" in biceps_result


def test_invalid_muscle_group():
    """Test that invalid muscle group raises error."""
    with pytest.raises(ValueError, match="Invalid muscle group"):
        recommend_volume(
            current_sets=12,
            training_level="intermediate",
            progress="yes",
            recovered="yes",
            muscle_group="invalid_muscle",
        )


def test_all_training_levels():
    """Test all training levels work."""
    for level in ["beginner", "intermediate", "advanced"]:
        result = recommend_volume(
            current_sets=12,
            training_level=level,
            progress="yes",
            recovered="yes",
            muscle_group="chest",
        )
        assert "No change needed" in result


def test_maintain_volume_recommendation():
    """Test edge case where user should maintain volume."""
    result = recommend_volume(
        current_sets=15,
        training_level="intermediate",
        progress="no",
        recovered="no",  # Not recovered but within range
        muscle_group="chest",
    )
    assert "Maintain current volume" in result
