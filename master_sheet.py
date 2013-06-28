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
    mid_point = len(bad_touches)/2

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
    out_dict = defaultdict(lambda: defaultdict())

    # Divide trial types according to how they differ from previous trials
    out_dict['Switch-Rule']['trials'] = [trial for trial in task_dict_list if trial['Switch-rule'] is True]
    out_dict['Switch-Side']['trials'] = [trial for trial in task_dict_list if trial['Switch-side'] is True]
    out_dict['Non-Switch-Rule']['trials'] = [trial for trial in task_dict_list if trial['Switch-rule'] is False]
    out_dict['Non-Switch-Side']['trials'] = [trial for trial in task_dict_list if trial['Switch-side'] is False]

    # Divide trial types based on rule
    out_dict['Same']['trials'] = [trial for trial in task_dict_list if trial['TargetSide'] == 'Opposite']
    out_dict['Opposite']['trials'] = [trial for trial in task_dict_list if trial['TargetSide'] == 'Same']

    # Calculate Average RT and Accuracy for each type of trial
    for trial_type in out_dict:
        out_dict[trial_type]['Accuracy'] = np.mean([float(x['Correct']) for x in out_dict[trial_type]['trials']])
        out_dict[trial_type]['ReactionTime'] = np.mean([float(x['ReactionTime']) for x in out_dict[trial_type]['trials']])
        del out_dict[trial_type]['trials']

    return out_dict



def get3(task_dist_list)


