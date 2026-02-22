"""
Comprehensive tests for ranking and scoring algorithm.

Tests cover normal cases, edge cases, and boundary conditions to ensure
the ranking algorithm produces correct scores and ordering.
"""

import pytest
from services.ranking_service import (
    MatchCriteria,
    BreedScore,
    RankingAlgorithm,
    criteria_for_filter,
    rank_results,
)


class TestRankingAlgorithm:
    """Tests for the RankingAlgorithm scoring class."""
    
    def test_score_dog_perfect_match(self):
        """A dog matching all criteria gets maximum score (100)."""
        dog = {
            "breed": "Labrador Retriever Mix",
            "age_upon_outcome_in_weeks": 52,
            "sex_upon_outcome": "Intact Female"
        }
        criteria = MatchCriteria(
            preferred_breeds={"Labrador Retriever Mix"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        score = RankingAlgorithm.score_dog(dog, criteria)
        
        assert score.breed_match == 50
        assert score.age_match == 30
        assert score.sex_match == 20
        assert score.total_score == 100
    
    def test_score_dog_breed_only(self):
        """A dog matching only breed gets 50 points."""
        dog = {
            "breed": "Labrador Retriever Mix",
            "age_upon_outcome_in_weeks": 10,  # Too young
            "sex_upon_outcome": "Intact Male"  # Wrong sex
        }
        criteria = MatchCriteria(
            preferred_breeds={"Labrador Retriever Mix"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        score = RankingAlgorithm.score_dog(dog, criteria)
        
        assert score.breed_match == 50
        assert score.age_match == 0
        assert score.sex_match == 0
        assert score.total_score == 50
    
    def test_score_dog_age_only(self):
        """A dog matching only age gets 30 points."""
        dog = {
            "breed": "Terrier Mix",  # Wrong breed
            "age_upon_outcome_in_weeks": 52,
            "sex_upon_outcome": "Intact Male"  # Wrong sex
        }
        criteria = MatchCriteria(
            preferred_breeds={"Labrador Retriever Mix"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        score = RankingAlgorithm.score_dog(dog, criteria)
        
        assert score.breed_match == 0
        assert score.age_match == 30
        assert score.sex_match == 0
        assert score.total_score == 30
    
    def test_score_dog_sex_only(self):
        """A dog matching only sex gets 20 points."""
        dog = {
            "breed": "Terrier Mix",  # Wrong breed
            "age_upon_outcome_in_weeks": 10,  # Too young
            "sex_upon_outcome": "Intact Female"
        }
        criteria = MatchCriteria(
            preferred_breeds={"Labrador Retriever Mix"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        score = RankingAlgorithm.score_dog(dog, criteria)
        
        assert score.breed_match == 0
        assert score.age_match == 0
        assert score.sex_match == 20
        assert score.total_score == 20
    
    def test_score_dog_no_matches(self):
        """A dog matching no criteria gets 0 points."""
        dog = {
            "breed": "Chihuahua",
            "age_upon_outcome_in_weeks": 500,  # Way too old
            "sex_upon_outcome": "Spayed Female"  # Not intact
        }
        criteria = MatchCriteria(
            preferred_breeds={"Labrador Retriever Mix"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        score = RankingAlgorithm.score_dog(dog, criteria)
        
        assert score.total_score == 0
    
    def test_score_age_boundary_minimum(self):
        """A dog exactly at minimum age gets age points."""
        dog = {
            "breed": "Labrador Retriever Mix",
            "age_upon_outcome_in_weeks": 26,  # Exactly minimum
            "sex_upon_outcome": "Intact Female"
        }
        criteria = MatchCriteria(
            preferred_breeds={"Labrador Retriever Mix"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        score = RankingAlgorithm.score_dog(dog, criteria)
        
        assert score.age_match == 30
        assert score.total_score == 100
    
    def test_score_age_boundary_maximum(self):
        """A dog exactly at maximum age gets age points."""
        dog = {
            "breed": "Labrador Retriever Mix",
            "age_upon_outcome_in_weeks": 156,  # Exactly maximum
            "sex_upon_outcome": "Intact Female"
        }
        criteria = MatchCriteria(
            preferred_breeds={"Labrador Retriever Mix"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        score = RankingAlgorithm.score_dog(dog, criteria)
        
        assert score.age_match == 30
        assert score.total_score == 100
    
    def test_score_age_just_below_minimum(self):
        """A dog just below minimum age gets 0 age points."""
        dog = {
            "breed": "Labrador Retriever Mix",
            "age_upon_outcome_in_weeks": 25,  # One week too young
            "sex_upon_outcome": "Intact Female"
        }
        criteria = MatchCriteria(
            preferred_breeds={"Labrador Retriever Mix"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        score = RankingAlgorithm.score_dog(dog, criteria)
        
        assert score.age_match == 0
        assert score.total_score == 70  # Only breed + sex
    
    def test_score_age_just_above_maximum(self):
        """A dog just above maximum age gets 0 age points."""
        dog = {
            "breed": "Labrador Retriever Mix",
            "age_upon_outcome_in_weeks": 157,  # One week too old
            "sex_upon_outcome": "Intact Female"
        }
        criteria = MatchCriteria(
            preferred_breeds={"Labrador Retriever Mix"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        score = RankingAlgorithm.score_dog(dog, criteria)
        
        assert score.age_match == 0
        assert score.total_score == 70  # Only breed + sex
    
    def test_score_dog_missing_fields(self):
        """Scoring handles missing fields gracefully."""
        dog = {"breed": "Labrador Retriever Mix"}  # Missing age and sex
        criteria = MatchCriteria(
            preferred_breeds={"Labrador Retriever Mix"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        score = RankingAlgorithm.score_dog(dog, criteria)
        
        # Should score only breed (50), no crash
        assert score.breed_match == 50
        assert score.age_match == 0
        assert score.sex_match == 0
        assert score.total_score == 50
    
    def test_score_dog_null_age(self):
        """Scoring handles null age field."""
        dog = {
            "breed": "Labrador Retriever Mix",
            "age_upon_outcome_in_weeks": None,  # Null age
            "sex_upon_outcome": "Intact Female"
        }
        criteria = MatchCriteria(
            preferred_breeds={"Labrador Retriever Mix"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        score = RankingAlgorithm.score_dog(dog, criteria)
        
        assert score.age_match == 0
        assert score.total_score == 70  # Breed + sex, no age
    
    def test_score_dog_string_age(self):
        """Scoring handles non-numeric age gracefully."""
        dog = {
            "breed": "Labrador Retriever Mix",
            "age_upon_outcome_in_weeks": "52 weeks",  # String instead of number
            "sex_upon_outcome": "Intact Female"
        }
        criteria = MatchCriteria(
            preferred_breeds={"Labrador Retriever Mix"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        score = RankingAlgorithm.score_dog(dog, criteria)
        
        assert score.age_match == 0
        assert score.total_score == 70  # Breed + sex, no age
    
    def test_score_dog_float_age(self):
        """Scoring correctly handles floating-point age values."""
        dog = {
            "breed": "Labrador Retriever Mix",
            "age_upon_outcome_in_weeks": 52.5,  # Float age
            "sex_upon_outcome": "Intact Female"
        }
        criteria = MatchCriteria(
            preferred_breeds={"Labrador Retriever Mix"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        score = RankingAlgorithm.score_dog(dog, criteria)
        
        assert score.age_match == 30
        assert score.total_score == 100


class TestCriteriaForFilter:
    """Tests for criteria_for_filter function."""
    
    def test_water_criteria(self):
        """Water filter returns correct criteria."""
        criteria = criteria_for_filter("water")
        
        assert criteria.preferred_breeds == {
            "Labrador Retriever Mix",
            "Chesapeake Bay Retriever",
            "Newfoundland"
        }
        assert criteria.min_weeks == 26
        assert criteria.max_weeks == 156
        assert criteria.preferred_sex == "Intact Female"
    
    def test_mountain_criteria(self):
        """Mountain filter returns correct criteria."""
        criteria = criteria_for_filter("mountain")
        
        assert "German Shepherd" in criteria.preferred_breeds
        assert "Alaskan Malamute" in criteria.preferred_breeds
        assert criteria.min_weeks == 26
        assert criteria.max_weeks == 156
        assert criteria.preferred_sex == "Intact Male"
    
    def test_disaster_criteria(self):
        """Disaster filter returns correct criteria."""
        criteria = criteria_for_filter("disaster")
        
        assert "Doberman Pinscher" in criteria.preferred_breeds
        assert "German Shepherd" in criteria.preferred_breeds
        assert criteria.min_weeks == 20
        assert criteria.max_weeks == 300
        assert criteria.preferred_sex == "Intact Male"
    
    def test_all_criteria_empty(self):
        """All filter returns empty criteria (no filtering)."""
        criteria = criteria_for_filter("all")
        
        assert criteria.preferred_breeds is None
        assert criteria.min_weeks is None
        assert criteria.max_weeks is None
        assert criteria.preferred_sex is None


class TestRankResults:
    """Tests for rank_results function."""
    
    def test_rank_results_orders_by_score(self):
        """Results are sorted by score (highest first)."""
        dogs = [
            {
                "breed": "Terrier Mix",
                "age_upon_outcome_in_weeks": 50,
                "sex_upon_outcome": "Intact Male"
            },
            {
                "breed": "Labrador Retriever Mix",
                "age_upon_outcome_in_weeks": 52,
                "sex_upon_outcome": "Intact Female"
            },
            {
                "breed": "Chihuahua",
                "age_upon_outcome_in_weeks": 100,
                "sex_upon_outcome": "Spayed Female"
            }
        ]
        criteria = criteria_for_filter("water")
        
        ranked = rank_results(dogs, criteria)
        
        # First should be perfect match (Labrador female)
        assert ranked[0]["breed"] == "Labrador Retriever Mix"
        assert ranked[0]["match_score"] == 100
        
        # Second should be partial match (age+sex but wrong breed)
        assert ranked[1]["breed"] == "Terrier Mix"
        assert ranked[1]["match_score"] == 30  # age only
        
        # Third should be no match
        assert ranked[2]["breed"] == "Chihuahua"
        assert ranked[2]["match_score"] == 0
    
    def test_rank_results_includes_score_breakdown(self):
        """Ranked results include score breakdown details."""
        dogs = [{
            "breed": "Labrador Retriever Mix",
            "age_upon_outcome_in_weeks": 52,
            "sex_upon_outcome": "Intact Female"
        }]
        criteria = criteria_for_filter("water")
        
        ranked = rank_results(dogs, criteria)
        
        assert "match_score" in ranked[0]
        assert "score_breakdown" in ranked[0]
        assert "breed_match" in ranked[0]["score_breakdown"]
        assert "age_match" in ranked[0]["score_breakdown"]
        assert "sex_match" in ranked[0]["score_breakdown"]
    
    def test_rank_results_empty_list(self):
        """Ranking handles empty input gracefully."""
        criteria = criteria_for_filter("water")
        
        ranked = rank_results([], criteria)
        
        assert ranked == []
    
    def test_rank_results_missing_fields(self):
        """Ranking handles records with missing fields."""
        dogs = [
            {"breed": "Labrador Retriever Mix"},  # Missing age and sex
            {"age_upon_outcome_in_weeks": 52},    # Missing breed and sex
            {}  # Completely empty
        ]
        criteria = criteria_for_filter("water")
        
        ranked = rank_results(dogs, criteria)
        
        # Should not crash, all records should be returned
        assert len(ranked) == 3
        
        # First dog scores only breed (50)
        assert ranked[0]["match_score"] == 50
        
        # Second dog scores only age (30)
        assert ranked[1]["match_score"] == 30
        
        # Third dog scores nothing (0)
        assert ranked[2]["match_score"] == 0
    
    def test_rank_results_with_no_criteria(self):
        """Ranking with empty criteria (all filter) gives all zeros."""
        dogs = [
            {
                "breed": "Labrador Retriever Mix",
                "age_upon_outcome_in_weeks": 52,
                "sex_upon_outcome": "Intact Female"
            }
        ]
        criteria = criteria_for_filter("all")  # Empty criteria
        
        ranked = rank_results(dogs, criteria)
        
        assert ranked[0]["match_score"] == 0
    
    def test_rank_results_tie_ordering(self):
        """Dogs with same score maintain input order (stable sort)."""
        dogs = [
            {"breed": "Terrier", "age_upon_outcome_in_weeks": 100, "sex_upon_outcome": "Female"},
            {"breed": "Poodle", "age_upon_outcome_in_weeks": 100, "sex_upon_outcome": "Female"},
            {"breed": "Collie", "age_upon_outcome_in_weeks": 100, "sex_upon_outcome": "Female"},
        ]
        criteria = MatchCriteria()  # Empty criteria, all get score 0
        
        ranked = rank_results(dogs, criteria)
        
        # All have same score, should maintain relative order
        assert ranked[0]["breed"] == "Terrier"
        assert ranked[1]["breed"] == "Poodle"
        assert ranked[2]["breed"] == "Collie"
    
    def test_rank_results_mixed_disaster_dogs(self):
        """Test ranking with disaster rescue dogs."""
        dogs = [
            {
                "breed": "Doberman Pinscher",
                "age_upon_outcome_in_weeks": 100,
                "sex_upon_outcome": "Intact Male"
            },
            {
                "breed": "Terrier Mix",
                "age_upon_outcome_in_weeks": 100,
                "sex_upon_outcome": "Intact Male"
            },
            {
                "breed": "German Shepherd",
                "age_upon_outcome_in_weeks": 400,  # Too old
                "sex_upon_outcome": "Intact Male"
            }
        ]
        criteria = criteria_for_filter("disaster")
        
        ranked = rank_results(dogs, criteria)
        
        # First: Doberman (perfect match)
        assert ranked[0]["breed"] == "Doberman Pinscher"
        assert ranked[0]["match_score"] == 100
        
        # Second: Terrier (age+sex only)
        assert ranked[1]["breed"] == "Terrier Mix"
        assert ranked[1]["match_score"] == 50  # age + sex
        
        # Third: German Shepherd (breed+sex, but too old)
        assert ranked[2]["breed"] == "German Shepherd"
        assert ranked[2]["match_score"] == 70  # breed + sex only
    
    def test_rank_results_preserves_all_fields(self):
        """Ranking preserves all original fields in records."""
        dogs = [{
            "breed": "Labrador Retriever Mix",
            "age_upon_outcome_in_weeks": 52,
            "sex_upon_outcome": "Intact Female",
            "animal_id": "A12345",
            "color": "Yellow",
            "name": "Buddy"
        }]
        criteria = criteria_for_filter("water")
        
        ranked = rank_results(dogs, criteria)
        
        # All original fields should still be present
        assert ranked[0]["animal_id"] == "A12345"
        assert ranked[0]["color"] == "Yellow"
        assert ranked[0]["name"] == "Buddy"


class TestBreedScoreDataClass:
    """Tests for BreedScore data structure."""
    
    def test_breed_score_immutable(self):
        """BreedScore is immutable (frozen dataclass)."""
        score = BreedScore(breed_match=50, age_match=30, sex_match=20, total_score=100)
        
        with pytest.raises(AttributeError):
            score.total_score = 90


class TestMatchCriteriaDataClass:
    """Tests for MatchCriteria data structure."""
    
    def test_match_criteria_immutable(self):
        """MatchCriteria is immutable (frozen dataclass)."""
        criteria = MatchCriteria(
            preferred_breeds={"Lab"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        with pytest.raises(AttributeError):
            criteria.min_weeks = 20
    
    def test_match_criteria_can_compare(self):
        """Two MatchCriteria with same values are equal."""
        criteria1 = MatchCriteria(
            preferred_breeds={"Lab"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        criteria2 = MatchCriteria(
            preferred_breeds={"Lab"},
            min_weeks=26,
            max_weeks=156,
            preferred_sex="Intact Female"
        )
        
        assert criteria1 == criteria2
