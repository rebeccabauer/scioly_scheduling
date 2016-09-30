import Queue
import csv
import os
import constants


class ScheduleGroup(object):
    """
    An object that holds several different schedule options.
    Used and returned by the minimize_conflict function
    """
    def __init__(self, max_size=5, initial_threshold=20):
        self.schedules = []
        self.mpq = Queue.PriorityQueue()
        self.max_size = max_size
        self.initial_threshold = initial_threshold
        self.threshold = initial_threshold

    def remove_largest_element(self):
        largest = self.mpq.get()
        self.update_threshold()
        return largest

    def put(self, schedule):
        """
        Add a schedule to the ScheduleGroup
        """
        schedule_conflict = schedule.total_conflict()

        # Don't add the new schedule if the mpq is full and it's conflict is already at the threshold
        if self.threshold <= schedule_conflict and self.mpq.qsize() == self.max_size:
            return

        sch = schedule.copy()   # Make a shallow copy so that the schedule's events are not later rearranged
        mpq_item = (-1*schedule_conflict, sch)     # multiply conflict by -1 so that the highest-conflict items will be removed first
        self.mpq.put(mpq_item)

        # remove an element if there are now too many
        if self.mpq.qsize() > self.max_size:
            self.mpq.get()

        self.update_threshold()     # update the threshold

    def update_threshold(self):
        """
        Updates the max conflict threshold for being included in this group
        This threshold is the max conflict of any schedule in the ScheduleGroup
        """
        sch = self.mpq.get()
        self.mpq.put(sch)
        new_threshold = -1*sch[0]
        if new_threshold < self.threshold:
            print "New Threshold: {}".format(new_threshold)
            self.threshold = new_threshold

    def schedule_list(self):
        """
        Returns a list of the schedules in the group
        Warning: This empties the internal priorityqueue
        """
        schedules = []
        while not self.mpq.empty():
            schedules.insert(0, self.mpq.get()[1])
        self.schedules = schedules
        return schedules

    def save_as_csv(self, basename, folder):
        """
        Save the schedules in a collection of csv files
        :param basename: csv file base. Files will be named basename_option0.csv, basename_option1.csv ...
        :param folder: the folder to save in
        """
        schedule_list = self.schedule_list()
        fieldnames = ['Event Name', 'B/C', 'Coach', 'Students']
        print "Writing output to file ..."
        for index, schedule in enumerate(schedule_list):
            filename = '{}_option{}.csv'.format(basename, index)
            filename = os.path.join(folder, filename)
            with open(filename, 'wb') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(['Option {}'.format(index)])
                writer.writerow(['Conflict Score:', schedule.total_conflict()])
                writer.writerow([])
                for index, shift in enumerate(schedule.shifts):
                    students = shift.students_with_conflicts()
                    coaches = shift.coaches_with_conflicts()
                    writer.writerow(['...'])
                    writer.writerow(['Shift {}:'.format(index)])
                    writer.writerow(['Conflict Summary:'])
                    writer.writerow(['Student Conflicts', 'Coach Conflicts', 'Total'])
                    writer.writerow([len(students), len(coaches), len(students)+len(coaches)])
                    writer.writerow([])
                    writer.writerow(['Students with conflicts:'] + students)
                    writer.writerow(['Coaches with conflicts:'] + coaches)
                    writer.writerow([])
                    writer.writerow(fieldnames)
                    for event in shift.events:
                        b_or_c = 'C' if event.hs else 'B'
                        writer.writerow([event.name, event.coach, b_or_c, ', '.join(event.kids)])   # Print schedule
                    writer.writerow([])
            print "Finished writing file {}".format(filename)


def minimize_conflict(schedule, num_results=constants.NUM_SCHEDULE_OPTIONS):
    """
    Function that attempts to minimize schedule conflicts using a recursive search algorithm
    :param schedule: A schedule object to optimize
    :param num_results: The number of the best schedule options to return
    :return: A ScheduleGroup object, which is essentially a collection of the best schedules
    """
    best_groupings = ScheduleGroup(max_size=num_results)
    mpq = Queue.PriorityQueue()
    for event in schedule.events:
        mpq.put((-1 * event.priority, event))       # Populate the priority queue

    def recurse():
        # Base cases
        if schedule.total_conflict() > best_groupings.threshold:
            return
        if schedule.scheduled_events() == schedule.total_events():
            best_groupings.put(schedule)
            print "Possible order found.  " + schedule.status()
            return

        # Dequeue next event
        priority, event = mpq.get()
        conflicts = [shift.event_conflicts(event) for shift in schedule.shifts]
        min_conflict = min(conflicts)

        starter = False
        for index, conflict in enumerate(conflicts):
            if conflict == min_conflict:
                shift = schedule.shifts[index]
                if shift.num_events() == 0:
                    if starter:  # continue if this element has already started its own shift
                        continue
                    else:
                        starter = True
                shift.add_event(event)
                recurse()       # call recursively
                shift.remove_event(event)
        mpq.put((priority, event))

    recurse()
    print "Finished optimizing schedules."
    return best_groupings


