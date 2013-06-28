# Task 1: Paired associated learning task. Subject
# is tasked with learning a hierarchical function mapping
# one type of shape to another. 

# Each subject's individual log file 
# is named something like 1A01_IIN004_task1_5-3-2013-17-43-20.csv
# where the first four digits are a subject ID, IIN004 seems to
# also vary, but I'm not sure what it is.  The numbers separated
# by hyphens correspond to the date and time:  month-day-year-hour-minute-second

# The contents of the file look like this: 

# Stim Locations	 Stim1	 222.5506; 576	 Stim2	 529.5168; 576	 Stim3	 836.4832; 576	 Stim4
# Calculations	 AvgNumBadTouch	1.083333	 LearningRateItems	11	 AvgProbabilityCorrectCategory	75%	 LearningRateCategory
# Practice	 TrialNum	 TargetID	 Stimuli	 TouchedID	 TouchPosition	 NumBadTouches	 Score
# 	1	-3	 4;5;1;2	4	 237;607	0	0
# 	2	-1	 4;3;2;5	3	 524;612	1	2
# 	2	-1	 4;3;2;5	2	 796;611	1	2
# 	3	-2	 3;1;5;4	5	 825;571	1	2
# Task	 TrialNum	 TargetID	 Stimuli	 TouchedID	 TouchPosition	 NumBadTouches	 Score
# 	1	6	 3;11;10;5	11	 532;588	2	1
# 	1	6	 3;11;10;5	3	 229;608	2	1
# 	1	6	 3;11;10;5	10	 839;580	2	1



# where the first line contains summary statistics, then there is a block for practice data
# followed by a block containing the data from the actual task. We want to take both the 
# task and practice data and append them to corresponding sheets in an excel document 
# containing such data for all subjects.  That file is formatted in this way:

# Task	group	 TrialNum	 NumBadTouches	 Score	Score-incorrect only
# 1A01	6 & 7	1	4	2	2
# 1A01	6 & 7	2	0	0	
# 1A01	6 & 7	3	0	0	
# 1A01	6 & 7	4	0	0	
# 1A01	6 & 7	5	0	0	
# 1A01	6 & 7	6	0	0	
# 1A01	6 & 7	7	0	0	
# 1A01	6 & 7	8	2	1	1
# 1A01	6 & 7	9	1	2	2
# 1A01	6 & 7	10	0	0	

# Grab all the log files with _task1_ in them, 
# put the first four digits of the filename in column 1
# Column 2 will hold the age group, and I have to figure
# out how to get that from the log file (whether it's from
# the file name or otherwise). The next three columns will 
# be TrialNum, NumBadTouches, Score, in that order.  The 
# next column, Score-incorrect only, contains nothing if the
# value in column "NumBadTouches" is zero.  Otherwise, 
# it contains the same value as Score. 

# Lingering questions about Task1: 
# 
# What to do about "incomplete files"
# Do we want to include stim locations? 
# Will probably need to implement a way 
# to compile the summary stats into one sheet. 

field_names = {'task1': ["TrialNum", "NumBadTouches", "Score", "Score-incorrect only"],
               'task2': ['TrialNum', 'TargetSide', 'TimeOut', 'ReactionTime', 'TouchPosition',
                         'DistanceFromCenter', 'PressedSide', 'GoalSide', 'Correct', 'SwitchRule',
                         'SwitchSide'],
               'task3': ['TrialNum', 'NumDots', 'ShownDots', 'Delay', 'TimeOut', 'EarlyResponse',
                         'DotPressed', 'ReactionTime', 'TouchPosition', 'DistanceFromCenter', 'Rank'],
               'task4': ['Block', 'PercentCorrect', 'AvgDistanceFromCenter', 'AvgResponseTime'],
               'task5': ['TrialNum', 'TurnedOrange', 'Correct', 'ReactionTime', 'TouchPosition',
                         'DistanceFromCenter', 'PrevTrialOrange'],
               'task6': ['Task', 'EndCondition', 'Duration', 'NumGoodTouches', 'NumBadTouches',
                         'NumRepeats', 'AvgTimePerTarget', 'StandardDeviation', 'AvgTimePerAction',
                         'AvgTargetsPerArea', 'AvgLocation', 'AvgFirstTen', 'AvgLastTen', 'AvgDistancePerTarget'],
               'task7': ["TrialNum", "NumBadTouches", "Score", "Score-incorrect only"]
}


