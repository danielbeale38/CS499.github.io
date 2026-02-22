// db_setup.js
// MongoDB collection validation + indexes for Grazioso Salvare (AAC animals)

use aac;

// Validation: require core fields used by filters/ranking and enforce types/ranges.
// "moderate" allows existing bad docs to remain but blocks new/updated invalid ones.
db.runCommand({
  collMod: "animals",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["breed", "sex_upon_outcome", "age_upon_outcome_in_weeks"],
      properties: {
        breed: {
          bsonType: "string",
          description: "Required string"
        },
        sex_upon_outcome: {
          bsonType: "string",
          description: "Required string"
        },
        age_upon_outcome_in_weeks: {
          bsonType: ["int", "long", "double", "decimal"],
          minimum: 0,
          description: "Required non-negative number"
        },
        // Optional geolocation fields (only validated when present)
        location_lat: {
          bsonType: ["double", "decimal", "int", "long"],
          minimum: -90,
          maximum: 90
        },
        location_long: {
          bsonType: ["double", "decimal", "int", "long"],
          minimum: -180,
          maximum: 180
        }
      }
    }
  },
  validationLevel: "moderate"
});

// Indexing choices aligned to your rescue filters and sort patterns.
db.animals.createIndex(
  { breed: 1, sex_upon_outcome: 1, age_upon_outcome_in_weeks: 1 },
  { name: "idx_rescue_filter" }
);

// If you commonly sort by age, this supports that.
db.animals.createIndex(
  { age_upon_outcome_in_weeks: 1 },
  { name: "idx_age" }
);
