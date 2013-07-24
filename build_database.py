"""
A script to iterate over log files, add them to database, and
then write the summary data to a file. Example usage:

>$ python build_database.py
Please type the path to your log files folder: YL_DATA_PERU
Please enter the path to your summary data spreadsheet:summary.csv
Overwrite existing summary file (y/n): y
Log files to process: 1237


All Done!



The log folder specified should contain the .csv log files output
from the YL tablet games and ideally only those files.  All files
in the log files folder will be considered as log files, but if a file's
name doesn't fit the log file naming convention, the program will report this
to the user, and that file will be skipped. Responses to the prompt should
be typed without quotes. Path to the log file folder should include the name of
the log folder itself, not just the path to the directory that contains it.  The
same goes for the path to the summary file (actually specify the name of the summary
file, not just to the path to the directory containing it).  Paths should be specified
as either absolute paths or paths relative to the current working directory.  Don't use
'~' to specify a home directory.

In addition to writing to the
comma-separated summary file specified by the user (summary.csv above), this script
also automatically saves 6 task-specific files, each of which contains all trial data
from all subjects for its respective task, to the working directory (the same one in
which this script resides).  In addition, subject data are saved to a shelve database,
which contains all info about the subject.

When the overwrite option is chosen, the summary file, all the task files, and the
shelve database are overwritten as well.  Before choosing to overwrite, you should ensure
that you have access to all of the log files that have been processed previously (except, of course,
those that you don't want to keep), or the information in those files will be lost.

If a single subject has multiple log files for the same task, a warning will be printed to the
screen, and the second such log file encountered by the program will be the one that is used.
In such cases, the user should manually inspect the files to determine which one should be kept.  The
file that is not kept should then be removed from the log files directory and this script should be re-run
in overwrite mode.

"""

import os
import shelve
import cPickle as pickle

import data_classes as dat
import exception_classes as e

# Initialize default values

log_folder = ""
summary_file = ""
overwrite_summary = True
overwrite_task = True
shelve_database = "YL_DATABASE"  # Automatically store the shelve DB in current directory
subjects = {}  # This will store subject data to be added to shelve DB
seen_file_store = "PROCESSED_FILES.pck"  # To keep track of files already processed

# Get User Input

# Prompt the user for the path to their log files folder.
# The user will be continually prompted until they give a path to
# an existing folder.
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
        overwrite_task = False

# Load a pickled list of already seen files
if overwrite_summary is False and os.path.isfile(seen_file_store):
    with open(seen_file_store, "rb") as f:
        already_seen = pickle.load(f)
else:
    already_seen = set()

# Make a list of files not already seen
new_files = set(f for f in os.listdir(log_folder)).difference(already_seen)

# Tell the user how many files have already been processed
if not overwrite_summary:
    print "Number of previously processed log files to date: %d" % len(already_seen)
print "Log files to process: %d" % len(new_files)


# Iterate over all the files
for log_file in [os.path.join(log_folder, f) for f in new_files]:

    # Check if the current subject number is in our dictionary
    with open(log_file, "rU") as in_file:

        # Try to generate a data_file instance from the given log file.  If
        # any of the anticipated errors occur, alert the user to the error and
        # skip the file.
        try:
            log_data = dat.DataFile(in_file)
        except e.BadFileNameError as bfe:
            print "Bad file name!\n%s\n" % bfe
            continue
        except e.TaskNameError as tne:
            print "Invalid task name encountered in processing file: %s\n%s\nSkipping this file\n" % (in_file.name, tne)
            continue
        except e.BadLineError as ble:
            print "Line of unexpected format encountered in log file: %s\n%s\nSkipping this file\n" % (
                in_file.name, ble)
            continue

        # If the subject associated with the log file is not yet in the subject dictionary, create a new entry
        if log_data.key not in subjects:
            subjects[log_data.key] = dat.Subject(log_data.ID, log_data.group, log_data.sibling, log_data.key)

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
    raise

# If we choose to overwrite the summary file, also overwrite the database.
if overwrite_summary:
    db.clear()

for sub in subjects:
    # If there is already a record of the subject in the shelve database,
    # check to see if there is missing task data and update the subject if this is the case
    if sub in db:
        print "Pre-existing DATABASE entry for subject %s." % sub
        for task in subjects[sub].data:
            if task not in db[sub].data:
                updated_sub = db[sub]
                updated_sub.add_data(task, subjects[sub].data[task])
                db[sub] = updated_sub
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