class ReferenceProfile:
    # stores the participant's baseline heart rate
    # heart rate is kept private and checked through a property
    def __init__(self, heart_rate):
        self.heart_rate = heart_rate  # goes through the setter below

    @staticmethod
    def is_realistic(value):
        # simple check used by the setter, doesn't need self
        if type(value) != int and type(value) != float:
            return False
        return 30 <= value <= 120

    @property
    def heart_rate(self):
        return self._heart_rate

    @heart_rate.setter
    def heart_rate(self, value):
        if not self.is_realistic(value):
            raise ValueError("baseline heart rate must be between 30 and 120")
        self._heart_rate = value


class Participant:
    # a participant has a reference profile (composition)
    def __init__(self, participant_id, name, reference):
        self.participant_id = participant_id
        self.name = name
        self.reference = reference


class Session:
    # one training session: a participant + their observations
    def __init__(self, session_id, participant, observations):
        self.session_id = session_id
        self.participant = participant
        self.observations = observations