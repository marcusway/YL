# Task 1: Paired associated learning task. Subject
# is tasked with learning a hierarchical function mapping
# one type of shape to another.

def readTask1LogFile(logFile, task_number, headers):
    """
    Takes as an argument the path to
    a log file of the format specified above and
    returns two lists of lists: practice and task.
    It also returns the subject ID number
    """

    import csv

    # Make a list of lists, one for each line
    # of the file.  csv.reader breaks each row into
    # a list according where the commas are
    logReader = csv.reader(logFile)

    # The top line contains summary statistics, where each cell contains
    # a key: value pair, except for the first column, which is just "Calculations"

    # UNUSED LINES
    # Stimulus locations, summary data lines unused
    skip_lines(logReader, 2)

    # The subject only has practice trials for task1, not for task6
    if task_number == 1:
        logReader.next()  # Contains practice headers

    # There are a variable number of practice trials.
    # Iterate over the lines of the file until we hit the line with
    # the task headers.  Prior to said line, all rows should have
    # an empty first column.
    practice = []
    task = []
    currTrialType = practice
    prevTrialNum = None

    for line in logReader:
        # Once we hit the row with the task headers,
        # change currTrialType to task so that subsequent
        # rows of data are written to the task list.
        if line[0] == "Task":
            # This line contains task headers.  Do nothing with these.
            currTrialType = task

        # If we get a row with something other
        # than "Task" in the first column, report an error.
        elif line[0] and not line[0].isspace():
            raise Exception("Error: line of unexpected format in file %s:\n%s" % (logFile.name, line))

        # Add the current row to its appropriate list
        else:
            # Add the current line (as a list) to
            # the appropriate list of lines
            currTrialNum = line[1]
            if currTrialNum != prevTrialNum:
                currTrialType.append(get_values(line, (1, 6, 7)))
                prevTrialNum = currTrialNum

    # At this point, practice and task will each be a list of lists, where
    # each sub-list has entries corresponding to the values indicated
    # by the header row of the log file
    for trial in task:
        if int(trial[1]) != 0:
            trial.append(trial[2])
        else:
            trial.append("")

    # Make a list of dictionaries for both practice and task
    # for easy csv writing
    task_dict = [dict(zip(headers, trial)) for trial in task]
    practice_dict = [dict(zip(headers[:-1], trial)) for trial in practice]  # No calculations for practice

    return practice_dict, task_dict  # summary

###############################################################################
################################## TASK 2 #####################################
###############################################################################

#---------------------------
# Task description 
#---------------------------

# This is an inhibition task. In each trial, the subject is presented with 
# a circle that is either yellow or pink.  If it is yellow, the subject
# must touch to the circle.  If it is pink, the subject must 
# press on the side of the screen opposite the circle.  


def readTask2LogFile(logFile, headers):
    """
    Takes as an argument the path to
    a log file output from task 2
    of the format specified above and
    returns lists of lists containing
    trial info for both task and practice.
    the subject ID (read from the file name)
    is also returned.
    """
    import csv

    # Specifies the column numbers of some
    # important categories for the log file.
    PRESSED_SIDE = 6
    GOAL_SIDE = 7

    # Make a list of lists, one for each line
    # of the file.  csv.reader breaks each row into
    # a list according where the commas are
    logReader = csv.reader(logFile)

    # The top line of the file contains
    # coordinates of the locations where the
    # circle stimuli are presented

    # UNUSED LINES
    # logReader.next()  # Dot locations
    # logReader.next()  # Practice headers
    skip_lines(logReader, 2)

    # There are a variable number of practice trials.
    # Iterate over the lines of the file until we hit the line with
    # the task headers.  Prior to said line, all rows should have
    # an empty first column.
    practice = []
    task = []

    # Fill practice, task lists with trial data
    grab_raw_data(logReader, practice, task)

    task_2_determine_switch(task)

    task_dict = [dict(zip(headers, trial)) for trial in task]
    practice_dict = [dict(zip(headers[:-2], trial)) for trial in practice]  # Don't include switch calculations

    return practice_dict, task_dict


