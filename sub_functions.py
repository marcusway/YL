import exception_classes as e


def read_file(task_number, logFile, task_headers, practice_headers):
    """

    :param task_number: a string, one of 'task1', 'task2', ..., 'task3'
    :param logFile: an open file object corresponding to a YL log file.
    :param task_headers: a list of names corresponding to the information we want to parse from the log file
    :param practice_headers: a list of names corresponding to data we wish to parse from practice trials in the log file
    :return: two lists of dictionaries, one for practice data and one for task data.  The returned dictionary keys are
             given by the names in practice_headers and task_headers, respectively

    This function is called by the data_file class method, parse_file_data with arguments given by
    class attributes.
    """

    import csv

    logReader = csv.reader(logFile)

    # Check if the task number argument is valid
    if task_number not in ['task1', 'task2', 'task3', 'task4', 'task5', 'task6']:
        raise e.TaskNameError(task_number)

    # Skip over unused metadata at the top of the file (different tasks have different numbers of unused lines)
    if task_number in ['task1', 'task2']:
        skip_lines(logReader, 3)
    else:
        skip_lines(logReader, 2)

    # Initialize empty practice and task lists to store data trial by trial
    task = []
    practice = []

    # Call on task-specific parser functions to read data from log_file and store appropriate data in
    # task and practice lists
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

    # Return two lists of dictionaries, the first of which corresponds to practice data, the second of
    # which holds the actual trial data.
    return [dict(zip(practice_headers, trial)) for trial in practice], [dict(zip(task_headers, trial)) for trial in
                                                                        task]


def cleaned_string(in_str):
    """
    A function to translate the string values
    read from log files into values that
    can be manipulated later for data analysis.

    :param in_str: a string from YL log file
    :return just_text:  a cleaned version of in_str,
                        changed to a different data type.
    """
    if in_str:  # If it isn't the empty string

        # Make all lower-case, get rid of whitespace
        just_text = in_str.strip().lower()

        # Convert Boolean values
        if just_text == 'false':
            return False
        elif just_text == 'true':
            return True

        # A "." is used when there is missing data in the log files.
        # Return None when this is encountered.
        elif just_text == ".":
            return None

        # If the string is all numerical (i.e., all members of the string are numerical and there is no decimal point)
        # return it as an int
        elif just_text.isdigit():
            return int(just_text)

        # Special for task5, which is done in blocks
        elif "block" in just_text and "calculations" in just_text:
            return int(just_text.split()[1])

        # Convert percentages to floats
        elif just_text.replace(".", "").strip("%").isdigit():
            return float(just_text.strip("%"))

        # Coordinate values are often given in (x;y) format.  Convert to tuple(x,y)
        elif ";" in just_text:
            return tuple(float(x.strip("()")) for x in just_text.split(";"))
        else:
            return just_text
    else: # If it's the empty string, return None
        return None


def skip_lines(reader, n):
    """
    Most of the log files have 2 or 3 lines at the top of the file containing some sort of metadata
    that isn't used in these analyses.  This function just skips the number of lines specified by argument, n.
    :param reader: a csv reader object
    :param n: the number of lines to skip (an int)
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
    """
    Given trial data from task 3 (in the list of lists form generated in
    the function read_file(), task3_determine_dot_order appends a value
    indicating the order in which the dots were pressed (or at least
    in which they appear on the log file)

    :param task: a list of lists, where each nested list corresponds to a dot
    :return None:  the input is modified in place
    """

    task[0].append(1)

    # Iterate over the remaining lines of the file
    for i in range(1, len(task)):

        # If the current dot was presented as a part
        # of the same trial as the previous one
        if task[i][0] == task[i - 1][0]:
            # Increment the trial number
            task[i].append(task[i - 1][-1] + 1)
        else:  # It's a new trial, so reset the dot number to 1.
            task[i].append(1)


def task1_get_data(logReader, practice, task):
    """
    :param logReader:
    :param practice:
    :param task:
    :return: None: task is modified in place
    """
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




