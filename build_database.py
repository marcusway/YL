"""
A script to iterate over log files, add them to database, and
then write the summary data to a file.
"""

import os
import shelve
import data_classes as dat
import exception_classes as e


log_folder = ""
summary_file = ""
task_files = ""
overwrite_summary = False
overwrite_task = False

# Prompt the user for the path to their log files folder.
# The user will be continually prompted until they give a real folder.
while not os.path.isdir(log_folder):
    log_folder = raw_input("Please type the path to your log files folder: ")

# Get user input for summary file
summary_file = raw_input("Please enter the path to your summary data spreadsheet:")

# Ask user for path to shelve database file
shelve_database = raw_input("Please enter the path to your shelve database: ")

# If the named output file already exists, see if the user wishes to overwrite the file
if os.path.isfile(summary_file):
    w = ""
    while w not in ['y', 'n']:
        w = raw_input("Overwrite existing summary file (y/n): ")
    if w == "y":
        overwrite_summary = True
    else:
        overwrite_summary = False


subjects = {}
bad_subs = set()
# Iterate over all the files
for log_file in [os.path.join(log_folder, f) for f in os.listdir(log_folder)]:

    # Check if the current subject number is in our dictionary
    with open(log_file, "rU") as in_file:

        # Try to generate a data_file instance from the given log file.  If
        # any of the anticipated errors occur, alert the user to the error and
        # skip the file.
        try:
            log_data = dat.data_file(in_file)
        except e.BadFileNameError as bfe:
            print "Invalid format for file: %s\n%s\nSkipping this file." % (in_file, bfe)
            continue
        except e.TaskNameError as tne:
            print "Invalid task name encountered in processing file: %s\n%s\nSkipping this file" % (in_file, tne)
            continue
        except e.BadLineError as ble:
            print "Line of unexpected format encountered in file: %s\n%s\nSkipping this file" % (in_file, ble)
            continue

        # If the subject associated with the log file is not yet in the subject dictionary, create a new entry
        if log_data.IDString not in subjects:
            subjects[log_data.IDString] = dat.subject(log_data.ID, log_data.group, log_data.sibling)

        # If there is an existing subject, check to make sure subject data matches (sibling, group)
        else:
            # Check if sibling data from log file matches that in the subject object
            if log_data.sibling != subjects[log_data.IDString].sibling:
                print "Conflicting sibling info for subject %s" % log_data.ID
                bad_subs.add(log_data.IDString)

            # Check if the group number matches
            if log_data.group != subjects[log_data.IDString].group:
                print "Conflicting Group Info for subject: %s" % log_data.ID
                bad_subs.add(log_data.IDString)

            # Check if there are multiple task files for the given subject for the given task number
            # (e.g. see if subject PE231010 has more than one task1 log file)
            if log_data.task in subjects[log_data.IDString].data:
                print "Multiple %s files for subject %s:" % (log_data.task, log_data.IDString)
                bad_subs.add(log_data.IDString)

        # Update the corresponding subject's data dictionary with the data from the log file object
        subjects[log_data.IDString].add_data(log_data.task, log_data)

db = shelve.open(shelve_database)
try:
    for sub in subjects:
        if sub in db:
            print "There is already an entry for subject %s." % sub
        else:
            db[sub] = subjects[sub]
except: # Make sure we close the database no matter what
    print "An error occurred writing to database"
finally:
    db.close()

# Iterate over the new dictionary
for sub in subjects:
    subjects[sub].write_summary(summary_file, overwrite=overwrite_summary)

    # After the first call to write summary, we want to continue to write
    # to the same file instead of overwriting every time.
    overwrite_summary = False