def readTask1LogFile(filename, headers=field_names['task1']):
    """
    Takes as an argument the path to
    a log file of the format specified above and
    returns two lists of lists: practice and task.
    It also returns the subject ID number
    """

    import csv

    with open(filename, "rU") as logFile:

        # Make a list of lists, one for each line
        # of the file.  csv.reader breaks each row into
        # a list according where the commas are
        logReader = csv.reader(logFile)

        # The top line contains summary statistics, where each cell contains
        # a key: value pair, except for the first column, which is just "Calculations"

        # Here we turn each pair into a dictionary item in the summary dictionary
        #summary = dict(entry.split(":") for entry in logReader.next()[1:])

        # UNUSED LINES
        logReader.next()  # Returns stimulus locations. Unused.
        logReader.next()  # Returns a summary line, which is also unused.
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
                raise Exception("Error: line of unexpected format in file %s:\n%s" % (filename, line))

            # Add the current row to its appropriate list
            else:
                # Add the current line (as a list) to
                # the appropriate list of lines
                currTrialNum = line[1]
                if currTrialNum != prevTrialNum:
                    currTrialType.append([cleaned_string(x) for x in [line[1], line[6], line[7]]])
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

#---------------------------
# Log File Format
#---------------------------

# Dot Locations	 Left: 341.5;384	 Right: 1024.5;384						
# Practice	 TrialNum	 TargetSide	 TimeOut	 ReactionTime	 TouchPosition	 DistanceFromCenter	 PressedSide	 Correct
#  	1	Opposite	TRUE	 .	 .	 .	 .	0
#  	2	Opposite	FALSE	0.8832397	1025;414	30.00417	 Right	1
#  	3	Opposite	FALSE	0.6688843	995;414	42.07434	 Right	1
#  	4	Opposite	FALSE	0.7524414	484;439	152.7457	 Left	1
#  	5	Opposite	FALSE	0.6675415	480;390	138.6299	 Left	1
#  	6	Same	FALSE	0.8174438	356;392	16.5605	 Left	1
#  	7	Same	FALSE	0.8015747	1023;410	26.04323	 Right	1
# Task	 TrialNum	 TargetSide	 TimeOut	 ReactionTime	 TouchPosition	 DistanceFromCenter	 PressedSide	 Correct
#  	1	Same	FALSE	1.130798	1010;408	28.04015	 Right	1
#  	2	Opposite	FALSE	0.8491211	1003;374	23.71181	 Right	1
#  	3	Same	FALSE	0.8665161	356;395	18.20028	 Left	1
#  	4	Opposite	FALSE	0.7685547	431;407	92.40807	 Left	1
#  	5	Same	FALSE	0.6846313	1042;382	17.61391	 Right	1

# There are 60 total "Task" trials (the rest not shown here in interest of space)

#--------------------------
# Compiled Data Format
#--------------------------
#       				0 		       1          2             3                 4            5                6                7       8         9            10
# subject	group	 TrialNum	 TargetSide	 TimeOut	 ReactionTime	 TouchPosition	 DistanceFromCenter	 PressedSide  GoalSide	 Correct	SwitchRule      SwitchSide
# 1A01	6 & 7	1	Opposite	FALSE	1.419495	1028;432	48.12743	 Right	1	switch	switch
# 1A01	6 & 7	2	Opposite	FALSE	1.180237	293;382	48.54122	 Left	1	non-switch	switch
# 1A01	6 & 7	3	Same	FALSE	0.8774414	339;386	3.201562	 Left	1	switch	non-switch
# 1A01	6 & 7	4	Same	FALSE	0.7954712	1022;357	27.11549	 Right	1	non-switch	switch
# 1A01	6 & 7	5	Same	FALSE	0.9067993	1006;386	18.60779	 Right	1	non-switch	non-switch
# 1A01	6 & 7	6	Opposite	FALSE	1.047668	376;384	34.5	 Left	1	switch	switch

