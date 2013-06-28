__author__ = 'margaretsheridan'


# These functions aim to grab the summary data that we want out of
# the task dictionaries created from log file data.  The input
# dictionaries are the output of the readTaskXLogFile() functions

def get1(task_dict_list):
    """
    :param task_dict_list: list of dictionaries output
                           by readTask1LogFile function

    """
    import numpy as np

    # Calculate the average number of bad touches per trial
    bad_touches = [x['NumBadTouches'] for x in task_dict_list]

    # We should always have 12 trials, and be looking at the first
    # six trials versus the last six trials, but I've added this
    # midpoint variable in case for some reason there's a different
    # number of trials.
    mid_point = len(bad_touches) / 2

    # Again, since there should be equal number of trials contributing
    # to avg_first and average_last, avg_total could be computed by
    # just doing np.mean([avg_first, avg_last]), but it's safer this way
    avg_total = np.mean(bad_touches)
    avg_first = np.mean(bad_touches[:mid_point])
    avg_last = np.mean(bad_touches[mid_point:])

    return {'T1_BadTouches_AllTrials': avg_total, 'T1_BadTouches_First': avg_first, 'T1_BadTouchesLast:': avg_last}


def get2(task_dict_list):
    """
    :param task_dict_list: list of dictionaries output
                           by readTask1LogFile function
    {'Correct': '1',
    'DistanceFromCenter': '33.87108',
    'GoalSide': ' Left',
    'PressedSide': ' Left',
    'ReactionTime': '1.047791',
    'Switch-rule': 'switch',
    'Switch-side': 'non-switch',
    'TargetSide': 'Opposite',
    'TimeOut': 'False',
    'TouchPosition': '308;379',
    'TrialNum': '60'}

    """

    import numpy as np
    from collections import defaultdict

    # Make lists of types of trials
    trial_type_dict = {}

    # The dictionary to be returned will be nested such that
    # each key will be a trial type whose corresponding value
    # is a dictionary with keys 'Accuracy' and 'ReactionTime'
    out_dict = defaultdict(lambda: defaultdict())

    # Divide trial types according to how they differ from previous trials
    for switch_condition in ['SwitchRule', 'SwitchSide']:
        trial_type_dict[switch_condition] = [trial for trial in task_dict_list if trial[switch_condition] is True]
        trial_type_dict["Non" + switch_condition] = \
            [trial for trial in task_dict_list if trial[switch_condition] is False]

    # Divide trial types based on rule
    trial_type_dict['Same'] = [trial for trial in task_dict_list if trial['TargetSide'] == 'same']
    trial_type_dict['Opposite'] = [trial for trial in task_dict_list if trial['TargetSide'] == 'opposite']

    # Calculate Average RT and Accuracy for each type of trial
    for trial_type in trial_type_dict:
        out_dict[trial_type]['Accuracy'] = np.mean([float(x['Correct']) for x in trial_type_dict[trial_type]])
        out_dict[trial_type]['ReactionTime'] = np.mean([float(x['ReactionTime']) for x in trial_type_dict[trial_type]])

    return out_dict


def get3(task_dict_list):
    """
    Reads Task 3 list of dictionaries.  Importantly, each list member for
    task three corresponds to an individual dot press, not an individual trial
    (there may be 1,2, or 3 dot presses per trial).

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

    import numpy as np

    trials = []
    trial_num = None

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
        acc_by_load[i] = np.mean([np.mean([dot[0] for dot in trial if dot[0] is not None])
                                  for trial in trials if len(trial) == i])
    acc_by_delay = {}
    for delay in [.1, 3]:
        acc_by_delay[delay] = np.mean([np.mean([dot[0] for dot in trial if dot[0] is not None])
                                      for trial in trials if trial[0][1] == delay])

    return acc_by_delay, acc_by_load


def get4(get_task_dict):
    


