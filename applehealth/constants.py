"""Apple Health type identifiers and output file names."""

HEART_RATE_TYPE = "HKQuantityTypeIdentifierHeartRate"
HRV_TYPE = "HKQuantityTypeIdentifierHeartRateVariabilitySDNN"
STEP_COUNT_TYPE = "HKQuantityTypeIdentifierStepCount"
ACTIVE_ENERGY_TYPE = "HKQuantityTypeIdentifierActiveEnergyBurned"

QUANTITY_TYPES: dict[str, str] = {
    HEART_RATE_TYPE: "heart_rate",
    HRV_TYPE: "hrv",
    STEP_COUNT_TYPE: "step_count",
    ACTIVE_ENERGY_TYPE: "active_energy",
}

SQLITE_FILENAME = "health.sqlite"
HEART_RATE_CSV = "HeartRate.csv"
HRV_CSV = "HRV.csv"
WORKOUTS_CSV = "Workouts.csv"
STEPS_CSV = "Steps.csv"
ACTIVE_ENERGY_CSV = "ActiveEnergy.csv"
SUMMARY_JSON = "summary.json"
SUMMARY_MD = "summary.md"

DEFAULT_BATCH_SIZE = 5_000