# Note the addition of switch side and switch rule columns.  Switched-side is true
# if the correct response to the current trial is to press to the side opposite 
# the correct response to the previous trial.  Switched-rule is true if the 
# color of circle presented in the current trial differs from that of the 
# circle presented in the previous trial.  


def readTask2LogFile(filename, headers=field_names['task2']):
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
    TRIAL_NUM = 0
    TARGET_SIDE = 1
    TIME_OUT = 2
    REACTION_TIME = 3
    TOUCH_POSITION = 4
    DIST_FROM_CENTER = 5
    PRESSED_SIDE = 6
    GOAL_SIDE = 7

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
        logReader.next()  # Practice headers

        # There are a variable number of practice trials.
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
            if line[0] == "Task":
                # The line contains task headers. Do nothing with it,
                # but the following lines should be added to the task list
                currTrialType = task

            # If we get a row with something other
            # than "Task" in the first column, report an error.
            elif line[0] and not line[0].isspace():
                raise Exception("Error: line of unexpected format in file %s:\n%s" % (filename, line))

            # Add the current row to its appropriate list
            else:
                # Add the current line (as a list) to
                # the appropriate list of lines
                currTrialType.append([cleaned_string(x) for x in line[1:]])

        # At this point, practice and task will each be a list of lists, where
        # each sub-list has entries corresponding to the values indicated
        # by the header row of the log file

        # Now it seems that we will want to determine switch/non-switch.  True for switch,
        # False for non-switch
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

#-----------------------------
# Log File Format
#-----------------------------

# Dot Locations Dot 1	 227.6667; 128	 Dot 2	 683; 128	 Dot 3	 1138.333; 128	 Dot 4	 227.6667; 384	 Dot 5	 683; 384	 Dot 6
# Practice	 TrialNum	 NumDots	 ShownDots	 Delay	 TimeOut	  EarlyResponse	 DotPressed	 ReactionTime	 TouchPosition	 DistanceFromCenter
#  	1	1	7	0.1	TRUE	 .	 .	 .	 .	 .
#  	2	3	1;3;4	3	FALSE	FALSE	3	1.434814	959;147	180.3369
#  	2	3	1;3;4	3	FALSE	FALSE	7	3.221802	173;647	55.11302
#  	2	3	1;3;4	3	TRUE	 .	 .	 .	 .	 .
#  	3	3	5;6;7	0.1	FALSE	FALSE	7	2.745911	203;676	43.63994
# Task	 TrialNum	 NumDots	 ShownDots	 Delay	 TimeOut	 EarlyResponse	 DotPressed	 ReactionTime	 TouchPosition	 DistanceFromCenter
#  	1	1	5	3	FALSE	FALSE	5	1.154114	659;345	45.79301
#  	2	1	1	3	FALSE	FALSE	1	1.184998	253;125	25.51034
#  	3	3	4;6;7	0.1	FALSE	FALSE	4	1.552307	280;383	52.34288
#  	3	3	4;6;7	0.1	FALSE	FALSE	7	2.151245	259;622	36.13554
#  	3	3	4;6;7	0.1	FALSE	FALSE	3	2.828674	1042;214	129.136
#  	4	1	3	0.1	FALSE	FALSE	3	1.454163	1114;156	37.09592

#------------------------------
# Compiled Data Format
#------------------------------

# subject	group	 TrialNum	NumDots	 ShownDots	 Delay	 TimeOut	 EarlyResponse	 DotPressed	 ReactionTime	 TouchPosition	 DistanceFromCenter	2if2nd	1if3rd	rank
# 1A01	6 & 7	1		4;9	3	FALSE	FALSE	9	0.7625732	1154;637	15.9514	1		1
# 1A01	6 & 7	1		4;9	3	FALSE	FALSE	4	1.651245	455;438	233.6588	2		2
# 1A01	6 & 7	2		3;4	3	FALSE	FALSE	3	0.6737061	1120;142	23.06747	1		1
# 1A01	6 & 7	2		3;4	3	FALSE	FALSE	4	1.375122	427;345	203.1127	2		2
# 1A01	6 & 7	3		5	0.1	FALSE	FALSE	5	1.649292	698;387	15.29706	1		1
# 1A01	6 & 7	4		3;6;7	3	FALSE	FALSE	3	0.7937012	1142;89	39.17199	1		1
# 1A01	6 & 7	4		3;6;7	3	FALSE	FALSE	7	2.56897	323;593	106.2894	2		2


