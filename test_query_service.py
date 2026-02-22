"""
Tests for query service validation and query building.
"""

import pytest
from services.query_service import validate_filter_type, build_rescue_query


class TestValidateFilterType:
    """Tests for filter type validation."""
    
    def test_validate_all_filter(self):
        """'all' is a valid filter."""
        assert validate_filter_type("all") == "all"
    
    def test_validate_water_filter(self):
        """'water' is a valid filter."""
        assert validate_filter_type("water") == "water"
    
    def test_validate_mountain_filter(self):
        """'mountain' is a valid filter."""
        assert validate_filter_type("mountain") == "mountain"
    
    def test_validate_disaster_filter(self):
        """'disaster' is a valid filter."""
        assert validate_filter_type("disaster") == "disaster"
    
    def test_validate_rejects_invalid_filter(self):
        """Invalid filter type raises ValueError."""
        with pytest.raises(ValueError):
            validate_filter_type("invalid")
    
    def test_validate_rejects_empty_string(self):
        """Empty string is rejected."""
        with pytest.raises(ValueError):
            validate_filter_type("")
    
    def test_validate_case_sensitive(self):
        """Filter validation is case-sensitive."""
        with pytest.raises(ValueError):
            validate_filter_type("WATER")
    
    def test_validate_with_whitespace(self):
        """Filter with whitespace is rejected."""
        with pytest.raises(ValueError):
            validate_filter_type(" water")


class TestBuildRescueQuery:
    """Tests for rescue query building."""
    
    def test_build_water_query(self):
        """Water filter builds correct MongoDB query."""
        query = build_rescue_query("water")
        
        # Should have $and array with three conditions
        assert "$and" in query
        assert len(query["$and"]) == 3
        
        # Check breed condition
        breed_cond = [c for c in query["$and"] if "breed" in c][0]
        assert set(breed_cond["breed"]["$in"]) == {
            "Labrador Retriever Mix",
            "Chesapeake Bay Retriever",
            "Newfoundland"
        }
        
        # Check sex condition
        sex_cond = [c for c in query["$and"] if "sex_upon_outcome" in c][0]
        assert sex_cond["sex_upon_outcome"] == "Intact Female"
        
        # Check age condition
        age_cond = [c for c in query["$and"] if "age_upon_outcome_in_weeks" in c][0]
        assert age_cond["age_upon_outcome_in_weeks"]["$gte"] == 26
        assert age_cond["age_upon_outcome_in_weeks"]["$lte"] == 156
    
    def test_build_mountain_query(self):
        """Mountain filter builds correct MongoDB query."""
        query = build_rescue_query("mountain")
        
        assert "$and" in query
        assert len(query["$and"]) == 3
        
        # Check breed condition has right breeds
        breed_cond = [c for c in query["$and"] if "breed" in c][0]
        assert "German Shepherd" in breed_cond["breed"]["$in"]
        assert "Rottweiler" in breed_cond["breed"]["$in"]
        assert "Alaskan Malamute" in breed_cond["breed"]["$in"]
        
        # Check sex is male
        sex_cond = [c for c in query["$and"] if "sex_upon_outcome" in c][0]
        assert sex_cond["sex_upon_outcome"] == "Intact Male"
    
    def test_build_disaster_query(self):
        """Disaster filter builds correct MongoDB query."""
        query = build_rescue_query("disaster")
        
        assert "$and" in query
        
        # Check breed condition has right breeds
        breed_cond = [c for c in query["$and"] if "breed" in c][0]
        assert "Doberman Pinscher" in breed_cond["breed"]["$in"]
        assert "Bloodhound" in breed_cond["breed"]["$in"]
        
        # Check age range is different (longer)
        age_cond = [c for c in query["$and"] if "age_upon_outcome_in_weeks" in c][0]
        assert age_cond["age_upon_outcome_in_weeks"]["$gte"] == 20
        assert age_cond["age_upon_outcome_in_weeks"]["$lte"] == 300
    
    def test_build_all_query(self):
        """All filter returns empty query (no filtering)."""
        query = build_rescue_query("all")
        
        assert query == {}
    
    def test_build_query_validates_input(self):
        """Invalid filter type raises ValueError."""
        with pytest.raises(ValueError):
            build_rescue_query("invalid")
    
    def test_water_age_range(self):
        """Water filter has correct age range (6 months to 3 years)."""
        query = build_rescue_query("water")
        age_cond = [c for c in query["$and"] if "age_upon_outcome_in_weeks" in c][0]
        
        # 6 months = 26 weeks, 3 years = 156 weeks
        assert age_cond["age_upon_outcome_in_weeks"]["$gte"] == 26
        assert age_cond["age_upon_outcome_in_weeks"]["$lte"] == 156
    
    def test_disaster_age_range(self):
        """Disaster filter has extended age range (5 months to 7 years)."""
        query = build_rescue_query("disaster")
        age_cond = [c for c in query["$and"] if "age_upon_outcome_in_weeks" in c][0]
        
        # 5 months = 20 weeks, 7 years = 300 weeks
        assert age_cond["age_upon_outcome_in_weeks"]["$gte"] == 20
        assert age_cond["age_upon_outcome_in_weeks"]["$lte"] == 300
