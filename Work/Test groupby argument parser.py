""" test alternatives to passing field and options without tuples """

VALID_AGG_TYPES = ['sum', 'count', 'mean']  # TODO Replace with enum??


def parse_elements(raw_elements) :
    """ parse list of fields separated by ',' or field/option pairs separated by ':'s into list of lists
    >>> parse_elements(" x ")
    [['x']]
    >>> parse_elements(" x , y ")
    [['x'], ['y']]
    >>> parse_elements("  x , y : sum ")
    [['x'], ['y', 'sum']]

    Args:
        raw_elements (): string of comma separated fields or 'fields:option' like "field1, field2:mean"

    """
    elements = [element.strip() for element in raw_elements.split(',')]
    items = [[item.strip() for item in element.split(':')] for element in elements]
    return items


def check_string_elements_for_errors_new(raw_string_elements, option_list):
    """ check if var_string in proper format; raise exception if not.
    Proper format is a list of elements separated by commas, each element either a valid dataframe field name or a
    fielname followed by an option separated by a colon.
    'option' must be in list.

    Args:
        raw_string_elements (): string of comma separated fields or 'fields:option' like "field1, field2:mean"

    >>> check_string_elements_for_errors_new("var1*",VALID_AGG_TYPES)  # special char not allowed in field name (_-ok)
    Traceback (most recent call last):
    Exception: First item contains other than alphanumeric, underscore or dash
    >>> check_string_elements_for_errors_new("var1 : sumx", VALID_AGG_TYPES)
    Traceback (most recent call last):
    Exception: Option not in accepted list
    >>> check_string_elements_for_errors_new("var1, var2 ", VALID_AGG_TYPES)
    [['var1'], ['var2']]
    >>> check_string_elements_for_errors_new("var1 : sum, var2 ", VALID_AGG_TYPES)
    [['var1', 'sum'], ['var2']]
    >>> check_string_elements_for_errors_new("var1: True, var2", ['True', 'False'])  # booleans are read as str
    [['var1', 'True'], ['var2']]
    >>> check_string_elements_for_errors_new("var1: True, var2", [True, False])  # booleans are read as str
    Traceback (most recent call last):
    Exception: Option not in accepted list
    >>> check_string_elements_for_errors_new(None, VALID_AGG_TYPES)  # TODO how should no fields-summary line only be treated
    Traceback (most recent call last):
    AttributeError: 'NoneType' object has no attribute 'split'
    >>> check_string_elements_for_errors_new("999", VALID_AGG_TYPES)
    [['999']]
    >>> check_string_elements_for_errors_new("var1: bogus, var2", VALID_AGG_TYPES)  # option bogus not in list
    Traceback (most recent call last):
    Exception: Option not in accepted list

    """
    import re
    from loguru import logger

    # Characters allowed in dataframe field names
    valid_field_pattern = "^[A-Za-z0-9_-]*$"

    elements = parse_elements(raw_string_elements)

    # check elements to make sure they are list of variables or of variable, agg_type
    for element in elements:  #
        # should be string (variable) or pair of string/variable and agg_type
        if len(element) > 2:
            logger.info(f"'{element}' has more than two items.")
            raise Exception("Element has more than two items.")
        if len(element) > 0:
            # if isinstance(element[0], str):  # variable  FIXME check for valid characters using regex
            if bool(re.match(valid_field_pattern, element[0])):  # field contains only alphanumeric, underscore or dash
                pass
            else:
                logger.info(f"First item '{element[0]}' contains other than alphanumeric, underscore or dash.")
                raise Exception("First item contains other than alphanumeric, underscore or dash")
        if len(element) > 1:
            if element[1] in option_list:  # acceptable option
                pass
            else:
                logger.info(f"Second item '{element[1]}' is not a valid option, '{option_list}'.")
                raise Exception('Option not in accepted list')
        if len(element) <= 0:
            logger.info(f"Length of '{element}' 0 or less.")
            raise Exception("Length of 'element' 0 or less.")
    return elements


def fill_field_pairs(string_elements, default_param):
    """ fill the second argument in a field list with optional second parameter

    Args:
        string_elements (): string of comma separated fields or 'fields:option' like "field1, field2:mean"
        default_param (): value to fill blank option item of non-paird elements

    >>> fill_field_pairs("var1", 'mean')
    [['var1', 'mean']]
    >>> fill_field_pairs("var1, var2 : count", 'sum')
    [['var1', 'sum'], ['var2', 'count']]
    """

    pairs = []
    # evaled_string_elements = eval(string_elements)
    elements = check_string_elements_for_errors_new(string_elements, VALID_AGG_TYPES)

    for element in elements:  # will be string (variable) or pair of string/variable and True/False
        if len(element) == 1:  # variable w no option
            pair = [element[0], default_param]
        else:  # var/option
            pair = element
        pairs.append(pair)

    return pairs



if __name__ == '__main__':
    # check_string_elements_for_errors_new("var1*",VALID_AGG_TYPES)  # specified option_list ok
    # check_string_elements_for_errors_new("var1: True, var2", ['True', 'False'])  # specified option_list ok
    # check_string_elements_for_errors_new("var1 : sumx", VALID_AGG_TYPES)
    # check_string_elements_for_errors_new("var1, var2, ", VALID_AGG_TYPES)

    # print(f"{parse_elements(' x')=}")
    # print(f"{parse_elements(' x, y')=}")
    # print(f"{parse_elements('x,  y,  z:  sum')=}")

    a=1
