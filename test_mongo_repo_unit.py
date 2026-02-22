"""
Tests for MongoDB repository operations including server-side pagination and sorting.
"""

import pytest
from unittest.mock import MagicMock, Mock, patch
from data.mongo_repo import AnimalRepository


class TestAnimalRepositoryRead:
    """Tests for the read method with pagination and sorting."""
    
    def test_read_returns_list_on_success(self):
        """Read returns list of documents on success."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = [{"breed": "Lab", "match_score": 100}]
        repo.collection.find.return_value = mock_cursor
        
        result = repo.read({}, limit=10)
        
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_read_applies_sort_server_side(self):
        """Sort is applied server-side before skip/limit."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        repo.collection.find.return_value = mock_cursor
        
        # Call with sort specification
        sort_spec = [("match_score", -1), ("breed", 1)]
        repo.read({}, sort=sort_spec, limit=10)
        
        # Verify sort was called with correct spec
        mock_cursor.sort.assert_called_with(sort_spec)
    
    def test_read_applies_skip_pagination(self):
        """Skip is applied for pagination."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        repo.collection.find.return_value = mock_cursor
        
        # Call with skip for page 2 (10 items per page)
        repo.read({}, skip=10, limit=10)
        
        # Verify skip was called with correct value
        mock_cursor.skip.assert_called_with(10)
    
    def test_read_applies_limit_pagination(self):
        """Limit is applied and capped at 500."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        repo.collection.find.return_value = mock_cursor
        
        # Call with limit exceeding cap
        repo.read({}, limit=1000)
        
        # Verify limit was capped at 500
        mock_cursor.limit.assert_called_with(500)
    
    def test_read_caps_limit_at_500(self):
        """Limit cannot exceed 500 for safety."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        repo.collection.find.return_value = mock_cursor
        
        # Try limit of 1000
        repo.read({}, limit=1000)
        
        # Should be capped at 500
        mock_cursor.limit.assert_called_with(500)
    
    def test_read_minimum_limit_is_one(self):
        """Limit must be at least 1."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        repo.collection.find.return_value = mock_cursor
        
        # Try limit of 0
        repo.read({}, limit=0)
        
        # Should be capped at 1 minimum
        mock_cursor.limit.assert_called_with(1)
    
    def test_read_validates_query_type(self):
        """Read validates that query is a dict."""
        repo = AnimalRepository.__new__(AnimalRepository)
        
        with pytest.raises(ValueError):
            repo.read("not a dict")
    
    def test_read_handles_pymongo_error(self):
        """Read returns empty list on database error."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        repo.collection.find.side_effect = Exception("Database error")
        
        result = repo.read({})
        
        assert result == []
    
    def test_read_default_projection_excludes_id(self):
        """Read uses projection that excludes _id by default."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        repo.collection.find.return_value = mock_cursor
        
        # Call without projection
        repo.read({})
        
        # Verify find was called with projection excluding _id
        call_args = repo.collection.find.call_args
        assert call_args[1].get("projection") == {"_id": 0}
    
    def test_read_custom_projection(self):
        """Read uses custom projection if provided."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        repo.collection.find.return_value = mock_cursor
        
        custom_projection = {"breed": 1, "age_upon_outcome_in_weeks": 1}
        repo.read({}, projection=custom_projection)
        
        call_args = repo.collection.find.call_args
        assert call_args[1].get("projection") == custom_projection


class TestAnimalRepositoryCountDocuments:
    """Tests for the count_documents method."""
    
    def test_count_documents_returns_count(self):
        """Count returns document count."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        repo.collection.count_documents.return_value = 42
        
        count = repo.count_documents({"breed": "Lab"})
        
        assert count == 42
    
    def test_count_documents_validates_query(self):
        """Count validates query is a dict."""
        repo = AnimalRepository.__new__(AnimalRepository)
        
        result = repo.count_documents("not a dict")
        
        assert result == 0
    
    def test_count_documents_handles_error(self):
        """Count returns 0 on error."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        repo.collection.count_documents.side_effect = Exception("Error")
        
        result = repo.count_documents({})
        
        assert result == 0


class TestAnimalRepositoryAggregateBreedCounts:
    """Tests for the aggregate_breed_counts method."""
    
    def test_aggregate_breed_counts_returns_list(self):
        """Aggregate returns list of breed counts."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        repo.collection.aggregate.return_value = [
            {"breed": "Lab", "count": 50},
            {"breed": "Terrier", "count": 30},
        ]
        
        result = repo.aggregate_breed_counts({})
        
        assert isinstance(result, list)
        assert len(result) == 2
    
    def test_aggregate_breed_counts_validates_query(self):
        """Aggregate validates query is a dict."""
        repo = AnimalRepository.__new__(AnimalRepository)
        
        with pytest.raises(ValueError):
            repo.aggregate_breed_counts("not a dict")
    
    def test_aggregate_breed_counts_handles_error(self):
        """Aggregate returns empty list on error."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        repo.collection.aggregate.side_effect = Exception("Error")
        
        result = repo.aggregate_breed_counts({})
        
        assert result == []
    
    def test_aggregate_applies_match_filter(self):
        """Aggregate applies match filter to pipeline."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        repo.collection.aggregate.return_value = []
        
        query = {"sex_upon_outcome": "Intact Female"}
        repo.aggregate_breed_counts(query)
        
        # Verify aggregate was called
        assert repo.collection.aggregate.called
        
        # Get the pipeline passed to aggregate
        pipeline = repo.collection.aggregate.call_args[0][0]
        
        # First stage should be $match with the query
        assert pipeline[0]["$match"] == query