# In the compiled spreadsheet, there should be an additional column indicating 
# in what order the circles were pressed--this is determined by seeing how many
# previous lines share the same trial number.  That is, for the current line, 
# if it belongs to trial N, and the previous 2 lines also belong to trial N, 
# then the current line represents dot number 3 for trial N. 

def readTask3LogFile(filename, headers=field_names['task3']):
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

    with open(filename, "rU") as logFile:

        # Make a list of lists, one for each line
        # of the file.  csv.reader breaks each row into
        # a list according where the commas are
        logReader = csv.reader(logFile)

        # UNUSED LINES
        logReader.next()  # Dot Locations
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
            if line[0] == "Task":
                # Current line contains task headers; disregard
                currTrialType = task  # Following lines are for task (not practice)

            # If we get a row with something other
            # than "Task" in the first column, report an error.
            elif line[0] and not line[0].isspace():
                raise Exception("Error: line of unexpected format in file %s:\n%s" % (filename, line))

            # Add the current row to its appropriate list
            else:
                # Add the current line (as a list) to
                # the appropriate list of lines
                currTrialType.append([cleaned_string(x) for x in line[1:]])

        # At this point, practice and task will each be a list of lists, where
        # each sub-list has entries corresponding to the values indicated
        # by the header row of the log file

        # Now it we want to label dot numbers according to trial numbers.
        # The first overall dot presented has to be the first dot of its
        # respective trial.
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
# It's adnministered in 5 35-trial blocks.  Blocks 1 and 4 are the same.
# It looks like the alldata file only uses information from the 
# mean block calculations

#------------------------------
# Log File Format
#------------------------------

# Dot Locations	 Dot1	 299.2921; 128	 Dot2	 810.9026; 256	 Dot3	 1066.708; 640	 Dot4	 427.1948; 512
# Practice	 TrialNum	 Correct	 ResponseTime	 TouchPosition	 DistanceFromCenter			
# 	1	 True	0.8709106	 (197;126)	25.68845			
# 	2	 True	0.8661499	 (162;635)	10.63782			
# 	3	 False	 .	 .	 .			
# 	4	 True	0.9961548	 (1207;673)	35.24912			
# Block 1 Calculations	 PercentCorrect	94.29%	 AvgDistanceFromCenter	26.89667	 AvgResponseTime	0.6776623		
# 	 TrialNum	 Correct	 ResponseTime	 TouchPosition	 DistanceFromCenter			
#  	1	 True	0.8650513	 (816;282)	26.49497			
#  	2	 True	0.8317261	 (826;275)	24.26792			
#  	3	 True	0.7005005	 (452;532)	31.86377			
# Block 3 Calculations	 PercentCorrect	100%	 AvgDistanceFromCenter	26.84296	 AvgResponseTime	0.6177822
# 	 TrialNum	 Correct	 ResponseTime	 TouchPosition	 DistanceFromCenter	
#  	71	 True	0.829834	 (811;280)	24.0002	
#  	72	 True	0.6978149	 (1057;626)	17.03652	
#  	73	 True	0.6636353	 (806;216)	40.29932	
# Block 4 Calculations	 PercentCorrect	91.43%	 AvgDistanceFromCenter	32.28865	 AvgResponseTime	0.6529274
# 	 TrialNum	 Correct	 ResponseTime	 TouchPosition	 DistanceFromCenter	
#  	106	 True	0.7467651	 (1064;657)	17.21432	
#  	107	 True	0.7786865	 (449;515)	22.01064	
#  	108	 True	0.7628784	 (328;95)	43.73947	
# Block 5 Calculations	 PercentCorrect	91.43%	 AvgDistanceFromCenter	33.50831	 AvgResponseTime	0.6706448
# 	 TrialNum	 Correct	 ResponseTime	 TouchPosition	 DistanceFromCenter	
#  	141	 True	0.5807495	 (820;216)	41.02149	
#  	142	 False	 .	 .	 .	
#  	143	 True	0.6467896	 (777;293)	50.18352	

# There are actually 35 trials per block, but I truncated them here for space reasons. 

