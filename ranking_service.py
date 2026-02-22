"""
Ranking and scoring service for rescue dog matching.

This module implements a scoring algorithm that evaluates dogs against
rescue criteria, allowing for ordered results that clearly indicate
which dogs best match the selection requirements.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MatchCriteria:
    """
    Immutable scoring criteria for ranking rescue dogs.
    
    Attributes:
        preferred_breeds: Set of breed names that match this rescue type
        min_weeks: Minimum age in weeks (inclusive)
        max_weeks: Maximum age in weeks (inclusive)
        preferred_sex: Required sex/reproductive status
    """
    preferred_breeds: set[str] | None = None
    min_weeks: int | None = None
    max_weeks: int | None = None
    preferred_sex: str | None = None


@dataclass(frozen=True)
class BreedScore:
    """Scoring breakdown for a single dog record."""
    breed_match: int
    age_match: int
    sex_match: int
    total_score: int


class RankingAlgorithm:
    """
    Scoring algorithm for matching dogs to rescue criteria.
    
    Uses weighted scoring across three dimensions:
    - Breed match (50 points): Direct match against preferred breeds
    - Age match (30 points): Within acceptable age range
    - Sex match (20 points): Matches required reproductive status
    
    Total possible score: 100 points
    """
    
    # Scoring weights
    BREED_WEIGHT = 50
    AGE_WEIGHT = 30
    SEX_WEIGHT = 20
    
    @staticmethod
    def score_dog(record: dict, criteria: MatchCriteria) -> BreedScore:
        """
        Score a single dog record against matching criteria.
        
        Args:
            record: Dog record dict containing breed, age_upon_outcome_in_weeks, sex_upon_outcome
            criteria: MatchCriteria with preferred attributes
        
        Returns:
            BreedScore with component scores and total
        
        Example:
            >>> dog = {
            ...     "breed": "Labrador Retriever Mix",
            ...     "age_upon_outcome_in_weeks": 52,
            ...     "sex_upon_outcome": "Intact Female"
            ... }
            >>> criteria = MatchCriteria(
            ...     preferred_breeds={"Labrador Retriever Mix"},
            ...     min_weeks=26,
            ...     max_weeks=156,
            ...     preferred_sex="Intact Female"
            ... )
            >>> score = RankingAlgorithm.score_dog(dog, criteria)
            >>> score.total_score
            100
        """
        breed_score = RankingAlgorithm._score_breed(record, criteria)
        age_score = RankingAlgorithm._score_age(record, criteria)
        sex_score = RankingAlgorithm._score_sex(record, criteria)
        
        total = breed_score + age_score + sex_score
        
        return BreedScore(
            breed_match=breed_score,
            age_match=age_score,
            sex_match=sex_score,
            total_score=total
        )
    
    @staticmethod
    def _score_breed(record: dict, criteria: MatchCriteria) -> int:
        """
        Score breed match: 50 points for exact breed match, 0 otherwise.
        
        Args:
            record: Dog record with 'breed' field
            criteria: MatchCriteria with preferred_breeds
        
        Returns:
            RankingAlgorithm.BREED_WEIGHT if match, 0 otherwise
        """
        if criteria.preferred_breeds is None:
            return 0
        
        breed = record.get("breed")
        if breed and breed in criteria.preferred_breeds:
            return RankingAlgorithm.BREED_WEIGHT
        
        return 0
    
    @staticmethod
    def _score_age(record: dict, criteria: MatchCriteria) -> int:
        """
        Score age match: 30 points if within range, 0 if outside.
        
        Age scoring is binary (not gradient): either the dog is within
        the acceptable age range for this rescue type (30 points) or not (0 points).
        
        Args:
            record: Dog record with 'age_upon_outcome_in_weeks' field
            criteria: MatchCriteria with min_weeks and max_weeks
        
        Returns:
            RankingAlgorithm.AGE_WEIGHT if within range, 0 otherwise
        """
        if criteria.min_weeks is None or criteria.max_weeks is None:
            return 0
        
        age = record.get("age_upon_outcome_in_weeks")
        
        # Safe type checking for age field
        if not isinstance(age, (int, float)):
            return 0
        
        # Check if age falls within acceptable range (inclusive bounds)
        if criteria.min_weeks <= age <= criteria.max_weeks:
            return RankingAlgorithm.AGE_WEIGHT
        
        return 0
    
    @staticmethod
    def _score_sex(record: dict, criteria: MatchCriteria) -> int:
        """
        Score sex match: 20 points for exact sex match, 0 otherwise.
        
        Args:
            record: Dog record with 'sex_upon_outcome' field
            criteria: MatchCriteria with preferred_sex
        
        Returns:
            RankingAlgorithm.SEX_WEIGHT if match, 0 otherwise
        """
        if criteria.preferred_sex is None:
            return 0
        
        sex = record.get("sex_upon_outcome")
        if sex and sex == criteria.preferred_sex:
            return RankingAlgorithm.SEX_WEIGHT
        
        return 0


def criteria_for_filter(filter_type: str) -> MatchCriteria:
    """
    Get matching criteria for a rescue type filter.
    
    Maps filter selection to specific criteria that identify suitable dogs
    for that rescue category. Criteria include breed preferences, age ranges,
    and sex requirements based on typical rescue team needs.
    
    Args:
        filter_type: One of {'all', 'water', 'mountain', 'disaster'}
    
    Returns:
        MatchCriteria with preferences for the selected rescue type,
        or empty MatchCriteria if filter_type is 'all'
    
    Examples:
        >>> water_criteria = criteria_for_filter("water")
        >>> water_criteria.preferred_breeds
        {'Labrador Retriever Mix', 'Chesapeake Bay Retriever', 'Newfoundland'}
        
        >>> mountain_criteria = criteria_for_filter("mountain")
        >>> mountain_criteria.min_weeks
        26
    """
    if filter_type == "water":
        return MatchCriteria(
            preferred_breeds={
                "Labrador Retriever Mix",
                "Chesapeake Bay Retriever",
                "Newfoundland"
            },
            min_weeks=26,  # 6 months
            max_weeks=156,  # 3 years
            preferred_sex="Intact Female",
        )
    
    if filter_type == "mountain":
        return MatchCriteria(
            preferred_breeds={
                "German Shepherd",
                "Alaskan Malamute",
                "Old English Sheepdog",
                "Siberian Husky",
                "Rottweiler"
            },
            min_weeks=26,  # 6 months
            max_weeks=156,  # 3 years
            preferred_sex="Intact Male",
        )
    
    if filter_type == "disaster":
        return MatchCriteria(
            preferred_breeds={
                "Doberman Pinscher",
                "German Shepherd",
                "Golden Retriever",
                "Bloodhound",
                "Rottweiler"
            },
            min_weeks=20,  # 5 months
            max_weeks=300,  # 7 years
            preferred_sex="Intact Male",
        )
    
    # Default: no criteria (for "all" filter)
    return MatchCriteria()


def rank_results(rows: list[dict], criteria: MatchCriteria) -> list[dict]:
    """
    Rank results by match score, highest scores first.
    
    This function implements the core ranking algorithm: each dog is scored
    against the matching criteria, then results are sorted in descending order
    of total score. Dogs with perfect matches appear first, followed by
    partial matches, with non-matching dogs last.
    
    Args:
        rows: List of dog records from database
        criteria: MatchCriteria for scoring
    
    Returns:
        Same records sorted by score (descending), with 'match_score' and
        'score_breakdown' fields added to each record
    
    Examples:
        >>> dogs = [
        ...     {
        ...         "breed": "Labrador Retriever Mix",
        ...         "age_upon_outcome_in_weeks": 52,
        ...         "sex_upon_outcome": "Intact Female"
        ...     },
        ...     {
        ...         "breed": "Terrier Mix",
        ...         "age_upon_outcome_in_weeks": 50,
        ...         "sex_upon_outcome": "Intact Male"
        ...     }
        ... ]
        >>> criteria = criteria_for_filter("water")
        >>> ranked = rank_results(dogs, criteria)
        >>> ranked[0]["match_score"]
        100
        >>> ranked[0]["score_breakdown"]["breed_match"]
        50
    """
    # Score each record
    scored_records = []
    for record in rows:
        score = RankingAlgorithm.score_dog(record, criteria)
        
        # Create scored record with breakdown
        scored_record = dict(record)
        scored_record["match_score"] = score.total_score
        scored_record["score_breakdown"] = {
            "breed_match": score.breed_match,
            "age_match": score.age_match,
            "sex_match": score.sex_match,
        }
        
        scored_records.append((score.total_score, scored_record))
    
    # Sort by score (descending), maintaining order for ties
    scored_records.sort(key=lambda x: x[0], reverse=True)
    
    # Return just the records with scores attached
    return [record for _, record in scored_records]
