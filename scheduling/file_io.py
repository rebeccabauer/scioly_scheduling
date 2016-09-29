import csv
import json
from schedule_components import Event


def events_from_dict(event_dict):
    """
    Create a list of events from a dict of event info
    """
    all_events = []
    for key, value in event_dict.iteritems():
        all_events.append(Event(name=key,
                                kids=value['kids'],
                                coach=value['coach'],
                                hs=True))
    return all_events


def events_from_json(filename):
    """
    Create a list of events from a JSON file of event info
    TODO: Incorporate whether an event is marked as B or C
    """
    with open(filename) as ifile:
        event_dict = json.load(ifile)
    return events_from_dict(event_dict)


def events_from_csv(filename):
    """
    Note: I haven't tested this function because I don't have a csv version of the event assignments.
    Please test this before use Matthew!
    """
    # TODO: add a way to specify if each event is middle school or high school - we need this so we can break them up if necessary for scheduling purposes

    all_events = []
    with open(filename) as ifile:
        event_reader = csv.reader(filename, dialect='excel')
        event_reader.next()     # skip column names
        for line in event_reader:
            e = Event(
                name=line[0],
                kids=line[1].split(','),
                coach=line[2])
            all_events.append(e)

    return all_events


def events_from_mattheroni(filename):
    """
    Load events from Matthew's old custom file format
    TODO: Incorporate whether an event is marked as B or C into the events produced
    """
    event_dict = {}
    with open(filename) as fh:
        for line in fh:
            line = line.rstrip()

            # deal with skippable lines
            if not line:  # blank line
                continue
            if line[0] == '#':  # comment line
                continue

            # normal assignment line
            spl = line.split(';')

            build = spl[0][0] == '!'
            event = spl[0][1:]

            people = spl[1].split(',')
            coach = people.pop(-1)
            if coach == "none":
                coach = None
            kids = people

            event_dict[event] = {
                'build_event': build,
                'coach': coach,
                'kids': kids
            }

    return events_from_dict(event_dict)


def load_events(filename):
    """
    Load events from file.
    Calls more specific file-loading functions depending on filename extension
    """
    print('Loading events...')

    file_ext = filename.split('.')[-1]      # Don't use this function on files without extensions

    if file_ext == 'json':
        return events_from_json(filename)
    elif file_ext == 'csv':
        return events_from_csv(filename)
    elif file_ext == 'txt':                 # TODO: change this behavior if Matthew's file format is updated or has a different extension
        return events_from_mattheroni(filename)

    print "ERROR: File type not recognized"
