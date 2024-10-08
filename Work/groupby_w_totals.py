"""
Started as sumby_w_totals.py, a script to group by specified fields and sum results.
This version will allow functions other than sum (count, etc) and more importantly, will add three functions that can
be called before:
groupby_w_totals_setup will provide prompts where required
groupby_w_totals_check will validate the fields before passing to the groupby_main function, groupby_w_totals
groupby_w_totals_sincere is particular to work with Sincere files and will fill fields accordingly.
"""

# TODO Is all the code below the if __file__ ok?  Especially the imports?  Is this how testing works?

# format of INDEX_VARS_W_SUMFLAG is list of pairs: (variable name, whether to subtotal)
# Order of variables is order/level of subtotaling


VALID_AGG_TYPES = ['sum', 'count', 'mean']  # TODO Replace with enum??

# class CustomException(Exception):
#     def __init__(self, msg='My default message', *args, **kwargs):
#         super().__init__(msg, *args, **kwargs)


def groupby_w_totals_check(df_in, raw_row_pairs_in, raw_aggregate_pairs_in):
    """
    Args:
        df_in (): dataframe to summarize.
        raw_row_pairs_in (): list of fields in df to be grouped-by, lowercase list.
        raw_aggregate_pairs_in (): list of fields in df to be aggregated.  Specified as pairs of (field,agg).
    """

    from loguru import logger
    from bekutils import setup_loguru
    from bekutils.bek_funcs import exit_yes

    check_string_elements_for_errors(raw_aggregate_pairs_in, VALID_AGG_TYPES)

    # make sure all fields are in df_in
    aggregate_fields = [var for var, sum_flag in eval(raw_aggregate_pairs_in)]
    missing_aggregate_fields = set(aggregate_fields) - set(df_in.columns)
    if len(missing_aggregate_fields) != 0:
        exit_yes(f"Aggregate fields {missing_aggregate_fields} are not in file to be summarized.", "MISSING FIELD", )

    check_string_elements_for_errors(raw_row_pairs_in, [True, False])

    row_fields = [var for var, sum_flag in eval(raw_row_pairs_in)]
    missing_row_fields = set(row_fields) - set(df_in.columns)
    if len(missing_row_fields) != 0:
        exit_yes(f"Row fields {missing_row_fields} are not in file to be summarized.", "MISSING FIELD", )


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