class TestAnimalRepositoryPing:
    """Tests for database connectivity."""
    
    def test_ping_returns_true_on_success(self):
        """Ping returns True when database is available."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.client = MagicMock()
        repo.client.admin.command.return_value = None
        
        result = repo.ping()
        
        assert result is True
    
    def test_ping_returns_false_on_timeout(self):
        """Ping returns False on timeout."""
        from pymongo.errors import ServerSelectionTimeoutError
        
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.client = MagicMock()
        repo.client.admin.command.side_effect = ServerSelectionTimeoutError()
        
        result = repo.ping()
        
        assert result is False
    
    def test_ping_returns_false_on_error(self):
        """Ping returns False on any PyMongo error."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.client = MagicMock()
        repo.client.admin.command.side_effect = Exception("Database error")
        
        result = repo.ping()
        
        assert result is False


class TestAnimalRepositoryServerSideSorting:
    """Tests for server-side sorting with multiple fields."""
    
    def test_sort_by_match_score_descending(self):
        """Results can be sorted by match_score (highest first)."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        repo.collection.find.return_value = mock_cursor
        
        # Sort by match_score descending
        repo.read({}, sort=[("match_score", -1)])
        
        mock_cursor.sort.assert_called_with([("match_score", -1)])
    
    def test_sort_by_multiple_fields(self):
        """Results can be sorted by multiple fields."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        repo.collection.find.return_value = mock_cursor
        
        # Sort by score desc, then breed asc
        sort_spec = [("match_score", -1), ("breed", 1)]
        repo.read({}, sort=sort_spec)
        
        mock_cursor.sort.assert_called_with(sort_spec)
    
    def test_sort_order_is_preserved(self):
        """Sort specifications are applied in order."""
        repo = AnimalRepository.__new__(AnimalRepository)
        repo.collection = MagicMock()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        repo.collection.find.return_value = mock_cursor
        
        # Multiple sort specs
        sorts = [("match_score", -1), ("age_upon_outcome_in_weeks", 1), ("breed", 1)]
        repo.read({}, sort=sorts)
        
        # Verify exact sort spec was passed
        mock_cursor.sort.assert_called_with(sorts)
