""" try out pydantic for use in validating aggregate elements passed to group_by program

    # >>> check_string_elements_for_errors(None, VALID_AGG_TYPES)  # multi vars ok
    # Traceback (most recent call last):
    # Exception: Field_vals can not be evaluated by python, is not a valid python object
    # >>> check_string_elements_for_errors("'var1','var2', 'var3'", VALID_AGG_TYPES)  # multi vars ok
    # >>> check_string_elements_for_errors("('varx','sum'),'var2',", VALID_AGG_TYPES)  # pair ok
    # >>> check_string_elements_for_errors("('varx', True),'var2',", [True, False])  # specified option_list ok
    # >>> check_string_elements_for_errors("['varx','sum'],'var2',", VALID_AGG_TYPES)  # list ok
    # >>> check_string_elements_for_errors("['varx','sum','dummy'],'var2',", VALID_AGG_TYPES)  # third ignored element ok
    # >>> check_string_elements_for_errors("['varx','sum'],'var2',", VALID_AGG_TYPES)  # list ok
    # >>> check_string_elements_for_errors("999", VALID_AGG_TYPES)  # not a variable
    # Traceback (most recent call last):
    # Exception: Passed string is not a valid format, may be missing quotes
    # >>> check_string_elements_for_errors("['varx','wrong'],'var2',", VALID_AGG_TYPES)  # agg_type not in list
    # Traceback (most recent call last):
    # Exception: Option not in accepted list
    # >>> check_string_elements_for_errors("var1,(var2,sum, var3, var4", VALID_AGG_TYPES)  # missing closing )
    # Traceback (most recent call last):
    # Exception: Field_vals can not be evaluated by python, is not a valid python object
    # >>> check_string_elements_for_errors("'var1,'var2', 'var3'", VALID_AGG_TYPES)  # missing var1 closing quote
    # Traceback (most recent call last):
    # Exception: Field_vals can not be evaluated by python, is not a valid python object
    # >>> check_string_elements_for_errors("['varx','sum','var2',", VALID_AGG_TYPES)  # missing close bracket ]
    # Traceback (most recent call last):
    # Exception: Field_vals can not be evaluated by python, is not a valid python object

    """

from enum import Enum
from pydantic import BaseModel, validate_call
from typing import List, Optional

# VALID_AGG_TYPES = ['sum', 'count']

class VALID_AGG_TYPES(Enum):
    sum = "sum"
    count = "count"
    mean = 'mean'

# class Employee(BaseModel):
#     employee_id: UUID = uuid4()
#     name: str
#     email: EmailStr
#     date_of_birth: date
#     salary: float
#     department: Department
#     elected_benefits: bool

# class Foo(BaseModel):
#     count: int
#     size: Optional[float] = None

class aggregate_element(BaseModel):
    fieldname : str
    aggregate_function : Optional[VALID_AGG_TYPES] = 'sum'

class aggregate_elements(BaseModel):
    elements : List[aggregate_element]

class aggregate_pair(BaseModel):
    fieldname : str
    aggregate_function : VALID_AGG_TYPES

@validate_call
def read_aggregate_elements(agg_elem: aggregate_element):
    print("Is it ok?")

element1 = aggregate_element(fieldname='var1', aggregate_function='mean')


read_aggregate_elements(element1)
read_aggregate_elements('var1', 'mean')
a=1
