from unittest.mock import MagicMock
from data.mongo_repo import AnimalRepository

def test_aggregate_breed_counts_returns_list():
    repo = AnimalRepository.__new__(AnimalRepository)
    repo.collection = MagicMock()
    repo.collection.aggregate.return_value = [{"breed": "A", "count": 2}]
    out = AnimalRepository.aggregate_breed_counts(repo, {})
    assert out[0]["count"] == 2