############################################################################
############################### TASK 3 #####################################
############################################################################

#-----------------------------
# Task Description
#-----------------------------

# This is a memory task like the one used at the CHPCC.  The subject
# is shown some number of dots, which then disappear. After some variable
# time interval, the subject is asked to press where the dots used to be.

def readTask3LogFile(logFile, headers):
    """
    Takes as an argument the path to
    a log file output from task 3
    of the format specified above and
    returns lists of lists containing
    trial info for both task and practice.
    the subject ID (read from the file name)
    is also returned.
    """

    import csv

    # Make a list of lists, one for each line
    # of the file.  csv.reader breaks each row into
    # a list according where the commas are
    logReader = csv.reader(logFile)

    # UNUSED LINES
    # logReader.next()  # Dot Locations
    # logReader.next()  # Practice headers

    skip_lines(logReader, 2)

    # There are a variable number of practice trials
    # Iterate over the lines of the file until we hit the line with
    # the task headers.  Prior to said line, all rows should have
    # an empty first column.
    practice = []
    task = []

    # Fill practice, task lists
    grab_raw_data(logReader, practice, task)
    # At this point, practice and task will each be a list of lists, where
    # each sub-list has entries corresponding to the values indicated
    # by the header row of the log file

    # Label dot order within trial

    task[0].append(1)

    # Iterate over the remaining lines of the file
    for i in range(1, len(task)):

        # If the current dot was presented as a part
        # of the same trial as the previous one
        if task[i][0] == task[i - 1][0]:
        # The trial number is one more than the last one
            task[i].append(task[i - 1][-1] + 1)
        else:  # It's a new trial, so reset the dot number to 1.
            task[i].append(1)

    task_dict = [dict(zip(headers, trial)) for trial in task]
    practice_dict = [dict(zip(headers[:-1], trial)) for trial in practice]  # Don't include rank info

    return practice_dict, task_dict

############################################################################
############################### TASK 4 #####################################
############################################################################

#-----------------------------
# Task Description
#-----------------------------

# This is an implicit learning task that involves pressing to a dot.  
# It's administered in 5 35-trial blocks.  Blocks 1 and 4 are the same.
# It looks like the alldata file only uses information from the 
# mean block calculations

#----------------------
# Code
#----------------------


def readTask4LogFile(logFile, headers):
    """
    Takes as an argument the path to
    a log file output from task 3
    of the format specified above and
    returns lists of lists containing
    trial info for both task and practice.
    the subject ID (read from the file name)
    is also returned.
    """

    import csv

    # Make a list of lists, one for each line
    # of the file.  csv.reader breaks each row into
    # a list according where the commas are
    logReader = csv.reader(logFile)

    # The top line of the file contains
    # coordinates of the locations where the
    # circle stimuli are presented
    # logReader.next()  # Dot locations
    # logReader.next()  # Practice headers
    skip_lines(logReader, 2)

    # I'm just going to record raw practice data, and then
    # once the real trials start, there will be a line that starts
    # with "Block 1 Calculations".  After that point, I'll
    # only look for the calculations rows and record the
    # data from those rows in "task"

    task = []
    practice = []
    practiceDone = False

    for line in logReader:
    # Add lines to practice until we get to the first block line

        if "Block" in line[0]:
            # The line will look like this:
            # ['Block 4 Calculations', 'PercentCorrect', '91.43%', 'AvgDistanceFromCenter',
            # '32.28865', 'AvgResponseTime', '0.6529274']
            # which we will distill to ['4', '91.43', '32.28865', '0.6529274']

            task.append(get_values(line, (0, 2, 4, 6)))

            if not practiceDone:
                practiceDone = True

        elif line[0] and not line[0].isspace():
            raise Exception("Error: line of unexpected format in file %s:\n%s\n Expected "
                            "blank first column." % (logFile.name, line))

        elif not practiceDone:
            practice.append(line[1:])

    task_dict = [dict(zip(headers, trial)) for trial in task]
    practice_dict = [
        dict(zip(['TrialNum', 'Correct', 'ResponseTime', 'TouchPosition', 'DistanceFromCenter'], trial)) for trial
        in practice]

    return practice_dict, task_dict

