"""
Query service for building MongoDB queries based on rescue filter types.

Provides validation and query construction for rescue dog filtering.
All queries are built server-side to ensure consistency and security.
"""

ALLOWED_FILTERS = {"all", "water", "mountain", "disaster"}


def validate_filter_type(filter_type: str) -> str:
    """
    Validate that filter_type is in the allowed set.
    
    Uses whitelist validation to prevent invalid filters from reaching
    the database layer.
    
    Args:
        filter_type: The filter type to validate
    
    Returns:
        The validated filter_type if valid
    
    Raises:
        ValueError: If filter_type is not in ALLOWED_FILTERS
    
    Examples:
        >>> validate_filter_type("water")
        'water'
        
        >>> validate_filter_type("invalid")
        Traceback (most recent call last):
            ...
        ValueError: Invalid filter type.
    """
    if filter_type not in ALLOWED_FILTERS:
        raise ValueError("Invalid filter type.")
    return filter_type


def build_rescue_query(filter_type: str) -> dict:
    """
    Build MongoDB query for rescue dog filtering based on rescue type.
    
    Each rescue type has specific criteria for suitable dogs:
    
    - water: Water rescue requires dogs comfortable in water environments.
             Preferred breeds: Labrador Retriever Mix, Chesapeake Bay Retriever, Newfoundland
             Sex: Intact Female
             Age: 6 months to 3 years (26-156 weeks)
    
    - mountain: Mountain/wilderness rescue requires large, hardy dogs.
                Preferred breeds: German Shepherd, Alaskan Malamute, Old English Sheepdog,
                                 Siberian Husky, Rottweiler
                Sex: Intact Male
                Age: 6 months to 3 years (26-156 weeks)
    
    - disaster: Disaster/tracking rescue requires athletic, intelligent dogs.
                Preferred breeds: Doberman Pinscher, German Shepherd, Golden Retriever,
                                 Bloodhound, Rottweiler
                Sex: Intact Male
                Age: 5 months to 7 years (20-300 weeks)
    
    - all: No filtering; returns all dogs
    
    Args:
        filter_type: One of {'all', 'water', 'mountain', 'disaster'}
    
    Returns:
        MongoDB query dict that can be passed to collection.find()
    
    Raises:
        ValueError: If filter_type is invalid
    
    Examples:
        >>> query = build_rescue_query("water")
        >>> query["breed"]["$in"]
        ['Labrador Retriever Mix', 'Chesapeake Bay Retriever', 'Newfoundland']
        
        >>> query = build_rescue_query("all")
        >>> query
        {}
    """
    validate_filter_type(filter_type)

    if filter_type == "water":
        return {
            "$and": [
                {"breed": {"$in": ["Labrador Retriever Mix", "Chesapeake Bay Retriever", "Newfoundland"]}},
                {"sex_upon_outcome": "Intact Female"},
                {"age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156}},
            ]
        }

    if filter_type == "mountain":
        return {
            "$and": [
                {"breed": {"$in": ["German Shepherd", "Alaskan Malamute", "Old English Sheepdog", "Siberian Husky", "Rottweiler"]}},
                {"sex_upon_outcome": "Intact Male"},
                {"age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156}},
            ]
        }

    if filter_type == "disaster":
        return {
            "$and": [
                {"breed": {"$in": ["Doberman Pinscher", "German Shepherd", "Golden Retriever", "Bloodhound", "Rottweiler"]}},
                {"sex_upon_outcome": "Intact Male"},
                {"age_upon_outcome_in_weeks": {"$gte": 20, "$lte": 300}},
            ]
        }

    return {}
