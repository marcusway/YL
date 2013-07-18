"""
A set of functions that take the output of the read_file functions
and return a dictionary of summary statistics.
"""


def mean(x):
    """
    A roll your own function to get the mean of a list of numbers
    so that we don't have to use Numpy.  This ignores missing values, so
    mean([1,2,3,None]) = 6/3 = 2
    :param x: a list of numbers
    :return average: a float, the mean of the numbers in x
    """
    # Ignore any "None" values
    new_array = [i for i in x if i is not None]
    n_entries = len(new_array)

    # Calculate the mean of the new array the old-fashioned way
    if n_entries > 0:
        average = float(sum([i for i in new_array]))/n_entries
    else:  # If the array has no legitimate values, set the average to none
        average = None

    return average


def get1(task_dict_list):
    """
    :param task_dict_list: list of dictionaries output
                           by read_file function

    :return a dictionary of summary summary statistics including
            T1_BadTouchesAllTrials
            T1_BadTouchesFirst

    """

    # Calculate the average number of bad touches per trial
    bad_touches = [x['NumBadTouches'] for x in task_dict_list]
    scores = [x['Score-incorrect only'] for x in task_dict_list]

    # We should always have 12 trials, and be looking at the first
    # six trials versus the last six trials, but I've added this
    # midpoint variable in case for some reason there's a different
    # number of trials.
    mid_point = len(bad_touches) / 2

    # Again, since there should be equal number of trials contributing
    # to avg_first and average_last, avg_total could be computed by
    # just doing mean([avg_first, avg_last]), but it's safer this way
    avg_total = mean(bad_touches)
    avg_first = mean(bad_touches[:mid_point])
    avg_last = mean(bad_touches[mid_point:])

    score_first = mean([score for score in scores[:mid_point] if score])
    score_last = mean([score for score in scores[mid_point:] if score])
    score_total = mean([score for score in scores if score])

    return {'T1_BadTouchesAllTrials': avg_total, 'T1_BadTouchesFirst': avg_first, 'T1_BadTouchesLast': avg_last,
            'T1_ScoreFirst': score_first, 'T1_ScoreLast': score_last, 'T1_ScoreAllTrials': score_total}


def get2(task_dict_list):

    """
    :param task_dict_list: A list of dictionaries from task 2 log file.
                           Each entry of the list corresponds to a trial.

    :return: a dict object with 12 keys corresponding to summary data for task 2.

    This is grossly hard-coded, but it's correct
    and produces a flat dictionary, which will
    be easier to write to the summary file.
    """

    ###############################################################
    # Organize Trials into separate lists according to trial type #
    ###############################################################

    non_switch_rule_trials = []
    switch_rule_trials = []
    non_switch_side_trials = []
    switch_side_trials = []
    same_trials = []
    opposite_trials = []

    for trial in task_dict_list:
        if trial['SwitchRule'] is True:
            switch_rule_trials.append(trial)
        elif trial['SwitchRule'] is False:
            non_switch_rule_trials.append(trial)

        if trial['SwitchSide'] is True:
            switch_side_trials.append(trial)
        elif trial['SwitchSide'] is False:
            non_switch_side_trials.append(trial)

        if trial['TargetSide'] == "same":
            same_trials.append(trial)
        elif trial['TargetSide'] == "opposite":
            opposite_trials.append(trial)

    ###############################################################
    # Calculate summary statistics for the different trial types. #
    # Note that trials for which there is missing or incomplete   #
    # data are not included in these calculations.                #
    ###############################################################

    switch_rule_accuracy = mean([x['Correct'] for x in switch_rule_trials])
    non_switch_rule_accuracy = mean([x['Correct'] for x in non_switch_rule_trials])
    switch_side_accuracy = mean([x['Correct'] for x in switch_side_trials])
    non_switch_side_accuracy = mean([x['Correct'] for x in non_switch_side_trials])
    same_accuracy = mean([x['Correct'] for x in same_trials])
    opposite_accuracy = mean([x['Correct'] for x in opposite_trials])

    switch_rule_rt = mean([x['ReactionTime'] for x in switch_rule_trials])
    non_switch_rule_rt = mean([x['ReactionTime'] for x in non_switch_rule_trials])
    switch_side_rt = mean([x['ReactionTime'] for x in switch_side_trials])
    non_switch_side_rt = mean([x['ReactionTime'] for x in non_switch_side_trials])
    same_rt = mean([x['ReactionTime'] for x in same_trials])
    opposite_rt = mean([x['ReactionTime'] for x in opposite_trials])

    return {'T2_SwitchRuleAvgAccuracy': switch_rule_accuracy, 'T2_NonSwitchRuleAvgAccuracy': non_switch_rule_accuracy,
            'T2_SwitchSideAvgAccuracy': switch_side_accuracy, 'T2_NonSwitchSideAvgAccuracy': non_switch_side_accuracy,
            'T2_SameAccuracy': same_accuracy, 'T2_OppositeAccuracy': opposite_accuracy, 'T2_SwitchRuleRT':
            switch_rule_rt, 'T2_NonSwitchRuleRT': non_switch_rule_rt, 'T2_SwitchSideRT': switch_side_rt,
            'T2_NonSwitchSideRT': non_switch_side_rt, 'T2_SameRT': same_rt, 'T2_OppositeRT': opposite_rt}