############################################################################
############################### TASK 5 #####################################
############################################################################

#---------------------------
# Task Description
#---------------------------

# This is a visual search task, where the subject must press
# to stars of a certain size while avoiding other targets.  


def readTask5LogFile(logFile, headers):
    """
    Takes as an argument the path to
    a log file output from task 6
    of the format specified above and
    returns lists of lists containing
    trial info for both task and practice.
    the subject ID (read from the file name)
    is also returned.
    """

    import csv

    # Make a list of lists, one for each line
    # of the file.  csv.reader breaks each row into
    # a list according where the commas are
    logReader = csv.reader(logFile)

    # Unused line
    # logReader.next()  # Summary statistics.
    skip_lines(logReader, 1)

    practice = []
    task = []
    # The next line contains a summary of the practice.
    for line in logReader:
        if "Practice" in line[0]:
            practice.append(
                [cleaned_string(x) for x in [line[0].split()[1]] + [line[i] for i in range(2, len(line), 2)]])
        elif "Task" in line[0]:
            task.append(
                [cleaned_string(x) for x in [line[0].split()[1]] + [line[i] for i in range(2, len(line), 2)]])

    task_dict = [dict(zip(headers, trial)) for trial in task]
    # Convert the practice lines to dictionaries
    practice_dict = [dict(zip(headers, trial)) for trial in practice]

    # Specify trial number within each dictionary
    for i in range(len(practice_dict)):
        practice_dict[i]['Trial'] = i + 1

    return practice_dict, task_dict


def parse_file_name(file_name):
    """
    Given a log file name of a specific format
    for the YL data, should yield the
    subject number and group (age)
    membership of the subject. A file of the defined format is:

    'PE211005_IIN028_task1_5-15-2013-16-13-32'

    The PE is just a prefix (for Peru?).  The two numbers following
    the PE (21 in this case) indicate membership to a certain group.
    the numbers after 'IIN' specify the device on which the tasks were
    completed.  The number following 'task' indicates to which task
    the log file corresponds.  The string of numbers at the end
    (5-15-2013-16-13-32) correspond to the date and time of completion
    (month-day-year-hour-minute-second)
    """

    import os
    import re
    import warnings

    # Initialize a dictionary, metadata, in which to store
    # all of the information parsed from the file name.
    metadata = {}

    name, extension = os.path.splitext(os.path.basename(file_name))

    # Only accept csv files.
    if extension != ".csv":
        raise Exception("Invalid file format for file: %s\n Not a .csv file" % file_name)

    # Split the file name into components. If filename = 'PE211005_IIN028_task1_5-15-2013-16-13-32',
    # name components should be = ['PE211005', 'IIN028', 'task1', '5-15-2013-16-13-32']
    subject, device, metadata['Task'], date_and_time = name.split("_")

    # Further split the subject string, which should be something like 'PE211005'
    sub_components = re.search(r'(PEs?)(\d\d)(\d+)', subject, re.IGNORECASE)

    # This should split the subject data into match.group(1) = 'PE',
    # match.group(2) = '21', and match.group(3) = 1005.  Note that
    # this assumes that the group number is always two digits, but
    # allows for the subject number to vary in length.
    if not sub_components:
        raise Exception("File name of unexpected format: %s" % file_name)

    if len(sub_components.groups()) == 3:

        # Check if sibling
        if 's' in sub_components.group(1).lower():  # ignoring upper/lower case
            metadata['Sibling'] = True
        else:
            metadata['Sibling'] = False

        # Record group
        metadata['Group'] = sub_components.group(2)  # two digits following PE/PEs
        # Record subject number
        metadata['SubID'] = sub_components.group(3)  # all digits following
        metadata['Device'] = device

        # We expect 6 digits following PE (or PEs).  If there is a different number,
        # warn the user, but don't raise an error.
        if len(metadata['SubID']) != 4:
            warnings.warn("File name of unexpected format: %s\nExpected a 2-digit group number and "
                          "4-digit ID number.\nUsing SubID = %s" % (file_name, metadata['SubID']))

    else:  # The subject info isn't divided as expected
        raise Exception("File name of unexpected format: %s" % file_name)

    # Split the date and time
    split_date = date_and_time.split("-")
    metadata['Date'] = "/".join(split_date[:3])
    metadata['Time'] = ":".join(split_date[3:])

    return metadata


