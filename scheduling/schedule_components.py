import copy
import constants
from conflict import ConflictTable


class Schedule(object):
    """
    A full science olympiad schedule.
    """
    def __init__(self, events, shifts=None, conflict_table=None, num_shifts=4):
        """
        Creates a 'schedule' object from a list of events
        :param events: A list of events to be scheduled
        :param shifts: A list of pre-filled shifts (empty shifts will be created if this parameter is not passed)
        :param conflict_table: A conflict table. Will be generated based on events if not passed.
        :param num_shifts: The number of science olympiad shifts to schedule.
        """
        self.events = events
        self.shifts = shifts
        self.conflict_table = conflict_table

        # Create conflict table and shifts if not passed as parameters
        if conflict_table is None:
            self.conflict_table = ConflictTable(events)
        if shifts is None:
            self.shifts = [Shift(self.conflict_table) for i in range(num_shifts)]

    def total_conflict(self):
        """
        :return: The sum of the conflict scores for each shift in the schedule
        """
        conflicts = [shift.conflict_sum for shift in self.shifts]
        return sum(conflicts)

    def scheduled_events(self):
        """
        :return: The number of events that hve been scheduled so far
        """
        scheduled = [shift.num_events() for shift in self.shifts]
        return sum(scheduled)

    def total_events(self):
        """
        :return: Number of events in the schedule (includes scheduled events and events that have yet to be scheduled)
        """
        return len(self.events)

    def status(self):
        return "Total collision score: {}".format(self.total_conflict())

    def copy(self):
        """
        :return: A copy of the schedule.
        Event lists within shifts are shallow-copied, conflict table and event list are by reference
        """
        shift_copies = [shift.copy() for shift in self.shifts]
        schedule_copy = Schedule(self.events, shifts=shift_copies, conflict_table=self.conflict_table)
        return schedule_copy


class Shift(object):
    """
    An object that stores the events and event conflict info for a single Science Olympiad shift
    """
    def __init__(self, conflict_table):
        self.events = []
        self.conflict_values = []

        self.conf_table = conflict_table
        self.conflict_sum = 0

    def num_events(self):
        """
        :return: the number of events in the shift
        """
        return len(self.events)

    def add_event(self, event):
        """
        Add an event to the shift
        """
        if event not in self.events:
            # recalculate conflict info
            cfsum = 0
            for ev in self.events:
                cf = self.conf_table.get_conflict_score(ev, event)
                cfsum += cf
            self.conflict_sum += cfsum
            self.events.append(event)
            self.conflict_values.append(cfsum)

    def remove_event(self, event):
        """
        Remove a given event from the shift
        """
        i = self.events.index(event)
        event = self.events.pop(i)
        conflict_value = self.conflict_values.pop(i)
        self.conflict_sum -= conflict_value
        return event

    def event_conflicts(self, event):
        """
        Get the conflict score increase that would result if the Event 'event' was added to this shift
        """
        cfsum = 0
        for ev in self.events:
            cf = self.conf_table.get_conflict_score(ev, event)
            cfsum += cf
        return cfsum

    def calculate_conflict_sum(self):
        csum = 0
        for i in range(len(self.events)):
            for j in range(i):
                csum += self.conf_table.get_conflict_score(self.events[i], self.events[j])
        return csum

    def students_with_conflicts(self):
        """
        :return: a list of the students in this shift who have conflicts
        """
        students = []
        for i in range(len(self.events)):
            for j in range(i):
                overlap = self.conf_table.get_kid_conflicts(self.events[i], self.events[j])
                if overlap is not None:
                    students += list(overlap)
        return students

    def coaches_with_conflicts(self):
        """
        :return: a list of the coaches in this shift who have conflicts
        """
        coaches = []
        for i in range(len(self.events)):
            for j in range(i):
                coach = self.conf_table.get_coach_conflicts(self.events[i], self.events[j])
                if coach is not None:
                    coaches.append(coach)
        return coaches

    def copy(self):
        """
        :return: a shallow copy of the shift
        """
        shift_copy = Shift(self.conf_table)
        shift_copy.events = copy.copy(self.events)      # make a shallow copy of the event list so that events themselves are not copied but list order will not be inadvertently changed
        shift_copy.conflict_values = self.conflict_values
        shift_copy.conflict_sum = self.conflict_sum
        return shift_copy


class Event(object):
    """
    An object that stores information on a single event
    """
    def __init__(self, name, kids=None, coach=None, hs=True):
        """
        :param name: Event name
        :param kids: List of kids who are in the event
        :param coach: The coach name, if there is a coach, or None if no coach
        :param hs: This value should be true if it's an HS event, false if it's a MS event.
               MS and HS events should NOT be combined into single events, it will result in a larger number of schedule conflicts.
        """
        self.name = name
        self.kids = kids
        self.coach = coach
        self.hs = hs
        self.build_event = (name in constants.BUILD_EVENTS)

        # Set scheduling priority for this event
        # Note: this may need to be adjusted by adding a parameter that covers whether the event has a MS or HS counterpart that it could be paired with
        self.priority = constants.SIZE_FACTOR * len(self.kids) + constants.BUILD_EVENT_FACTOR * int(self.build_event)

    def __eq__(self, other):
        # Check equality based on event name and whether it is HS or MS
        return isinstance(other, Event) and other.name == self.name and self.hs == other.hs

    def get_common_kids(self, other_event):
        """
        :param other_event: an Event object
        :return: a set of kids that are common between this event and the other event
        """
        names1 = set(self.kids)
        names2 = set(other_event.kids)
        return names1.intersection(names2)

    def get_common_coach(self, other_event):
        """
        :param other_event: an Event object
        :return: the coach's name if the two events have the same coach, otherwise None
        """
        if self.coach is not None and self.coach == other_event.coach:
            return self.coach
        return None

    def summary_dict(self):
        """
        :return: A dict summarizing event information. Useful for printing.
        """
        summary = {
            'Event Name': self.name,
            'Coach': self.coach,
            'Students': self.kids
        }
        return summary






