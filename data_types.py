QUANTITY_TYPES = {
    quantity_type: f'HKQuantityTypeIdentifier{quantity_type}' 
    for quantity_type in [
        'Height',
        'BodyMass',
        'VO2Max',
        'WalkingHeartRateAverage',
        'RestingHeartRate',
        'WalkingAsymmetryPercentage',
        'HeadphoneAudioExposure',
        'HeartRateVariabilitySDNN',
        'WalkingDoubleSupportPercentage',
        'WalkingSpeed',
        'WalkingStepLength',
        'EnvironmentalAudioExposure',
        'FlightsClimbed',
        'AppleStandTime',
        'AppleExerciseTime',
        'HeartRate',
        'StepCount',
        'BasalEnergyBurned',
        'DistanceWalkingRunning',
        'ActiveEnergyBurned',
    ]
}


CATEGORY_TYPES = {
    category_type: f'HKCategoryTypeIdentifier{category_type}' 
    for category_type in [
        'SleepAnalysis', 'AppleStandHour'
    ]
}


TYPES = {**CATEGORY_TYPES, **QUANTITY_TYPES}