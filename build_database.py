__author__ = 'margaretsheridan'
import os
import data_class as dat
import cPickle as pickle
subjects = {}
bad_subs  = set()
# Iterate over all the files
for log_file in [os.path.join('YL_DATA_PERU',f) for f in os.listdir('YL_DATA_PERU')]:

    # Check if the current subject number is in our dictionary
    with open(log_file,"rU") as in_file:
        log_data = dat.data_file(in_file)

        if (log_data.ID, log_data.group, log_data.sibling) not in subjects:
            subjects[(log_data.ID, log_data.group, log_data.sibling)] = dat.subject(log_data.ID, log_data.group, log_data.sibling)
            # See if the group and siblinghood are the same
        else:
            if log_data.sibling != subjects[(log_data.ID, log_data.group, log_data.sibling)].sibling:
                print "Conflicting sibling info for subject %s" % log_data.ID
                bad_subs.add(log_data.ID)
            if log_data.group != subjects[(log_data.ID, log_data.group, log_data.sibling)].group:
                print "Conflicting Group Info for subject: %s" % log_data.ID
                bad_subs.add(log_data.ID)
            if log_data.task in subjects[(log_data.ID, log_data.group, log_data.sibling)].data:
                print "Multiple %s files for subject %s" % (log_data.task, log_data.ID)
                bad_subs.add(log_data.ID)

        subjects[(log_data.ID, log_data.group, log_data.sibling)].add_data(log_data.task, log_data)

with open("SUBJECTS2.pck", "wb") as f:
    pickle.dump((subjects, bad_subs), f)


# Iterate over the new dictionary
for sub in subjects:
    subjects[sub].write_summary('SUMMARY.csv')