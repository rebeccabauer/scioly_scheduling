
# Factors to prioritize scheduling large events and build events.  Larger values increase prioritization.
SIZE_FACTOR = 1
BUILD_EVENT_FACTOR = 1.2

# Factors to weight kid and coach conflicts.  Larger values penalize conflicts more.
KID_CONFLICT_FACTOR = 1
COACH_CONFLICT_FACTOR = 0.9

# This is a bonus for HS and MS events that take place at the same time
# It is negative to in order to give these event pairs very low conflict values
# The more negative this value, the larger the benefit for MS and HS events to run simultaneously
SIMULTENAITY_BONUS = -1

# List of build events.  Events in this list will be assigned higher priority for meeting without conflicts.
BUILD_EVENTS = ["Bottle Rocket", "Chem Lab", "Electric Vehicle", "Experimental Design",
                "Forensics", "Game On", "Helicopters", "Mission Possible", "Robot Arm",
                "Scrambler", "Towers", "Wind Power", "Wright Stuff", "Write It Do It"]


# A dict of custom conflict factors in case you want a coach or student with a conflict to be weighted differently
# Conflicts for people in this dict will be multiplied by the specified value during conflict score calculations,
# in addition to the standard kid or coach conflict factor.
# Example: if a kid has a custom conflict factor of 0.5, their resulting conflict factor is 0.5 times the standard kid conflict factor
CUSTOM_CONFLICT_FACTORS = {
    "Matt": 0.5,
    "Ian": 0.7
}

# Number of top schedule options to be returned
# Each of the schedule options will be printed to a different csv file
NUM_SCHEDULE_OPTIONS = 10