def check_string_elements_for_errors(raw_string_elements, option_list):
    """ check if var_string in proper format; raise exception if not.
    Proper format is a list of elements separated by commas, each element either a valid dataframe field name or a
    fielname followed by an option separated by a colon.
    'option' must be in list.

    Args:
        raw_string_elements (): string of comma separated fields or 'fields:option' like "field1, field2:mean"

    >>> check_string_elements_for_errors("var1*",VALID_AGG_TYPES)  # special char not allowed in field name (_-ok)
    Traceback (most recent call last):
    Exception: First item contains other than alphanumeric, underscore or dash
    >>> check_string_elements_for_errors("var1 : sumx", VALID_AGG_TYPES)
    Traceback (most recent call last):
    Exception: Option not in accepted list
    >>> check_string_elements_for_errors("var1, var2 ", VALID_AGG_TYPES)
    [['var1'], ['var2']]
    >>> check_string_elements_for_errors("var1 : sum, var2 ", VALID_AGG_TYPES)
    [['var1', 'sum'], ['var2']]
    >>> check_string_elements_for_errors("var1: True, var2", ['True', 'False'])  # booleans are read as str
    [['var1', 'True'], ['var2']]
    >>> check_string_elements_for_errors("var1: True, var2", [True, False])  # booleans are read as str
    Traceback (most recent call last):
    Exception: Option not in accepted list
    >>> check_string_elements_for_errors(None, VALID_AGG_TYPES)  # TODO how should no fields-summary line only be treated
    Traceback (most recent call last):
    AttributeError: 'NoneType' object has no attribute 'split'
    >>> check_string_elements_for_errors("999", VALID_AGG_TYPES)
    [['999']]
    >>> check_string_elements_for_errors("var1: bogus, var2", VALID_AGG_TYPES)  # option bogus not in list
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
    # elements = check_string_elements_for_errors(string_elements, VALID_AGG_TYPES)
    elements = parse_elements(string_elements)

    for element in elements:  # will be string (variable) or pair of string/variable and True/False
        if len(element) == 1:  # variable w no option
            pair = [element[0], default_param]
        else:  # var/option
            pair = element
        pairs.append(pair)

    return pairs


def groupby_w_totals_setup(input_file, df_in=None, raw_row_pairs_in=None, raw_aggregate_pairs_in=None,
                           default_agg_type='sum'):
    """
    Args:
        df_in (): dataframe to summarize. If not specified, the text input_file is uesd.  If neither, a prompt is given.

        input_file (): The text path to be used for df_in.  It is returned from the function in case it is selected
        so it can be used outside (ex in titles)

        raw_row_pairs_in (): list of fields in df to be grouped-by and whether to total by field (True/False).
        String separated by commas, converted to lowercase list. Default for total is False.

        raw_aggregate_pairs_in (): list of fields in df to be aggregated.  Simplest is string separated by commas, converted to
        lowercase list. Can be list of pairs = (field, agg_type).

        default_agg_type (): from the list VALID_AGG_TYPES

        >>> groupby_w_totals_setup(None,None)
        ['Factory', 'Name'],[('Total Addresses', 'sum'), ('Available Addresses', 'sum')],default_agg_type='count')
    """

    # import itertools
    from itertools import islice
    import numpy as np
    import pandas as pd
    from loguru import logger
    from bekutils import setup_loguru
    # from bekutils import autosize_xls_cols
    from bekutils.bek_funcs import exit_yes
    # from bekutils.bek_funcs import exit_yes_no
    from bekutils import get_file_name
    from pathlib import Path
    import pandas as pd
    from openpyxl.styles import Font

    # logger = setup_loguru('DEBUG', 'DEBUG')
    logger.info("testing")

    # get an input file
    if df_in is not None:
        pass
    elif input_file is not None:
        input_file = Path(input_file)
        if input_file.suffix == '.csv':
            df_in = pd.read_csv(input_file)
        elif input_file.suffix == '.xlsx':
            df_in = pd.read_excel(input_file)
        else:
            exit_yes(f"File type can not be read into dataframe. It is '{input_file.suffix}' and not csv or xlsx"
                     f"\n\nExiting.",
                     "BAD FILE TYPE FOR DATAFRAME")
    else:
        input_file = get_file_name("Pick File", "Pick a parent-campaign file to summarize (eg "
                                   "'parent-campaign-address-counts-2023-08-03.csv'",
                                   "~/Downloads/")
        if input_file.suffix == '.csv':
            df_in = pd.read_csv(input_file)
        elif input_file.suffix == '.xlsx':
            df_in = pd.read_excel(input_file)
        else:
            exit_yes(f"File type can not be read into dataframe. It is '{input_file.suffix}' and not csv or xlsx"
                     f"\n\nExiting.",
                     "BAD FILE TYPE FOR DATAFRAME")
    #     input_file = Path("/Users/Denise/Downloads/parent-campaign-address-counts-2023-08-03.csv").expanduser()
        # input_file = "/Users/Denise/Downloads/all-users-2024-01-06.csv"
    # convert all column names to lowercase
    df_in.columns = df_in.columns.str.lower().str.strip()

    if default_agg_type not in VALID_AGG_TYPES:
        exit_yes(f"Default aggregate type of '{default_agg_type}' not in '{VALID_AGG_TYPES}'.  \n\nExiting.",
                 "BAD DEFAULT AGGREGATE TYPE")

    # set up default fields and summary vars for Sincere report files
    if 'parent-campaign-address-counts' in str(input_file):
        df_in['remaining in room'] = df_in['assigned to organizations'] - df_in['assigned to writers']

        if raw_row_pairs_in is None:
            # raw_row_pairs_in = "[('factory', True), ('name', True), ]"
            raw_row_pairs_in = "factory: t, name: t"

        if raw_aggregate_pairs_in is None:
            # raw_aggregate_pairs_in = "[('total addresses', 'sum'), ('available addresses', 'sum'),\
            #                 ('assigned to organizations', 'sum'), ('assigned to writers', 'sum'),\
            #                 ('remaining in room', 'sum')\
            #                 ]"
            raw_aggregate_pairs_in = "total addresses: sum, available addresses: sum,\
                            assigned to organizations: sum, assigned to writers: sum,\
                            remaining in room: sum"

    if 'all-parent-campaigns-requests' in str(input_file):

        if raw_row_pairs_in is None:
            # raw_row_pairs_in = "[('factory_name', True), ('parent_campaign_name', True), " \
            #                         "('org_name', True), ('writer_name', True), ('team_name', True)]"
            raw_row_pairs_in = "factory_name: t, parent_campaign_name: t, " \
                                    "org_name: t, writer_name: t, team_name: t"

        if raw_aggregate_pairs_in is None:
            # raw_aggregate_pairs_in = "[('addresses_count', 'sum'),]"
            raw_aggregate_pairs_in = "addresses_count: sum"

    # can't check element list until defaults are set based on file name
    # check_string_elements_for_errors(raw_row_pairs_in, [True, False])
    check_string_elements_for_errors(raw_row_pairs_in, ['t', 'f'])
    check_string_elements_for_errors(raw_aggregate_pairs_in, VALID_AGG_TYPES)

    # convert list of 'elements' to proper 'pairs' substituting default 'option' if missing
    # row_pairs_out = fill_field_pairs(raw_row_pairs_in, False)
    row_pairs_out = fill_field_pairs(raw_row_pairs_in, 'f')
    aggregate_pairs_out = fill_field_pairs(raw_aggregate_pairs_in, default_agg_type)

    # replace var names with lowercase now that all are pairs
    row_pairs_out = [[var.lower(), option] for var, option in row_pairs_out]
    aggregate_pairs_out = [[var.lower(), option] for var, option in aggregate_pairs_out]

    raw_row_pairs_out = str(row_pairs_out)
    raw_aggregate_pairs_out = str(aggregate_pairs_out)

    return input_file, df_in, raw_row_pairs_out, raw_aggregate_pairs_out


def groupby_w_totals(df_in, raw_index_pairs, raw_agg_pairs):
    """ pivot with sumtotals"""

    import itertools
    import numpy as np
    import pandas as pd
    from loguru import logger

    logger.info("Just go into groupby_w_totals")
    # vlue to represent totalled lines; must have special char prefix to sort correctly
    TOTAL_STR = '_TOTAL'

    index_pairs = eval(raw_index_pairs)
    agg_pairs = eval(raw_agg_pairs)

    index_var_dict = {val[0]: val[1] for val in index_pairs}
    index_vars = list(index_var_dict.keys())
    # index_vars_to_sum = [field for index, (field, sum_flag) in enumerate(index_pairs) if sum_flag]
    index_vars_to_sum = [field for index, (field, sum_flag) in enumerate(index_pairs) if sum_flag.lower() == 't']

    # replace nan with " " to make sorting with _TOTAL correct
    df_in[index_vars] = df_in[index_vars]. fillna('')

    # TODO make aggtype part of sumvar pair
    # dictionary of all summed fields field:'sum'
    summed_fields_dict = {fld: option for fld, option in agg_pairs}

    # create df summed by break of all fields in index_vars
    df_base = df_in.groupby(index_vars, dropna=False).agg(summed_fields_dict)
    a=1

    # summed_dfs is a list of df objects, each a summ on a different level
    summed_dfs = []

    # series1 is grand total for all
    series1 = df_base.sum()
    summed_dfs.append(series1.to_frame().transpose())

    logger.info('combinations')
    # in itertools.combinations, second param is the length of the subsequences (eg 2 would produce pairs, 3 triples).
    # creates dataframes summed by combinations of variables
    # Skip summary dfs if len(index_vars_to_sum)==0 and don't run final if seq_len == len(index_vars) because that
    # would duplicate base_df
    if len(index_vars_to_sum) > 0:
        for seq_len in range(1, min(len(index_vars_to_sum) + 1, len(index_vars)) ):
            for temp_sum_vars in itertools.combinations(index_vars_to_sum, seq_len):
                logger.debug(f"{seq_len=},{temp_sum_vars=}")
                # create summed df and add to summed_dfs list
                # summed_dfs.append(df_base.groupby(level=temp_sum_vars).sum())
                summed_dfs.append(df_base.groupby(level=temp_sum_vars, dropna=False).sum())
                a=1

    # get index into correct format with correct number of fields (len(index_vars)) and TOTAL_STR in correct columns
    for df in summed_dfs:
        # check index type because some are not multiindex and have no len (grand total), some str and not iterable
        index_obj = df.index.values[0]  # so we can check index type

        if isinstance(index_obj, (list, tuple)):
            # This is general case, multiindex summary summed_dfs.
            # The variables are:
            #   df.index.values is an numpy ndarray, len = # of df rows, each value a tuple representing
            #   the index
            #   value for the row comprised of the field values.  Eg if multiindex is animal, count, state, df.index.values
            #   could be [('dog','1','NJ),('dog','2','CA'),('cat','1','NJ)]

            #
            # there's a neat trick to create individual list of index values from the tuples above:
            #   list(zip(*df.index.values)) would take [('dog','1','NJ),('dog','2','CA'),('cat','1','CA)]
            #   and produce [('dog','dog','cat'),('1','2','1'),('NJ','CA','CA')]
            # https://stackoverflow.com/questions/12974474/how-to-unzip-a-list-of-pairs-into-individual-lists
            #
            #   index_array: produced with index_array = len(index_vars) * [len(df.index.values) * [TOTAL_STR]].
            #   a list of lists with dimensions: # vars high by # of df rows wide filled with value of TOTAL_STR.
            #   TODO what does this mean?
            #   the list index will correspond to the column number for a variable, so we can replace the TOTAL_STR
            #   values with the index values from the summed df.  like
            #       index 0 = [_TOTAL,_TOTAL,_TOTAL,_TOTAL,]
            #       index 1 = [_TOTAL,_TOTAL,_TOTAL,_TOTAL,]
            #
            # df.MultiIndex.from_arrays(index_array) is used to convert arrays to MultiIndex.  Opposite of list(zip(*df.index.values))
            # for example:
            #   arrays = [[1, 1, 2, 2], ['red', 'blue', 'red', 'blue']]
            #   df.MultiIndex.from_arrays(arrays, names=('number', 'color'))
            #   MultiIndex([(1,  'red'),
            #             (1, 'blue'),
            #             (2,  'red'),
            #             (2, 'blue')],
            #            names=['number', 'color'])

            # The steps of forming the index are:
            # todo finish steps

            #   2. split df.index.values into a list of lists (actually pairs) where each list is the values down
            #   the rows.

            #   3. create a dictionary of filename to separate index
            #   4. replace the corresponding rows in the array with the index values
            #   5. create a multiindex for the df from the index array were row arrays become elements of index pairs

            index_array = len(index_vars) * [len(df.index.values) * [TOTAL_STR]]
            separate_indexes = list(zip(*df.index.values))

            # pairs of col name and list of index values
            # field_w_separate_indexes = list(zip(df.index.names, separate_indexes))

            # field_to_separate_indexes_dict = {field_and_index[0]: field_and_index[1] for field_and_index in field_w_separate_indexes}
            # dictionary = dict(zip(keys, values))
            field_to_separate_indexes_dict = dict(zip(index_vars, separate_indexes))

            for column_field in df.index.names:
                # below loops though to get index number in multiindex of field
                # index_in_multiindex = [index_vars_w_sumflag[0] for index_vars_w_sumflag in index_vars_w_sumflag_formatted].index(column_field)
                index_number_in_multiindex = index_vars.index(column_field)
                index_array[index_number_in_multiindex] = field_to_separate_indexes_dict[column_field]
            df.index = pd.MultiIndex.from_arrays(index_array)

        # elif isinstance(index_obj, str):
        elif type(df.index.values[0]) == np.int64:  # grand total row
            # below fills an array to number of index_vars (len(index_vars)) repeating (*) a list filled with the
            # TOTAL_STR, like [['_TOTAL'], ['_TOTAL']], then uses the array as the multiindex
            index_array = len(index_vars) * [[TOTAL_STR]]
            df.index = pd.MultiIndex.from_arrays(index_array)
        elif len(df.index.names) == 1:  # not a multiindex, just one variable used as index
            # index is only one variable, so need to build it up and add a column of "_TOTAL"
            # start with index_aray (# vars wide) by (# rows long) filled with "_TOTAL", then replace column with
            # original index
            index_array = len(index_vars) * [len(df.index.values) * [TOTAL_STR]]

            # sub index_var position below
            index_array[index_vars.index(df.index.names[0])] = df.index.values
            df.index = pd.MultiIndex.from_arrays(index_array)
        else:
            logger.error(df.index.values[0], ' is not pair or string or np.int64')
            index_array = df.index.values + \
                          (len(index_vars) - len(df.index.values[0])) * [[TOTAL_STR]]
            df.index = pd.MultiIndex.from_arrays(index_array)

    # concat all dataframes together, sort index
    df_out = df_base
    for df in summed_dfs:
        df_out = pd.concat([df_out, df])

    df_out.index.names = index_vars
    level_list = list(range(0, len(index_vars)-1))

    df_out = df_out.sort_index(key=lambda x: x.str.upper())
    # df_out = df_out.sort_index(level=None, key=lambda x: x.str.upper(), inplace=True)
    logger.debug('df_combine index names', df.index.names)

    logger.info("df created - returning")
    
    return df_out

def write_xls_report(df_pt, title1="", title2="", title3="", title4=""):
    """ write and format a df to xls """

    import pandas as pd
    from bekutils import autosize_xls_cols

    # op_file =op_file
    op_file = Path(__file__).stem
    writer = pd.ExcelWriter(op_file + ".xlsx")

    df_pt.to_excel(writer, sheet_name="Summary Report", startrow=6)
    wb = writer.book
    for sh in wb.worksheets:
        autosize_xls_cols(sh)

    for sh in wb.worksheets:
        sh['A1'].value = title1
        sh['A1'].font = Font(b=True, size=20)
        sh['A2'].value = title2
        sh['A3'].value = title3
        sh['A3'].font = Font(size=12)
        sh['A4'].value = title4

    writer.close()

def main(input_file=None):
    """ """

    INPUT_FILE, df, index_vars, agg_vars = groupby_w_totals_setup(input_file)

    # check info created above
    groupby_w_totals_check(df, index_vars, agg_vars)

    df_pt = groupby_w_totals(df, index_vars, agg_vars)

    write_xls_report(df_pt, title1="Summary Report", title3=f"Source data: {INPUT_FILE.name}")

    # sum_Group - return df?

    # if __main__ then
    #     write xls report


if __name__ == '__main__':

    # import doctest
    # doctest.testmod(verbose=True)

    INPUT_FILE = "/Users/Denise/Downloads/all-parent-campaigns-requests-2024-05-01.csv"

    from bekutils import setup_loguru
    from bekutils import autosize_xls_cols
    # from bekutils.bek_funcs import exit_yes
    # from bekutils.bek_funcs import exit_yes_no
    from bekutils import get_file_name

    from pathlib import Path
    import pandas as pd
    from openpyxl.styles import Font

    logger = setup_loguru('DEBUG', 'DEBUG')
    logger.info("testing")

    main(INPUT_FILE)

    # will prompt for input file and set summary defaults for Sincere files
    # df, index_vars, agg_vars = groupby_w_totals_setup(
    #     "/Users/Denise/Downloads/parent-campaign-address-counts-2023-08-03.csv",
    #     [('FactoryX', True), ('Name', True), ],
    #     [('Total Addresses', 'sum'), ('Available Addresses', 'sum'),
    #      ('Assigned to Organizations', 'sum'), ('Assigned to Writers', 'sum'),
    #     ])

    # df, index_vars, agg_vars = groupby_w_totals_setup("/Users/Denise/Downloads/parent-campaign-address-counts-2023-08-03.csv",)

    INPUT_FILE, df, index_vars, agg_vars = groupby_w_totals_setup(INPUT_FILE)

    # check info created above
    groupby_w_totals_check(df, index_vars, agg_vars)

    df_pt = groupby_w_totals(df, index_vars, agg_vars)

    write_xls_report(df_pt, title1 = "Summary Report", title3 = f"Source data: {INPUT_FILE.name}" )

    # FOR TESTING select only certain records
    # sincere_data = sincere_data.loc[sincere_data['Factory'] == "VA General BIPOC 7-2023"]
    # sincere_data = sincere_data[~sincere_data['Name'].str.lower().str.contains("test")]
    # sincere_data = sincere_data[sincere_data['organization'].str.lower().isin(["fl - entire state", "general",
    #                                                                            "national-bob haar"])]

    # sincere_data = sincere_data[~sincere_data['name'].str.lower().str.contains("test")]


    a = 1
