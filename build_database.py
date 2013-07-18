"""
A script to iterate over log files, add them to database, and
then write the summary data to a file.
"""

import os
import shelve
import cPickle as pickle
import data_classes as dat
import exception_classes as e

# Initialize default values

log_folder        = ""
summary_file      = ""
overwrite_summary = False
overwrite_task    = True
shelve_database   = ".YL_DATABASE"  # Automatically store the shelve DB in code directory
subjects          = {}
seen_file_store   = ".PROCESSED_FILES.pck"

# Load a pickled list of already seen files
if os.path.isfile(seen_file_store):
    with open(seen_file_store, "rb") as f:
        already_seen = pickle.load(f)
else:
    already_seen = set()

print "Number of previously processed log files to date: %d" % len(already_seen)
# Get User Input

# Prompt the user for the path to their log files folder.
# The user will be continually prompted until they give a real folder.
while not os.path.isdir(log_folder):
    log_folder = raw_input("Please type the path to your log files folder: ")

# Get user input for summary file
summary_file = raw_input("Please enter the path to your summary data spreadsheet:")

# Make sure they haven't just given you a directory
while os.path.isdir(summary_file):
    summary_file = raw_input("%s is a directory.  Please enter a valid file name: " % summary_file)

# If the named output file already exists, see if the user wishes to overwrite the file
if os.path.isfile(summary_file):
    w = ""
    while w not in ['y', 'n']:
        w = raw_input("Overwrite existing summary file (y/n): ")
    if w == "y":
        overwrite_summary = True
        overwrite_task = True
    else:
        overwrite_summary = False
        overwrite_task = True

# Make a list of files not already seen
new_files = set(f for f in os.listdir(log_folder)).difference(already_seen)

# Iterate over all the files
for log_file in [os.path.join(log_folder, f) for f in new_files]:

    # Check if the current subject number is in our dictionary
    with open(log_file, "rU") as in_file:

        # Try to generate a data_file instance from the given log file.  If
        # any of the anticipated errors occur, alert the user to the error and
        # skip the file.
        try:
            log_data = dat.data_file(in_file)
        except e.BadFileNameError as bfe:
            print "Invalid file name format for file: %s\n%s\nSkipping this file.\n" % (in_file.name, bfe)
            continue
        except e.TaskNameError as tne:
            print "Invalid task name encountered in processing file: %s\n%s\nSkipping this file\n" % (in_file.name, tne)
            continue
        except e.BadLineError as ble:
            print "Line of unexpected format encountered in log file: %s\n%s\nSkipping this file\n" % (in_file.name, ble)
            continue

        # If the subject associated with the log file is not yet in the subject dictionary, create a new entry
        if log_data.key not in subjects:
            subjects[log_data.key] = dat.subject(log_data.ID, log_data.group, log_data.sibling, log_data.key)

        # If there is an existing subject, check to make sure subject data matches (sibling, group)
        else:
            # Check if there are multiple task files for the given subject for the given task number
            # (e.g. see if subject PE231010 has more than one task1 log file)
            if log_data.task in subjects[log_data.key].data:
                print "Multiple %s files for subject %s:" % (log_data.task, log_data.key)

        # Update the corresponding subject's data dictionary with the data from the log file object
        subjects[log_data.key].add_data(log_data.task, log_data)
        already_seen.add(os.path.basename(log_file))

# Update the set of already seen files.
with open(seen_file_store, "wb") as f:
    pickle.dump(already_seen, f)

# Write the data to a shelve database
try:
    db = shelve.open(shelve_database)
except IOError as io:
    print "Problem opening database file: %s\nError: %s" % (shelve_database, io)

for sub in subjects:
    # If there is already a record of the subject in the shelve database,
    # check to see if there is missing task data and update the subject if this is the case
    if sub in db:
        print "Pre-existing DATABASE entry for subject %s." % sub
        for task in subjects[sub].data:
            if task not in db[sub].data:
                update = db[sub]
                update.add_data(task, subjects[sub].data[task])
                db[sub] = update
    else:
        db[sub] = subjects[sub]
db.close()

# Iterate over the new dictionary
for sub in subjects:
    subjects[sub].write_summary(summary_file, overwrite=overwrite_summary)

    # After the first call to write summary, we want to continue to write
    # to the same file instead of overwriting every time.
    overwrite_summary = False

    for task in subjects[sub].data:
        subjects[sub].dump_trial_by_trial(task, task + '.csv', overwrite=overwrite_task)

    #TODO We're assuming here that the first subject will have task data for all 6 tasks.
    overwrite_task = False

print "\n\nAll Done!\n\n"