def get3(task_dict_list):
    """
    Reads Task 3 list of dictionaries.  Importantly, each list member for
    task three corresponds to an individual dot press, not an individual trial
    (there may be 1,2, or 3 dot presses per trial).

    EXAMPLE INPUT: would consist of a list of dictionaries like these:

     {'Delay': 0.1,
      'DistanceFromCenter': 38.38547,
      'DotPressed': 4,
      'EarlyResponse': False,
      'NumDots': 1,
      'Rank': 1,
      'ReactionTime': 1.040039,
      'ShownDots': 4,
      'TimeOut': False,
      'TouchPosition': (263.0, 369.0),
      'TrialNum': 56},


    """

    trials = []
    trial_num = None

    # Builds a list within which each trial is represented by a list,
    # within which each dot has a (distance, delay tuple)
    # TODO: This could be implemented more efficiently either as a dictionary or a different list structure
    for trial in task_dict_list:
        if trial['TrialNum'] == trial_num:
            trials[-1].append((trial['DistanceFromCenter'], trial['Delay']))
        else:
            trials.append([])
            trial_num = trial['TrialNum']
            trials[-1].append((trial['DistanceFromCenter'], trial['Delay']))

    # Now we have a list of lists of (distance, delay) tuples.

    # Calculate average accuracy by load, determined by the length of the list
    acc_by_load = {}
    for i in range(1, 4):
        load_means = [mean([dot[0] for dot in trial if dot[0]]) for trial in trials if len(trial) == i]

        acc_by_load[i] = mean([x for x in load_means if x is not None])

    acc_by_delay = {}
    for delay in [0.1, 3]:
        delay_means = [mean([dot[0] for dot in trial if dot[0] is not None])
                       for trial in trials if trial[0][1] == delay]

        acc_by_delay[delay] = mean([x for x in delay_means if not x is not None])

    return {'T3_Load1Distance': acc_by_load[1], 'T3_Load2Distance': acc_by_load[2], 'T3_Load3Distance': acc_by_load[3],
            'T3_Delay0.1Distance': acc_by_delay[0.1], 'T3_Delay3Distance': acc_by_delay[3]}


def get4(task_dict_list):
    """
    Reads Task 4 dictionary (output from read_file)
    and outputs summary data.  Input looks like:

    [{'AvgDistanceFromCenter': 15.30155,
      'AvgResponseTime': 0.645187,
      'Block': 1,
      'PercentCorrect': 100.0},
     {'AvgDistanceFromCenter': 22.55198,
      'AvgResponseTime': 0.5908622,
      'Block': 2,
      'PercentCorrect': 100.0},
     {'AvgDistanceFromCenter': 17.30606,
      'AvgResponseTime': 0.6249163,
      'Block': 3,
      'PercentCorrect': 100.0},
     {'AvgDistanceFromCenter': 20.74315,
      'AvgResponseTime': 0.6071847,
      'Block': 4,
      'PercentCorrect': 100.0},
     {'AvgDistanceFromCenter': 21.26595,
      'AvgResponseTime': 0.5916294,
      'Block': 5,
      'PercentCorrect': 100.0}]

    """


    rand_blocks = (1, 4)
    rule_blocks = (2, 3, 5)

    random_mean = mean([block['AvgResponseTime'] for block in task_dict_list if block['Block'] in rand_blocks])
    rule_mean = mean([block['AvgResponseTime'] for block in task_dict_list if block['Block'] in rule_blocks])

    block4_mean = task_dict_list[3]['AvgResponseTime']
    block5_mean = task_dict_list[4]['AvgResponseTime']

    return {'T4_RandomRT': random_mean, 'T4_RuleRT': rule_mean, 'T4_Block4RT': block4_mean,
            'T4_Block5RT': block5_mean}


def get5(task_dict_list):
    """
    Reads Task 5 dictionary list (output from read_file)
    and outputs summary data. Input looks like:

    {'AvgDistancePerTarget': 170.9032,
    'AvgFirstTen': 0.5186402,
    'AvgLastTen': 0.5875,
    'AvgLocation': 692.6765,
    'AvgTargetsPerArea': (5.0, 3.0, 6.0, 3.0, 4.0, 5.0, 5.0, 3.0),
    'AvgTimePerAction': 0.5415921,
    'AvgTimePerTarget': 0.5734504,
    'Duration': 19.51416,
    'EndCondition': 'completed',
    'NumBadTouches': 2,
    'NumGoodTouches': 34,
    'NumRepeats': 0,
    'StandardDeviation': 10.20111,
    'Task': 1}
    """


    values = map(mean, ([x['NumBadTouches'] for x in task_dict_list], [x['NumRepeats'] for x in task_dict_list],
                           [x['AvgDistancePerTarget'] for x in task_dict_list]))
    return zip(['T5_NumBadTouches', 'T5_NumRepeats', 'T5_AvgDistancePerTarget'], values)


def get6(task_dict_list):
    """
    :param task_dict_list: list of dictionaries output
                           by readTask1LogFile function

    """

    # Calculate the average number of bad touches per trial
    bad_touches = [x['NumBadTouches'] for x in task_dict_list]
    scores = [x['Score-incorrect only'] for x in task_dict_list]

    # We should always have 12 trials, and be looking at the first
    # six trials versus the last six trials, but I've added this
    # midpoint variable in case for some reason there's a different
    # number of trials.
    mid_point = len(bad_touches) / 2

    # Again, since there should be equal number of trials contributing
    # to avg_first and average_last, avg_total could be computed by
    # just doing mean([avg_first, avg_last]), but it's safer this way
    avg_total = mean(bad_touches)
    avg_first = mean(bad_touches[:mid_point])
    avg_last = mean(bad_touches[mid_point:])

    score_first = mean([score for score in scores[:mid_point] if score])
    score_last = mean([score for score in scores[mid_point:] if score])
    score_total = mean([score for score in scores if score])

    return {'T6_BadTouchesAllTrials': avg_total, 'T6_BadTouchesFirst': avg_first, 'T6_BadTouchesLast': avg_last,
            "T6_ScoreFirst": score_first, "T6_ScoreLast": score_last, "T6_ScoreAllTrials": score_total}
