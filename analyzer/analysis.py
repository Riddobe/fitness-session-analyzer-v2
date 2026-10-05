class IntensityClassifier:
    # base class: decides resting / moderate / high from heart rate alone
    HIGH_CUTOFF = 45
    MODERATE_CUTOFF = 15

    def classify(self, observations, baseline_heart_rate):
        total = 0
        for obs in observations:
            total += obs["heart_rate"]
        average_hr = total / len(observations)
        elevation = average_hr - baseline_heart_rate

        if elevation >= self.HIGH_CUTOFF:
            label = "high_activity"
        elif elevation >= self.MODERATE_CUTOFF:
            label = "moderate_activity"
        else:
            label = "resting"

        rounded_elevation = round(elevation, 1)
        explanation = f"average heart rate was {rounded_elevation} bpm above baseline"
        return label, explanation


class SessionClassifier(IntensityClassifier):
    # adds the insufficient-data and recovery checks on top of the base class
    MIN_OBSERVATIONS = 4

    def classify(self, observations, baseline_heart_rate):
        if len(observations) < self.MIN_OBSERVATIONS:
            return "insufficient_data", "not enough usable observations to classify"

        if check_recovery(observations, baseline_heart_rate):
            return "recovering", "heart rate and activity dropped near the end of the session"

        return super().classify(observations, baseline_heart_rate)


def check_recovery(observations, baseline_heart_rate):
    # checks if heart rate and activity go down near the end
    if len(observations) < 6:
        return False

    third = len(observations) // 3
    early = observations[:third]
    late = observations[-third:]

    early_hr_total = 0
    for obs in early:
        early_hr_total += obs["heart_rate"]
    early_hr = early_hr_total / len(early)

    late_hr_total = 0
    for obs in late:
        late_hr_total += obs["heart_rate"]
    late_hr = late_hr_total / len(late)

    early_activity_total = 0
    for obs in early:
        early_activity_total += obs["activity_level"]
    early_activity = early_activity_total / len(early)

    late_activity_total = 0
    for obs in late:
        late_activity_total += obs["activity_level"]
    late_activity = late_activity_total / len(late)

    started_elevated = early_hr - baseline_heart_rate >= 20
    heart_rate_dropped = (early_hr - late_hr) >= 15
    activity_dropped = (early_activity - late_activity) >= 0.20

    return started_elevated and heart_rate_dropped and activity_dropped


def analyze_session(session, classifier):
    # runs the analysis for one session and returns a result dictionary
    label, explanation = classifier.classify(
        session.observations, session.participant.reference.heart_rate
    )
    return {
        "session_id": session.session_id,
        "participant_id": session.participant.participant_id,
        "participant_name": session.participant.name,
        "classification": label,
        "explanation": explanation,
        "observation_count": len(session.observations),
    }