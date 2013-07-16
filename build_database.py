"""
A script to iterate over log files, add them to database, and
then write the summary data to a file.
"""

import os
import shelve
import data_class as dat


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

# If the named output file already exists, see if the user wishes to overwrite the file
if os.path.isfile(summary_file):
    w = ""
    while w not in ['y', 'n']:
        w = raw_input("Overwrite existing summary file (y/n): ")
    if w == "y":
        overwrite_summary = True
    else:
        overwrite_summary = False

print "I'm assuming that the files with individual task data are titled\n" \
      "TASK1.csv, TASK2.csv, ..., TASK6.csv.  If you want to change that " \
      "you have to open me up and do it yourself."

subjects = {}
bad_subs = set()
# Iterate over all the files
for log_file in [os.path.join('YL_DATA_PERU', f) for f in os.listdir('YL_DATA_PERU')]:

    # Check if the current subject number is in our dictionary
    with open(log_file, "rU") as in_file:
        log_data = dat.data_file(in_file)

        if log_data.IDString not in subjects:
            subjects[log_data.IDString] = dat.subject(log_data.ID, log_data.group, log_data.sibling)
            # See if the group and siblinghood are the same
        else:
            if log_data.sibling != subjects[log_data.IDString].sibling:
                print "Conflicting sibling info for subject %s" % log_data.ID
                bad_subs.add(log_data.IDString)
            if log_data.group != subjects[log_data.IDString].group:
                print "Conflicting Group Info for subject: %s" % log_data.ID
                bad_subs.add(log_data.IDString)
            if log_data.task in subjects[log_data.IDString].data:
                print "Multiple %s files for subject %s" % (log_data.task, log_data.ID)
                bad_subs.add(log_data.IDString)

        subjects[log_data.IDString].add_data(log_data.task, log_data)

db = shelve.open("DATABASE1")
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
    overwrite_summary = False
