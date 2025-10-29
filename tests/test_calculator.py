from src.volume_calculator import recommend_volume


def test_intermediate_making_progress_below_mav():
    """
    Wenn: Intermediate, 12 Sets, Making Progress
    Dann: Empfehlung sollte 14-16 Sets sein
    """

    result = recommend_volume(
        current_sets=12,
        training_level="intermediate",
        progress="yes",
        recovered="yes",
    )
    assert result == "No change needed"


def test_beginner_no_progress_at_mev():
    """
    Wenn: Beginner, 8 Sets (=MEV), No Progress
    Dann: Empfehlung sollte erhöhen (12 Sets)
    """
    result = recommend_volume(
        current_sets=8,
        training_level="beginner",
        progress="no",
        recovered="yes",
    )
    assert result == "Increase to at least 12 sets per week."


def test_advanced_stalled_at_mrv():
    """
    Wenn: Advanced, 25 Sets (=MRV), Stalled
    Dann: Reduce to MRV
    """
    result = recommend_volume(
        current_sets=25,
        training_level="advanced",
        progress="no",
        recovered="no",
    )
    assert result == "Decrease to at most 24 sets per week."


def test_progress_yes():
    """
    If: Progress yes
    Then: No change needed
    """
    result = recommend_volume(
        current_sets=15,
        training_level="advanced",
        progress="yes",
        recovered="yes",
    )
    assert result == "No change needed"


def test_intermediate_no_progress_at_mav():
    """
    Wenn: Intermediate, 15 Sets, Making Progress
    Dann: Reassess in two weeks
    """

    result = recommend_volume(
        current_sets=15,
        training_level="intermediate",
        progress="no   ",
        recovered="yes",
    )
    assert result == "Reassess in two weeks."