def cleaned_string(in_str):
    """
    A function to translate the string values
    read from log files into values that
    can be manipulated later for data analysis.
    """
    if in_str:
        just_text = in_str.strip().lower()
        if just_text == 'false':
            return False
        elif just_text == 'true':
            return True
        elif just_text == ".":
            return None
        elif just_text.isdigit():
            return int(just_text)
        elif "block" in just_text and "calculations" in just_text:
            return int(just_text.split()[1])
        elif just_text.replace(".", "").strip("%").isdigit():
            return float(just_text.strip("%"))
        elif ";" in just_text:
            return tuple(float(x.strip("()")) for x in just_text.split(";"))
        else:
            return just_text
    else:
        return None


def skip_lines(reader, n):
    """
    :param reader: a csv reader object
    :param n: the number of lines to skip
    :return:
    """
    for i in xrange(n):
        reader.next()


def get_values(line, indices):
    return [cleaned_string(x) for x in (line[y] for y in indices)]


def grab_raw_data(logReader, practice, task):
    currTrialType = practice

    for line in logReader:
        # Once we hit the row with the task headers,
        # change currTrialType to task so that subsequent
        # rows of data are written to the task list.
        if line[0] == "Task":
            # Current line contains task headers; disregard
            currTrialType = task  # Following lines are for task (not practice)

        # If we get a row with something other
        # than "Task" in the first column, report an error.
        elif line[0] and not line[0].isspace():
            raise Exception("Error: line of unexpected format")

        # Add the current row to its appropriate list
        else:
            # Add the current line (as a list) to
            # the appropriate list of lines
            #TODO:  Some function that adds data to the task/practice list in the correct way
            currTrialType.append(get_values(line, range(1, len(line))))


def task_2_determine_switch(task):
    PRESSED_SIDE = 6
    GOAL_SIDE = 7
    task[0] += [True, True]
    for i in range(len(task)):

        # Determine whether it's a switch rule trial
        if i == 0:
            task[i].append(True)
        elif task[i][1] != task[i - 1][1]:
            task[i].append(True)
        else:
            task[i].append(False)

        # Determine if it's a switch side trial. Note that
        # whether or not SidePressed refers to the side of
        # the correct or actual response will have an impact
        # on how this is computed.  Right now, we are assuming
        # that SidePressed refers to the correct side.

        # UPDATE:  SidePressed actually refers to the side that
        # the subject pressed, not (necessarily) where
        # they were supposed to press.

        # Determine the goal side.  task[6] is PressedSide and task[7] is Correct
        if task[i][7] == 1:
            goal_side = task[i][PRESSED_SIDE]
        elif task[i][PRESSED_SIDE] == 'right':
            goal_side = "left"
        elif task[i][PRESSED_SIDE] == 'left':
            goal_side = "right"
        else:  # Side pressed isn't Left or Right
            goal_side = "???"

        # Insert the goal_side according to the output format above
        task[i].insert(GOAL_SIDE, goal_side)

        # Determine if it's a switch-side trial, i.e, the side to which the
        # subject was supposed to press changed.
        prev_goal_side = task[i][GOAL_SIDE]
        curr_goal_side = task[i - 1][GOAL_SIDE]
        if prev_goal_side == "???" or curr_goal_side == "???":
            task[i].append("???")
        elif prev_goal_side != curr_goal_side:
            task[i].append(True)
        else:
            task[i].append(False)