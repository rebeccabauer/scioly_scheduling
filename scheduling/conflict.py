import numpy as np
import constants


class ConflictTable(object):
    """
    Holds matrices that record conflicts (either values or students/coaches with conflicts) between each pair of events.
    """
    def __init__(self, event_array):
        # Create nested dicts that relate event name and HS/MS status to matrix cooredinates
        self.name_to_index = {}
        for index, event in enumerate(event_array):
            if event.name in self.name_to_index:
                self.name_to_index[event.name][event.hs] = index
            else:
                self.name_to_index[event.name] = {event.hs: index}

        self.num_events = len(event_array)
        matrix_dimensions = [self.num_events, self.num_events]

        # Create numpy matrices to hold various kinds of conflict info
        self.common_kids = np.empty(matrix_dimensions, dtype=object)        # stores sets of kids with conflicts
        self.common_coaches = np.empty(matrix_dimensions, dtype=object)     # Stores coaches if they have conflicts
        self.kid_conflict_scores = np.full(matrix_dimensions, 0)            # Stores conflict scores based on only the kid conflicts (before multiplying by KID_CONFLICT_FACTOR)
        self.coach_conflict_scores = np.full(matrix_dimensions, 0)          # Stores conflict scores based on only coach conflicts (before multiplying by COACH_CONFLICT_FACTOR)
        self.ms_hs_pairs = np.full(matrix_dimensions, 0)                    # If the event pair is corresponding B/C events, this matrix holds a 1.  Otherwise 0.
        self.conflict_scores = np.full(matrix_dimensions, 0)                # Stores resulting conflict scores for every pair of events

        self._fill_conflict_matrices(event_array)

    def _fill_conflict_matrices(self, event_array):
        """
        Fill in the conflict matrices defined at initialization
        :param event_array: Array of events that the matrices record information on
        """
        for col in range(len(event_array)):
            for row in range(col):
                ev1 = event_array[row]
                ev2 = event_array[col]

                # if the events are a B-C pair, register no coach/kid conflicts and record the correnspondence in the ms_hs_pairs matrix
                if ev1.name == ev2.name and ev1.hs != ev2.hs:
                    self.ms_hs_pairs[row, col] = 1
                    continue

                # Add up conflict factors for kids
                kids = event_array[row].get_common_kids(event_array[col])
                if len(kids) is not 0:
                    self.common_kids[row, col] = kids
                    kid_cscore = 0
                    for kid in kids:
                        kid_cscore += constants.CUSTOM_CONFLICT_FACTORS.get(kid, 1)
                    self.kid_conflict_scores[row, col] = kid_cscore

                # Get conflict factor for coach
                common_coach = event_array[row].get_common_coach(event_array[col])
                self.common_coaches[row, col] = common_coach
                if common_coach is not None:
                    self.coach_conflict_scores[row, col] = constants.CUSTOM_CONFLICT_FACTORS.get(common_coach, 1)

        # Generate final conflict scores by multiplying specific conflict matrices by constants and summing the results
        self.conflict_scores = self.coach_conflict_scores*constants.COACH_CONFLICT_FACTOR \
                               + self.kid_conflict_scores*constants.KID_CONFLICT_FACTOR \
                               + self.ms_hs_pairs*constants.SIMULTENAITY_BONUS

    def table_index(self, ev):
        """
        :return: the matrix row/col index of event ev
        """
        return self.name_to_index[ev.name][ev.hs]

    def get_coordinates(self, ev1, ev2):
        """
        :return: row, col coordinates for the interaction between ev1 and ev2
        """
        row = self.table_index(ev1)
        col = self.table_index(ev2)
        if row > col:
            col, row = row, col
        return row, col

    def get_conflict_score(self, ev1, ev2):
        """
        :return: the full conflict score between ev1 and ev2
        """
        row, col = self.get_coordinates(ev1, ev2)
        return self.conflict_scores[row, col]

    def get_kid_conflicts(self, ev1, ev2):
        """
        :return: The set of kids that have conflicts if ev1 and ev2 are scheduled simultaneously
        """
        row, col = self.get_coordinates(ev1, ev2)
        return self.common_kids[row, col]

    def get_coach_conflicts(self, ev1, ev2):
        """
        :return: The coach's name if ev1 and ev2 have the same coach, otherwise None
        """
        row, col = self.get_coordinates(ev1, ev2)
        return self.common_coaches[row, col]

