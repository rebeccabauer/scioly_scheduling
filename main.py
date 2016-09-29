import scheduling
import os

# Create file names
input_file = 'scioly_assignments.json'
input_folder = 'input'
filename = os.path.join(input_folder, input_file)

output_folder = 'output'
base_output_name = 'test'


# Load scioly info from file
events = scheduling.load_events(filename)

# Create a Schedule object
sch = scheduling.Schedule(events)

# Attempt to minimize conflicts:
min_conflict_schedules = scheduling.minimize_conflict(sch, num_results=scheduling.constants.NUM_SCHEDULE_OPTIONS)

# Save the minimum-conflict schedules in CSV files
print "---"
min_conflict_schedules.save_as_csv(base_output_name, output_folder)
print "Done saving files!"
print "---"
print "Science Olympiad scheduling finished."
