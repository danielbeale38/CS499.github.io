def aggregate_breed_counts(self, match_query: dict) -> list[dict]:
    pipeline = [
        {"$match": match_query},
        {"$group": {"_id": "$breed", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"breed": "$_id", "count": 1, "_id": 0}},
    ]
    try:
        return list(self.collection.aggregate(pipeline))
    except PyMongoError as e:
        logger.exception("aggregate_breed_counts failed: %s", e)
        return []

def aggregate_sex_counts(self, match_query: dict) -> list[dict]:
    pipeline = [
        {"$match": match_query},
        {"$group": {"_id": "$sex_upon_outcome", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"sex_upon_outcome": "$_id", "count": 1, "_id": 0}},
    ]
    try:
        return list(self.collection.aggregate(pipeline))
    except PyMongoError as e:
        logger.exception("aggregate_sex_counts failed: %s", e)
        return []

def aggregate_age_summary(self, match_query: dict) -> list[dict]:
    pipeline = [
        {"$match": match_query},
        {"$match": {"age_upon_outcome_in_weeks": {"$type": "number"}}},
        {"$group": {
            "_id": None,
            "min_weeks": {"$min": "$age_upon_outcome_in_weeks"},
            "max_weeks": {"$max": "$age_upon_outcome_in_weeks"},
            "avg_weeks": {"$avg": "$age_upon_outcome_in_weeks"},
        }},
        {"$project": {"_id": 0, "min_weeks": 1, "max_weeks": 1, "avg_weeks": 1}},
    ]
    try:
        return list(self.collection.aggregate(pipeline))
    except PyMongoError as e:
        logger.exception("aggregate_age_summary failed: %s", e)
        return []
