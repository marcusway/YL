YL
==

Code for organizing and analyzing output files from a battery of cognitive games being used for an international study on cognitive development

Dependencies
==
Code was developed in a Python 2.7 environment.  Imports include:

cPickle <br>
csv <br>
os <br>
re <br>
shelve <br>
warnings <br>

All of these are built-in modules in Python 2.7 so if you have Python 2.7, you shouldn't need to install anything else. 

General Use:  build_database.py
==

Once you have cloned the YL directory to your machine, cd into the YL/ directory. The only file that you will actually be running is build_database.py.  To run it, from the YL directory, type: python build_database.

<br><br>

The program will prompt you to enter the path to the folder where your log files are stored. This is the directory where the program will look for files to parse. To parse and process the files in the YL_DATA_PERU folder in my Dropbox, I would enter /Users/marcusway/Dropbox/YL_DATA_PERU at the prompt (Note: this path may be relative or absolute, but don't use '~' to represent your home directory.  It won't work.). If you enter a path to something other than a directory, you'll get the same prompt again until you enter a valid path.  

<br><br>

Next, you will be prompted to enter the path to a spreadsheet (including the file name, itslef!) where summary data will be stored.  Any path will do, but the extension should be .csv since the output will be comma-separated.  If you enter the name of a pre-existing file, you will be asked whether or not you wish to overwrite the file.  If you choose not to overwrite, subject data will be appended to the pre-existing file.  

<br>
<br>

Some likely messages you will encounter while the program is running:
<br>
<b>Bad File Format</b>: If a file in the log file folder does not follow the proper naming convention, 
this is reported and the file is skipped and excluded from analysis.  The names of such files are printed to the screen so if you have incorrectly named files, you will know which ones they are so you can change them. 
<br>
<b>Multiple Task X Files</b>: If there are multiple files sharing the same subject and task numbers, this will be reported. Right now, the default behavior for this scenario is to simply use the last one encountered by the program, but these files should be investigated.
<br>
<b>Success!</b> If the program has run successfully, you'll see a message that reads "All done!"

Outputs
==
Once the program has exited successfully, it will have generated a number of new files.  These files are:<br>

<b>The summary file</b>: this is the one you were asked to name at the prompt.  It should be a .csv spreadsheet where each row contains summary data across all tasks for one subject. 
<br>
<b>YL_DATABASE</b>: this is a Python shelve database file that contains data for all of the subjects. It is automatically stored in the YL directory (the same one that contains the code) More on this later. 
<br>
<b>PROCESSED_FILES.pck</b>: a pickled list containing the names of all of the files that have been successfully parsed by the build_database.py script.  This, too, will be stored in the YL directory.  The purpose of this file is to avoid rewriting the entire database everytime build_database.py is run.
<br>
<b>task files</b>: There should be six files, task1.csv, task2.csv, ..., task6.csv saved in the YL/ directory.  These files contain trial-by-trial output for all subjects for the titular task.  So each row corresponds to a single trial.


Important Notes
==
<br>
<b> Overwrite overwrites everything (but not your log files!)</b>
<br>
When you choose the overwrite option, not only will your summary file (the one you specify) be overwritten, but so will the YL_DATABASE and PROCESSED_FILES.pck files.  For example, if you are overwriting because you previously included a bad log file for some subject and want to use a different one, you should remove the bad one from the log files directory and re-run build_database.py, instructing an overwrite.  If you don't overwrite, the file will be ignored since it was already encountered in a previous running of build_database.py. So when in doubt, overwrite (as long as you have all the log files).  This way ensures that your output will match the current data in your log files folder. However, You would not want to overwrite if you are reading from a folder that contains just a subset of log files.  For example, if for some reason I have my log files split between two folders, f1 and f2, I would want to run build_database.py using f1 as my log file folder.  Then, to add the data from f2, I would run it again using f2 as my log file folder and choose NOT to overwrite.

Accessing DATABASE
==
Output from log files is stored in a shelve database, which acts very much like a Python dictionary.  It is something of an experiment, but it's meant to give you a little more flexibility in accessing data that you're interested in.  To explore the database, start an interactive python session:

>>import shelve
>>db = shelve.open("DATABASE")

To see how many subjects have been run, try:
>>len(db)

To see all of their subject ID keys:
>>db.keys()

Each entry corresponds to an instance of the subject class, defined in data_classes.py. To see the information associated with a particular subject, for example, 'PE121001' (if s/he is in there!), try:

>>db['PE121001'].__dict__

and you'll get something like this:

>>{'ID': '1001',
>> 'data': {'task1': <data_classes.data_file instance at 0x104ae7bd8>,
>>  'task2': <data_classes.data_file instance at 0x104ae7cf8>,
>>  'task3': <data_classes.data_file instance at 0x104ae7830>,
>>  'task4': <data_classes.data_file instance at 0x104ae7638>,
>>  'task5': <data_classes.data_file instance at 0x104ae7b48>,
>>  'task6': <data_classes.data_file instance at 0x104ae7d88>},
>> 'group': '12',
>> 'key': 'PE121001',
>> 'sibling': False}

Any of these fields can be accessed with dot notation (i.e, db['PE121001'].group returns '12') The 'data' dictionary has keys 'task1', 'task2', ..., 'task6', whose corresponding values are data_file objects generated by the original log files.  To see the information associated with, for instance, task3:

>>db['PE121001'].data['task1'].__dict__.keys()

returns something like this: 

>>['task_headers',
>> 'task',
>>'group',
>> 'practice_headers',
>> 'practice',
>> 'filename',
>> 'sibling',
>> 'key',
>> 'time',
>> 'device',
>> 'ID',
>> 'summary',
>> 'date',
>> 'trial_by_trial']
 
 Similarly, we can use dot notation to access this information.  For instance:
 
 >>db['PE121001'].data['task1'].summary
 
 returns a summary of the data from task 1 for subject PE121001.  These are the same data that are written to the summary file. 
 >>{'T1_BadTouchesAllTrials': 1.25,
 >>'T1_BadTouchesFirst': 1.3333333333333333,
 >>'T1_BadTouchesLast': 1.1666666666666667,
 >>'T1_ScoreAllTrials': 1.375,
 >>'T1_ScoreFirst': 1.5,
 >'T1_ScoreLast': 1.25}
 
You can also look at trial by trial data for the same task by examining 
>>bd['PE121001'].data['task1'].trial_by_trial

So if you wanted to do something really ambitious, like say, look at the median number of bad touches across all subjects on only the very first trial of task one, you could do something like:
>>import numpy as np 

If you have NumPy

>>avg = np.median([bd[sub].data['task1'].trial_by_trial[0]['NumBadTouches'] for sub in db])

For what it's worth, I get 2.0 for this 

<br><br>