#------------------------------
# Compiled Format
#------------------------------

# Just want subject number, block number, % correct, avg dist from center, avg response time.  
# Basically just need the calculations on the block lines along with the subject number. 

#----------------------
# Code
#----------------------


def readTask4LogFile(filename, headers=field_names['task4']):
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

    with open(filename, "rU") as logFile:

        # Make a list of lists, one for each line
        # of the file.  csv.reader breaks each row into
        # a list according where the commas are
        logReader = csv.reader(logFile)

        # The top line of the file contains
        # coordinates of the locations where the
        # circle stimuli are presented
        logReader.next()  # Dot locations
        logReader.next()  # Practice headers

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

                task.append([line[0].split()[1], line[2].strip("%"), line[4], line[6]])

                if not practiceDone:
                    practiceDone = True

            elif line[0] and not line[0].isspace():
                raise Exception("Error: line of unexpected format in file %s:\n%s\n Expected "
                                "blank first column." % (filename, line))

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
                currTrialType.append(line[1:])  # Don't include the first (blank) entry

        # The first trial has no previous trial, so the
        # previous trial was not Orange.
        task[0].append(False)

        # Iterate over the remaining lines of the file
        for i in range(1, len(task)):

            # If the dot turned orange in the previous trial:
            # (turned orange is the second value in the list
            # for the each task)
            if 'True' in task[i - 1][1]:
            # Set "prev trial orange" to be true.
                task[i].append(True)
            else:
                task[i].append(False)

        task_dict = [dict(zip(headers, trial)) for trial in task]
        practice_dict = [dict(zip(headers[:-1], trial)) for trial in practice]
        return practice_dict, task_dict

############################################################################
############################### TASK 6 #####################################
############################################################################

#---------------------------
# Task Description
#---------------------------

# This is a visual search task, where the subject must press
# to stars of a certain size while avoiding other targets.  

#---------------------------
# Log File Format
#---------------------------

# Global Averages, AvgGoodTouches, 33, AvgBadTouches, 1, AvgRepeats, 0, AvgTimePerTarget, 0.4169034, AvgStandardDeviation, 7.59258, AvgTimePerAction, 0.4046415, AvgTargetsPerArea, (5;3;5;3;4;5;4;4), AvgLocation, 695.8182, AvgFirstTen, 0.3613281, AvgLastTen, 0.4262695, AvgDistancePerTarget,160.6311
# Practice 1, EndCondition, Completed, Duration, 3.160156, NumGoodTouches, 5, NumBadTouches, 0, NumRepeats, 0, AvgTimePerTarget, 0.6292969, StandardDeviation, 1.564191, AvgTimePerAction, 0.6292969, AvgTargetsPerArea, (1;1;0;1;0;1;1;0), AvgLocation, 576.2, AvgFirstTen, 0.6292969, AvgLastTen, 0.6292969, AvgDistancePerTarget, 418.1909
# ResponseNum, ResponseType, ResponseTime, TouchPosition
# 1, GOOD, 0.4990234, (923;478)
# 2, GOOD, 1.162109, (1229;117)
# 3, GOOD, 1.956055, (460;509)
# 4, GOOD, 2.587891, (165;237)
# 5, GOOD, 3.146484, (104;585)
# Task 1, EndCondition, Skipped, Duration, 14.82715, NumGoodTouches, 33, NumBadTouches, 1, NumRepeats, 0, AvgTimePerTarget, 0.4169034, StandardDeviation, 7.59258, AvgTimePerAction, 0.4046415, AvgTargetsPerArea, (5;3;5;3;4;5;4;4), AvgLocation, 695.8182, AvgFirstTen, 0.3613281, AvgLastTen, 0.4262695, AvgDistancePerTarget, 160.6311
# ResponseNum, ResponseType, ResponseTime, TouchPosition
# 1, GOOD, 0.6464844, , (1013;604)
# 2, GOOD, 0.9326172, , (1055;553)
# 3, GOOD, 1.44043, , (1109;559)
# 4, GOOD, 1.544922, , (1314;544)
# 5, GOOD, 1.875977, , (1331;350)

