"""
Some classes for handling problems that
seem likely to occur
"""

class BadLineError(Exception):
    """
    raise when the contents of the
    file to read are in an unexpected format
    """
    pass


class BadFileNameError(Exception):
    """
    raise when a file name is not of the
    expected format
    """
    pass

class TaskNameError(Exception):
    """
    raise when an invalid task name is used
    """


