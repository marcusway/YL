# An attempt to use some OOP to solve this problem.
import exception_classes as e


class subject:
    """
    A class containing all data (including trial by trial and summary statistics)
    and metadata (subject ID, device number, sibling, time) from the output task
    log files.
    """

    def __init__(self, ID, group, sibling, key):

        self.ID = ID       # Should be a four digit number
        self.group = group    # Generally a two-digit number
        self.sibling = sibling  # True/False bool
        self.data = {}       # A dictionary to be filled with data_file objects
        self.key = key

    def __str__(self):
        """
        String representation of the object
        """
        return '<Subject Number: %s Group: %s Sibling: %s>' % (self.ID, self.group, str(self.sibling))


    def add_data(self, task, data_object):

        """
        Updates the subject object's data
        dictionary
        :param task_number: A string, one of 'task1', 'task2', ..., 'task6'.
        :param data_object: An instance of the data_file class
        :return: None
        """
        if task not in ['task1', 'task2', 'task3', 'task4', 'task5', 'task6']:
            raise e.TaskNameError(task)

        elif isinstance(data_object, data_file):
            self.data[task] = data_object
        else:
            raise TypeError(data_object)

    def write_summary(self, out_file, overwrite=False):

        import csv
        import os

        # Get summary data for all tasks in one dictionary
        full_summary = self.summarize_data()

        # Get headers in alphabetical order so that data will be written
        # in task order
        headers = sorted(full_summary.keys())

        # If the file already exists, we want to append to it
        # without writing header rows.  However, if overwrite
        # is true, the whole file will just be overwritten.

        if os.path.isfile(out_file) and not overwrite:
            with open(out_file, "a") as out:
                writer = csv.DictWriter(out, headers)
                out.write(",".join(str(x) for x in [self.key, self.ID, self.group, self.sibling]) + ",")
                writer.writerow(full_summary)  # Should only be one row

        else:  # Open a new file (or overwrite old one) and write to it
            with open(out_file, "w") as out:
                writer = csv.DictWriter(out, headers)
                # Add header for subject ID
                out.write('Key,SubID,Group,Sibling,')
                writer.writeheader()
                out.write(",".join(str(x) for x in [self.key, self.ID, self.group, self.sibling]) + ",")
                writer.writerow(full_summary)

    def dump_trial_by_trial(self, task, out_file, overwrite=False):
        """
        This function takes a list of dictionaries
        and writes them to a .csv file.
        """
        import csv
        import os

        # If the file already exists, we want to append to it
        # without writing header rows.  However, if overwrite
        # is true, the whole file will just be overwritten.
        if os.path.isfile(out_file) and not overwrite:
            with open(out_file, "a") as out:
                writer = csv.DictWriter(out, self.data[task].task_headers)
                # Add ID, time, group, and sibling as first columns

                for trial in self.data[task].trial_by_trial:
                    out.write(
                        ",".join(
                            str(x) for x in [self.key, self.ID, self.group, self.sibling, self.data[task].device,
                                             self.data[task].time]) + ",")
                    writer.writerow(trial)

        else:  # Open a new file (or overwrite old one) and write to it
            with open(out_file, "w") as out:
                writer = csv.DictWriter(out, self.data[task].task_headers)
                out.write('Key,SubID,Group,Sibling,Device,Time,')
                writer.writeheader()
                for row in self.data[task].trial_by_trial:
                    out.write(
                        ",".join(
                            str(x) for x in [self.key, self.ID, self.group, self.sibling, self.data[task].device,
                                             self.data[task].time]) + ",")
                    writer.writerow(row)

    def summarize_data(self):
        """
        Returns a dictionary with summary data from all tasks
        """
        # Get summary data for all tasks in one dictionary
        full_summary = {}
        for task in self.data:
            full_summary.update(self.data[task].summary)

        return full_summary


