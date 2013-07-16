# An attempt to use some OOP to solve this problem.
import exception_classes as e


class subject:
    """
    A class containing all data (including trial by trial and summary statistics)
    and metadata (subject ID, device number, sibling, time) from the output task
    log files.
    """

    def __init__(self, ID, group, sibling):

        self.ID = ID       # Should be a four digit number
        self.group = group    # Generally a two-digit number
        self.sibling = sibling  # True/False bool
        self.make_id_str()      # Generate unique ID String ex: "PEs131010"
        self.data = {}       # A dictionary to be filled with data_file objects

    def __str__(self):
        """
        String representation of the object
        """
        return '<Subject Number: %s Group: %s Sibling: %s>' % (self.ID, self.group, str(self.sibling))

    def make_id_str(self):
        """ Makes an IDString key for unique  identification """

        if self.sibling:
            extra_letter = "s"
        else:
            extra_letter = ""
        self.IDString = 'PE' + extra_letter + self.group + self.ID

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
                out.write(",".join(str(x) for x in [self.IDString, self.ID, self.group, self.sibling]) + ",")
                writer.writerow(full_summary)  # Should only be one row

        else:  # Open a new file (or overwrite old one) and write to it
            with open(out_file, "w") as out:
                writer = csv.DictWriter(out, headers)
                # Add header for subject ID
                out.write('Key,SubID,Group,Sibling,')
                writer.writeheader()
                out.write(",".join(str(x) for x in [self.IDString, self.ID, self.group, self.sibling]) + ",")
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
                        ",".join(str(x) for x in [self.ID, self.group, self.sibling, self.data[task].device,
                                                  self.data[task].time]) + ",")
                    writer.writerow(trial)

        else:  # Open a new file (or overwrite old one) and write to it
            with open(out_file, "w") as out:
                writer = csv.DictWriter(out, self.data[task].task_headers)
                out.write('IDString,SubID,Group,Sibling,Device,Time,')
                writer.writeheader()
                for row in self.data[task].trial_by_trial:
                    out.write(
                        ",".join(
                            str(x) for x in [self.IDString, self.ID, self.group, self.sibling, self.data[task].device,
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
        self.makeID()
        del self.log_file  # Just because you can't pickle files

    def makeID(self):
        """
        Generates a unique ID string for the file.  This should be the same as the first
        section of the filename (the bit before the first underscore).  This method would
        probably be better to have as a part of the parse_file_name method, but this is the way things
        have happened.  Right now PE is hard-coded.  This will have to be fixed for future studies
        that don't use the PE prefix.
        """

        if self.sibling:
            extra_letter = "s"
        else:
            extra_letter = ""
        self.IDString = 'PE' + extra_letter + self.group + self.ID

    def parse_file_name(self, file_name):

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
        (month-day-year-hour-minute-second). The letters 'PE' may or may not
        be followed by an 's'.
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

        if task not in ['task1', 'task2', 'task3', 'task4', 'task5', 'task6']:
            raise e.BadFileNameError(
                "Invalid task designation in file: %s\nExpected one of 'task1', 'task2', ..., 'task6'\n" % file_name)

        else:
            self.task = task

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
                warnings.warn("File name of unexpected format: %s  \nExpected a 2-digit group number and "
                              "4-digit ID number.  \nUsing SubID = %s" % (file_name, self.ID))

        else:  # The subject info isn't divided as expected
            raise e.BadFileNameError("File of unexpected format: %s\nCheck underscores." % file_name)

        # Split the date and time
        split_date = date_and_time.split("-")
        if len(split_date) != 6:
            raise e.BadFileNameError("Problem reading date/time information from file: %s\n" % file_name)
        else:
            self.date = "/".join(split_date[:3])
            self.time = ":".join(split_date[3:])

    def set_task_headers(self):

        """
        Determines which field names to use when reading from the log file into
        the task dictionary list.
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
        import sub_functions as sub

        self.practice, self.trial_by_trial = sub.read_file(self.task, self.log_file, self.task_headers,
                                                           self.practice_headers)

    def summarize(self):

        import master_sheet

        if self.task == 'task1':
            self.summary = master_sheet.get1(self.trial_by_trial)
        elif self.task == 'task2':
            self.summary = master_sheet.get2(self.trial_by_trial)
        elif self.task == 'task3':
            self.summary = master_sheet.get3(self.trial_by_trial)
        elif self.task == 'task4':
            self.summary = master_sheet.get4(self.trial_by_trial)
        elif self.task == 'task5':
            self.summary = master_sheet.get5(self.trial_by_trial)
        elif self.task == 'task6':
            self.summary = master_sheet.get6(self.trial_by_trial)


if __name__ == "__main__":
    import os

    subFiles = sorted(['YL_DATA_PERU/' + f for f in os.listdir('YL_DATA_PERU') if 'PE121003' in f])
    b = None
    for i, f in enumerate(subFiles, start=1):
        with open(f) as in_file:
            print in_file
            a = data_file(in_file)
            if not b:
                b = subject(a.ID, a.group, a.sibling)
            b.add_data("task" + str(i), a)
            b.dump_trial_by_trial("task" + str(i), 'NEW' + str(i) + '.csv', overwrite=True)
            b.write_summary("New7.csv")

    with open('NEW7.csv', "r") as f:
        print f.read()
