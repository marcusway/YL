# An attempt to use some OOP to solve this problem.


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
        self.data = {}       # A dictionary to be filled with data_file objects

    def add_data(self, task, data_object):

        """
        Updates the subject object's data
        dictionary
        :param task_number: A string, one of 'task1', 'task2', ..., 'task6'.
        :param data_object: An instance of the data_file class
        :return: None
        """
        if task not in ['task1', 'task2', 'task3', 'task4', 'task5', 'task6']:
            raise Exception(
                "Invalid argument for task : %s.  Expected one of 'task1', 'task2', ..., 'task6'" % str(task))

        elif isinstance(data_object, data_file):
            self.data[task] = data_object
        else:
            raise Exception("Invalid argument: %s.  \nExpected instance of data_file class")

    def write_summary(self, out_file, overwrite=False):

        import csv
        import os

        # Get summary data for all tasks in one dictionary
        full_summary = {}
        for task in self.data:
            full_summary.update(self.data[task].summary)

        # Get headers in alphabetical order so that data will be written
        # in task order
        headers = sorted(full_summary.keys())

        # If the file already exists, we want to append to it
        # without writing header rows.  However, if overwrite
        # is true, the whole file will just be overwritten.

        if os.path.isfile(out_file) and not overwrite:
            with open(out_file, "a") as out:
                writer = csv.DictWriter(out, headers)
                out.write(",".join(str(x) for x in [self.ID, self.group, self.sibling]) + ",")
                writer.writerow(full_summary)  # Should only be one row

        else:  # Open a new file (or overwrite old one) and write to it
            with open(out_file, "w") as out:
                writer = csv.DictWriter(out, headers)
                # Add header for subject ID
                out.write('SubID,Group,Sibling,')
                writer.writeheader()
                out.write(",".join(str(x) for x in [self.ID, self.group, self.sibling]) + ",")
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
                writer = csv.DictWriter(out, self.data[task].field_names)
                # Add ID, time, group, and sibling as first columns

                for trial in self.data[task].trial_by_trial:
                    out.write(
                        ",".join(str(x) for x in [self.ID, self.group, self.sibling, self.data[task].device,
                                                  self.data[task].time]) + ",")
                    writer.writerow(trial)

        else:  # Open a new file (or overwrite old one) and write to it
            with open(out_file, "w") as out:
                writer = csv.DictWriter(out, self.data[task].field_names)
                out.write('SubID,Group,Sibling,Device,Time,')
                writer.writeheader()
                for row in self.data[task].trial_by_trial:
                    out.write(
                        ",".join(str(x) for x in [self.ID, self.group, self.sibling, self.data[task].device,
                                                  self.data[task].time]) + ",")
                    writer.writerow(row)


class data_file:
    """
    A class, each instance of which is built from
    a log file
    """

    def __init__(self, file_name):

        self.file_name = file_name
        self.parse_file_name(file_name)
        self.set_field_names()
        self.read_file()
        self.summarize()

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
            raise Exception("Invalid file format for file: %s\n Not a .csv file" % file_name)

        # Split the file name into components. If filename = 'PE211005_IIN028_task1_5-15-2013-16-13-32',
        # name components should be = ['PE211005', 'IIN028', 'task1', '5-15-2013-16-13-32']
        subject, device, self.task, date_and_time = name.split("_")

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
            raise Exception("File name of unexpected format: %s" % file_name)

        # Split the date and time
        split_date = date_and_time.split("-")
        self.date = "/".join(split_date[:3])
        self.time = ":".join(split_date[3:])

    def set_field_names(self):

        """
        Determines which field names to use when reading from the log file into
        the task dictionary list.
        """

        if self.task == 'task1':
            self.field_names = ["TrialNum", "NumBadTouches", "Score", "Score-incorrect only"]

        elif self.task == 'task2':
            self.field_names = ['TrialNum', 'TargetSide', 'TimeOut', 'ReactionTime', 'TouchPosition',
                                'DistanceFromCenter', 'PressedSide', 'GoalSide', 'Correct', 'SwitchRule',
                                'SwitchSide']

        elif self.task == 'task3':
            self.field_names = ['TrialNum', 'NumDots', 'ShownDots', 'Delay', 'TimeOut', 'EarlyResponse',
                                'DotPressed', 'ReactionTime', 'TouchPosition', 'DistanceFromCenter', 'Rank']

        elif self.task == 'task4':
            self.field_names = ['Block', 'PercentCorrect', 'AvgDistanceFromCenter', 'AvgResponseTime']

        elif self.task == 'task5':
            self.field_names = ['Task', 'EndCondition', 'Duration', 'NumGoodTouches', 'NumBadTouches',
                                'NumRepeats', 'AvgTimePerTarget', 'StandardDeviation', 'AvgTimePerAction',
                                'AvgTargetsPerArea', 'AvgLocation', 'AvgFirstTen', 'AvgLastTen', 'AvgDistancePerTarget']

        elif self.task == 'task6':
            self.field_names = ["TrialNum", "NumBadTouches", "Score", "Score-incorrect only"]

    def read_file(self):
        """
        Call the readTaskData function from peru1 with the corresponding task number.
        """

        import peru1

        if self.task == 'task1':
            self.practice, self.trial_by_trial = peru1.readTask1LogFile(self.file_name, headers=self.field_names)
        elif self.task == 'task2':
            self.practice, self.trial_by_trial = peru1.readTask2LogFile(self.file_name, headers=self.field_names)
        elif self.task == 'task3':
            self.practice, self.trial_by_trial = peru1.readTask3LogFile(self.file_name, headers=self.field_names)
        elif self.task == 'task4':
            self.practice, self.trial_by_trial = peru1.readTask4LogFile(self.file_name, headers=self.field_names)
        elif self.task == 'task5':
            self.practice, self.trial_by_trial = peru1.readTask6LogFile(self.file_name, headers=self.field_names)
        elif self.task == 'task6':
            self.practice, self.trial_by_trial = peru1.readTask1LogFile(self.file_name, headers=self.field_names)

    def summarize(self):

        import master_sheet

        if self.task == 'task1':
            self.summary = master_sheet.get1(self.trial_by_trial)
        elif self.task == 'task2':
            self.summary = master_sheet.better_get2(self.trial_by_trial)
        elif self.task == 'task3':
            self.summary = master_sheet.get3(self.trial_by_trial)
        elif self.task == 'task4':
            self.summary = master_sheet.get4(self.trial_by_trial)
        elif self.task == 'task5':
            self.summary = master_sheet.get5(self.trial_by_trial)
        elif self.task == 'task6':
            self.summary = master_sheet.get1(self.trial_by_trial)


if __name__ == "__main__":
    import os

    subFiles = sorted(['log_files/' + f for f in os.listdir('log_files') if 'PE211020' in f])
    b = None
    for i, f in enumerate(subFiles):
        a = data_file(f)
        if not b:
            b = subject(a.ID, a.group, a.sibling)
        b.add_data("task"+str(i+1), a)
        b.dump_trial_by_trial("task" + str(i+1), 'NEW' + str(i+1) + '.csv', overwrite=True)
    b.write_summary("New7.csv")

    with open('NEW7.csv', "r") as f:
        print f.read()
