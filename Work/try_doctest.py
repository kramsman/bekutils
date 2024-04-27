""" try doctest """

class CustomException(Exception):
    def __init__(self, msg='My default message', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


def div_vars(a, b):
    """ add two numbers
    >>> div_vars(6, 2)
    3.0
    >>> div_vars(6.0, 2.0)
    3.0
    >>> div_vars(6, 0)
    Traceback (most recent call last):
    ZeroDivisionError: division by zero
    """
    return float(a / b)

raise CustomException('ERRORED HERE')
a=1
