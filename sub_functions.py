import exception_classes as e

def read_file(task_number, logFile, task_headers, practice_headers):

    import csv

    logReader = csv.reader(logFile)

    if task_number not in ['task1', 'task2', 'task3', 'task4', 'task5', 'task6']:
        raise e.TaskNameError(task_number)

    if task_number in ['task3', 'task5', 'task6', 'task4']:
        skip_lines(logReader, 2)
    else:
        skip_lines(logReader, 3)

    task = []
    practice = []

    if task_number == 'task1' or task_number == 'task6':
        task1_get_data(logReader, practice, task)

    elif task_number == 'task2' or task_number == 'task3':
        grab_raw_data(logReader, practice, task)

        if task_number == 'task2':
            task_2_determine_switch(task)
        else:
            task3_determine_dot_order(task)

    elif task_number == 'task4':
        task4_get_data(logReader, practice, task)

    elif task_number == 'task5':
        task5_get_data(logReader, practice, task)

    return [dict(zip(practice_headers, trial)) for trial in practice], [dict(zip(task_headers, trial)) for trial in
                                                                        task]


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
        raise e.BadFileNameError(file_name)

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
        raise e.BadFileNameError(file_name)

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
        raise e.BadFileNameError(file_name)

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
            raise e.BadLineError

        # Add the current row to its appropriate list
        else:
            # Add the current line (as a list) to
            # the appropriate list of lines
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


def task3_determine_dot_order(task):
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


def task1_get_data(logReader, practice, task):
    currTrialType = practice
    prevTrialNum = None

    for line in logReader:
    # Once we hit the row with the task headers,
    # change currTrialType to task so that subsequent
    # rows of data are written to the task list.
        if line[0] == "Task":
            # This line contains task headers.  Do nothing with these.
            currTrialType = task
        elif cleaned_string(line[0]) == 'practice':
            pass

        # If we get a row with something other
        # than "Task" in the first column, report an error.
        elif line[0] and not line[0].isspace():
            raise e.BadLineError(line)

        # Add the current row to its appropriate list
        else:
            # Add the current line (as a list) to
            # the appropriate list of lines
            currTrialNum = line[1]
            if currTrialNum != prevTrialNum:
                currTrialType.append(get_values(line, (1, 6, 7)))
                prevTrialNum = currTrialNum
        for trial in task:
            if int(trial[1]) != 0:
                trial.append(trial[2])
            else:
                trial.append("")


def task4_get_data(logReader, practice, task):
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
            raise e.BadLineError

        elif not practiceDone:
            practice.append(line[1:])


def task5_get_data(logReader, practice, task):
    for line in logReader:
        if "Practice" in line[0]:
            practice.append(
                [cleaned_string(x) for x in list([line[0].split()[1]] + [line[i] for i in range(2, len(line), 2)])])
        elif "Task" in line[0]:
            task.append(
                [cleaned_string(x) for x in list([line[0].split()[1]] + [line[i] for i in range(2, len(line), 2)])])