# I can't tell if there are generally two tasks or not.  The PowerPoint on the
# task indicates that there should be, but the most recent log files
# only seem to show one task.  In any case, the compiled data file
# just seems to contain the summary statistics in the "Task #" lines. 
# So we'll just take the data from those lines as in task 4. 

#-------------------------
# Code
#-------------------------


def readTask6LogFile(filename, headers=field_names['task6']):
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

    with open(filename, "rU") as logFile:

        # Make a list of lists, one for each line
        # of the file.  csv.reader breaks each row into
        # a list according where the commas are
        logReader = csv.reader(logFile)

        # Unused line
        logReader.next()  # Summary statistics.

        practice = []
        task = []
        # The next line contains a summary of the practice.
        for line in logReader:
            if "Practice" in line[0]:
                practice.append(line)
            elif "Task" in line[0]:
                # We will have a list like this:
                # [Task 1, EndCondition, Skipped, Duration, 14.82715, NumGoodTouches, 33,
                # 	NumBadTouches, 1, NumRepeats, 0, AvgTimePerTarget, 0.4169034, StandardDeviation,
                # 	7.59258, AvgTimePerAction, 0.4046415, AvgTargetsPerArea, (5;3;5;3;4;5;4;4), AvgLocation,
                # 	695.8182, AvgFirstTen, 0.3613281, AvgLastTen, 0.4262695, AvgDistancePerTarget, 160.6311]
                # where all entries are strings.  We will reduce this to
                # ['1', 'Skipped', '14.82715, '33', '1', '0', '0.4169034',
                #	'0.759258', '0.4046415', '(5;3;5;3;4;5;4;4)', '697.8182', '0.3613281', '0.4262695', '160.6311']

                task.append([line[0].split()[1]] + [line[i] for i in range(2, len(line), 2)])

        task_dict = [dict(zip(headers, trial)) for trial in task]
        # Convert the practice lines to dictionaries
        practice_dict = [dict([(practice[i][j], practice[i][j + 1]) for j in range(1, len(practice[i]) - 1, 2)]) for i
                         in range(len(practice))]
        # Specify trial number within each dictionary
        for i in range(len(practice_dict)):
            practice_dict[i]['Trial'] = i + 1

        return practice_dict, task_dict


############################################################################
############################### TASK 7 #####################################
############################################################################

# Identical to task 1, not bothering with additional description/code


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
    subject, device, task_number, date_and_time = name.split("_")

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

        # We expect 6 digits following PE (or PEs).  If there is a different number,
        # warn the user, but don't raise an error.
        if len(metadata['SubID']) != 4:
            warnings.warn("File name of unexpected format: %s  Expected a 2-digit group number and "
                          "4-digit ID number.  Using SubID = %s" % (file_name, metadata['SubID']))

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
        elif just_text.replace(".", "").isdigit():
            return float(just_text)
        elif ";" in just_text:
            return tuple(float(x) for x in just_text.split(";"))
        else:
            return just_text
    else:
        return None





if __name__ == "__main__":

    import os

    fileList = ['./log_files/' + logFile for logFile in os.listdir('./log_files') if 'pe' in logFile.lower()]

    for task, task_function, out_file in [('task1', readTask1LogFile, 'TEST1.csv'),
                                          ('task2', readTask2LogFile, 'TEST2.csv'),
                                          ('task3', readTask3LogFile, 'TEST3.csv'),
                                          ('task4', readTask4LogFile, 'TEST4.csv'),
                                          ('task5', readTask5LogFile, 'TEST5.csv'),
                                          ('task6', readTask6LogFile, 'TEST6.csv'),
                                          ('task7', readTask1LogFile, 'TEST7.csv')]:
        new_file = True

        for log_file in [f for f in fileList if task in f]:

            # Get subject ID and group from the file name

            file_metadata = parse_file_name(log_file)

            # Run the correct readTaskLogFile function on the
            # given task file
            practice, task_data = task_function(log_file)

            # Add group membership and subID to each dictionary
            # in the list of dictionaries returned by the readTaskLogFile
            # function

            for trial in task_data:
                trial.update(file_metadata)
                #print "Processing file: ", os.path.basename(log_file)
                write_to_task_file(task_data, out_file, ['SubID', 'Group', 'Device', ] + field_names[task],
                                   overwrite=new_file)
                new_file = False





