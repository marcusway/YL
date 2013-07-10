__author__ = 'margaretsheridan'

############################################################################
############################### TASK 5 #####################################
############################################################################

# JUST KIDDING


#-------------------------
# Task Description
#-------------------------

# This is a stopping task--the subject is presented with
# a dot to which s/he must press unless it turns orange.

#------------------------
# Log File Format
#------------------------

# Dot Locations	 Dot1: (253; 109.3333)	 Dot2: (693; 218.6667)	 Dot3: (913; 546.6667)	 Dot4: (363; 437.3333)
# Calculations	 GoPercentCorrect: 0.5108696	 AvgDistanceFromCenter: 19.82892	 AvgResponseTime: 0.7264586	 StopPercentCorrect: 0.6071429	 AvgTurningTime: 0.5454765
# Practice	 TrialNum	 TurnedOrange	 TurningTime	 Correct	 ReactionTime	 TouchPosition	 DistanceFromCenter
# 	1	 False	0	 False	.	.	.
# 	2	 False	0	 False	.	.	.
# 	3	 False	0	 False	.	.	.
# Trial	 TrialNum	 TurnedOrange	 TurningTime	 Correct	 ReactionTime	 TouchPosition	 DistanceFromCenter
# 	1	 False	0	 False	.	.	.
# 	2	 False	0	 True	0.6972656	 (960; 530)	49.86761
# 	3	 False	0	 False	.	.	.
# 	4	 False	0	 True	0.7102051	 (389; 417)	33.00674
# 	5	 False	0	 False	.	.	.

# There are 100 total "Trial" trials.

#-------------------------
# Compiled Data Format
#-------------------------

# subject	group	 TrialNum	 TurnedOrange	 Correct	 ReactionTime	 TouchPosition	 DistanceFromCenter	prev trial orange
# 1038	12p2	1	 False	 True	0.8833008	 (289; 131)	10.72046
# 1038	12p2	2	 False	 True	0.7955322	 (1059; 628)	14.26224	 False
# 1038	12p2	3	 False	 True	0.7636719	 (812; 236)	20.03008	 False
# 1038	12p2	4	 False	 True	0.8308105	 (309; 133)	10.91982	 False
# 1038	12p2	5	 False	 True	0.7296143	 (1049; 661)	27.46942	 False

# "prev trial orange" is the only value that must be computed from the log file.
# All other data can simply be copied.

#--------------------------
# Code
#--------------------------

def readTask5LogFile(filename, headers=field_names['task5']):
    """
    Takes as an argument the path to
    a log file output from task 5
    of the format specified above and
    returns lists of lists containing
    trial info for both task and practice.
    the subject ID (read from the file name)
    is also returned.
    """

    import csv

    with open(filename, "rU") as logFile:

        # Make a list of lists, one for each line
        # of the file.  csv.reader breaks each row into
        # a list according where the commas are
        logReader = csv.reader(logFile)

        # The top line of the file contains
        # coordinates of the locations where the
        # circle stimuli are presented

        # UNUSED LINES
        logReader.next()  # Dot locations
        logReader.next()  # Summary stats
        logReader.next()  # Practice headers

        # There are a variable number of practice trials
        # Iterate over the lines of the file until we hit the line with
        # the task headers.  Prior to said line, all rows should have
        # an empty first column.
        practice = []
        task = []
        currTrialType = practice

        for line in logReader:
            # Once we hit the row with the task headers,
            # change currTrialType to task so that subsequent
            # rows of data are written to the task list.
            if line[0] == "Trial":
                # Line contains task headers.  Do nothing with it.
                currTrialType = task

            # If we get a row with something other
            # than "Task" in the first column, report an error.
            elif line[0] and not line[0].isspace():
                raise Exception("Error: line of unexpected format in file %s:\n%s" % (filename, line))

            # Add the current row to its appropriate list
            else:
                # Add the current line (as a list) to
                # the appropriate list of lines
                currTrialType.append([cleaned_string(x) for x in line[1:]])  # Don't include the first (blank) entry

        # The first trial has no previous trial, so the
        # previous trial was not Orange.
        task[0].append(False)

        # Iterate over the remaining lines of the file
        for i in range(1, len(task)):

            # If the dot turned orange in the previous trial:
            # (turned orange is the second value in the list
            # for the each task)
            if task[i - 1][1] is True:
            # Set "prev trial orange" to be true.
                task[i].append(True)
            else:
                task[i].append(False)

        task_dict = [dict(zip(headers, trial)) for trial in task]
        practice_dict = [dict(zip(headers[:-1], trial)) for trial in practice]
        return practice_dict, task_dict


def write_to_task_file(task_dict, task_file, field_names, overwrite=False):
    """
    This function takes a list of dictionaries
    and writes them to a .csv file.
    """
    import csv
    import os

    # If the file already exists, we want to append to it
    # without writing header rows.  However, if overwrite
    # is true, the whole file will just be overwritten.
    if os.path.isfile(task_file) and not overwrite:
        with open(task_file, "a") as out:
            writer = csv.DictWriter(out, field_names)
            writer.writerows(task_dict)

    else:  # Open a new file (or overwrite old one) and write to it
        with open(task_file, "w") as out:
            writer = csv.DictWriter(out, field_names)
            writer.writeheader()
            writer.writerows(task_dict)