class data_file:
    """
    A class, each instance of which is built from
    a log file
    """

    def __init__(self, log_file):

        import os

        self.log_file = log_file
        self.filename = os.path.basename(log_file.name)
        self.parse_file_name(self.filename)
        self.set_task_headers()
        self.set_practice_headers()
        self.parse_file_data()
        self.summarize()
        del self.log_file  # Just because you can't pickle files

    def parse_file_name(self, file_name):

        """
        Given a log file name of a specific format
        for the YL data, will determine and assign values to attributes:

        self.task --> A string, one of 'task1', 'task2', ..., 'task6'
        self.sibling --> True/False
        self.group --> a two-digit number string
        self.ID --> a (hopefully) four-digit number string, though this is allowed to vary.
        self.key --> a unique identifier for the subject
        self.date --> the date when the file was generated
        self.time --> the time when the file was generated
        self.device --> a string identifying the device on which the task was administered

        A file of the defined format is:

        'PE211005_IIN028_task1_5-15-2013-16-13-32'

        The PE is just a prefix (for Peru?).  The two numbers following
        the PE (21 in this case) indicate membership to a certain group.
        the numbers after 'IIN' specify the device on which the tasks were
        completed.  The number following 'task' indicates to which task
        the log file corresponds.  The string of numbers at the end
        (5-15-2013-16-13-32) correspond to the date and time of completion
        (month-day-year-hour-minute-second). The letters 'PE' may or may not
        be followed by an 's', which indicates that that particular subject
        is a younger sibling of another subject with an identical ID number (other than the s).

        Example:

        The file name: 'PE211005_IIN028_task1_5-15-2013-16-13-32' will yield the following result:

        self.task = 'task1'
        self.sibling = False (since there's no 's' after 'PE')
        self.group = '21'
        self.ID = '1005'
        self.key = 'PE211005'
        self.date = '5/15/2013'
        self.time = '16:13:32'
        self.device = 'IIN028'
        """

        import os
        import re
        import warnings

        name, extension = os.path.splitext(os.path.basename(file_name))

        # Only accept csv files.
        if extension != ".csv":
            raise e.BadFileNameError("File: %s does not have extension, '.csv'" % file_name)

        # Split the file name into components. If filename = 'PE211005_IIN028_task1_5-15-2013-16-13-32',
        # name components should be = ['PE211005', 'IIN028', 'task1', '5-15-2013-16-13-32']
        subject, device, task, date_and_time = name.split("_")
        self.key = subject

        if task not in ['task1', 'task2', 'task3', 'task4', 'task5', 'task6']:
            raise e.BadFileNameError(
                "Invalid task designation in file: %s\nExpected one of 'task1', 'task2', ..., 'task6'\n" % file_name)

        else:
            self.task = task

        # Further split the subject string, which should be something like 'PE211005'
        sub_components = re.search(r'([a-zA-Z][a-zA-Z]s?)(\d\d)(\d+)', subject, re.IGNORECASE)

        # This should split the subject data into match.group(1) = 'PE',
        # match.group(2) = '21', and match.group(3) = 1005.  Note that
        # this assumes that the group number is always two digits, but
        # allows for the subject number to vary in length.
        if not sub_components:
            raise e.BadFileNameError(file_name)

        if len(sub_components.groups()) == 3:

            # Check if sibling
            if not sub_components.group(1):
                raise e.BadFileNameError(
                    "File name of unexpected format:\n\t%s\n\tExpected two-letter prefix" % file_name)
            if 's' in sub_components.group(1).lower():  # ignoring upper/lower case
                self.sibling = True
            else:
                self.sibling = False

            # Record group
            self.group = sub_components.group(2)  # two digits following PE/PEs
            # Record subject number
            self.ID = sub_components.group(3)  # all digits following
            self.device = device

            # We expect 6 digits following PE (or PEs).  If there is a different number,
            # warn the user, but don't raise an error.
            if len(self.ID) != 4:
                warnings.warn("File name of unexpected format:\n\t %s\n\tExpected a 2-digit group number and "
                              "4-digit ID number.  \nUsing SubID = %s" % (file_name, self.ID))

        else:  # The subject info isn't divided as expected
            raise e.BadFileNameError("File of unexpected format:\n\t%s" % file_name)

        # Split the date and time
        split_date = date_and_time.split("-")
        if len(split_date) != 6:
            raise e.BadFileNameError("Problem reading date/time information from file: %s\n" % file_name)
        else:
            self.date = "/".join(split_date[:3])
            self.time = ":".join(split_date[3:])

    def set_task_headers(self):

        """
        Assigns a value to self.practice_headers according to the value
        of self.task. Said value will be in the from of a list of
        strings (header names), which correspond to the data that we are interested in extracting
        from the log files.  This function is for task trials, specifically, as the headers
        for practice trials differ slightly from those associated with actual task trials.

        :return: None.  Value of self.practice_headers is assigned (as a list of strings)
        """

        if self.task == 'task1':
            self.task_headers = ["TrialNum", "NumBadTouches", "Score", "Score-incorrect only"]

        elif self.task == 'task2':
            self.task_headers = ['TrialNum', 'TargetSide', 'TimeOut', 'ReactionTime', 'TouchPosition',
                                 'DistanceFromCenter', 'PressedSide', 'GoalSide', 'Correct', 'SwitchRule',
                                 'SwitchSide']

        elif self.task == 'task3':
            self.task_headers = ['TrialNum', 'NumDots', 'ShownDots', 'Delay', 'TimeOut', 'EarlyResponse',
                                 'DotPressed', 'ReactionTime', 'TouchPosition', 'DistanceFromCenter', 'Rank']

        elif self.task == 'task4':
            self.task_headers = ['Block', 'PercentCorrect', 'AvgDistanceFromCenter', 'AvgResponseTime']

        elif self.task == 'task5':
            self.task_headers = ['Task', 'EndCondition', 'Duration', 'NumGoodTouches', 'NumBadTouches',
                                 'NumRepeats', 'AvgTimePerTarget', 'StandardDeviation', 'AvgTimePerAction',
                                 'AvgTargetsPerArea', 'AvgLocation', 'AvgFirstTen', 'AvgLastTen',
                                 'AvgDistancePerTarget']

        elif self.task == 'task6':
            self.task_headers = ["TrialNum", "NumBadTouches", "Score", "Score-incorrect only"]

    def set_practice_headers(self):

        """
        Assigns a value to self.practice_headers according to the value
        of self.task. Said value will be in the from of a list of
        strings (header names), which correspond to the data that we are interested in extracting
        from the log files.  This function is for practice trials, specifically, as the headers
        for practice trials differ slightly from those associated with actual task trials.

        :return: None.  Value of self.practice_headers is assigned (as a list of strings)
        """

        if self.task == 'task1':
            self.practice_headers = ["TrialNum", "NumBadTouches", "Score"]

        elif self.task == 'task2':
            self.practice_headers = ['TrialNum', 'TargetSide', 'TimeOut', 'ReactionTime', 'TouchPosition',
                                     'DistanceFromCenter', 'PressedSide', 'GoalSide', 'Correct']

        elif self.task == 'task3':
            self.practice_headers = ['TrialNum', 'NumDots', 'ShownDots', 'Delay', 'TimeOut', 'EarlyResponse',
                                     'DotPressed', 'ReactionTime', 'TouchPosition', 'DistanceFromCenter']

        elif self.task == 'task4':
            self.practice_headers = ['TrialNum', 'Correct', 'ResponseTime', 'TouchPosition', 'DistanceFromCenter']

        elif self.task == 'task5':
            self.practice_headers = ['EndCondition', 'Duration', 'NumGoodTouches', 'NumBadTouches',
                                     'NumRepeats', 'AvgTimePerTarget', 'StandardDeviation', 'AvgTimePerAction',
                                     'AvgTargetsPerArea', 'AvgLocation', 'AvgFirstTen', 'AvgLastTen',
                                     'AvgDistancePerTarget']

        elif self.task == 'task6':
            self.practice_headers = ["TrialNum", "NumBadTouches", "Score"]

    def parse_file_data(self):
        """
        Call the read_log_file function
        """
        import parser_functions as sub

        self.practice, self.trial_by_trial = sub.read_log_file(self.task, self.log_file, self.task_headers,
                                                               self.practice_headers)

    def summarize(self):

        """
        Generates task-specific summary data according to the value of self.task.
        The actual computation of the summary data relies on a call to a
        task-specific function, imported from summarize.py

        :return: None.  Assigns a value to self.summary
        """

        import summarize

        if self.task == 'task1':
            self.summary = summarize.get1(self.trial_by_trial)
        elif self.task == 'task2':
            self.summary = summarize.get2(self.trial_by_trial)
        elif self.task == 'task3':
            self.summary = summarize.get3(self.trial_by_trial)
        elif self.task == 'task4':
            self.summary = summarize.get4(self.trial_by_trial)
        elif self.task == 'task5':
            self.summary = summarize.get5(self.trial_by_trial)
        elif self.task == 'task6':
            self.summary = summarize.get6(self.trial_by_trial)