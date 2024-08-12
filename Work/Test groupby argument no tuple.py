""" test alternatives to passing field and options without tuples """
import pandas as pd

VALID_AGG_TYPES = ['sum', 'count', 'mean']  # TODO Replace with enum??


def groupby_w_totals_setup(*, input_file: str = None, df_in: pd.DataFrame = None, raw_row_pairs_in: str = None,
                           raw_aggregate_pairs_in: str = None,
                           default_agg_type: str = 'sum',
                           filter_df:str = None,
                           **kwargs):
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

        >>> groupby_w_totals_setup(raw_row_pairs_in=None, raw_aggregate_pairs_in=None)
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

    if raw_row_pairs_in is None and raw_aggregate_pairs_in is None:
        all_default_fields = True
    else:
        all_default_fields = False

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
        logger.info(f"Picked input file is '{input_file}'")

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

    # code = compile(
    #     "df_pt['percent assigned to rooms'] = df_pt['assigned to organizations_SUM'] / df_pt['total addresses_SUM']; df_pt['percent assigned to writers'] = df_pt['assigned to writers_SUM'] / df_pt['total addresses_SUM'];",
    #     '<string>', 'exec')
    df_in = eval(filter_df)
    # df_in = df_in[(df_in['factory'].notna() & ~df_in['name'].str.lower().str.contains('test'))]

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
            # raw_row_pairs_in = "factory_name: t, parent_campaign_name: t, " \
            #                         "org_name: t, writer_name: t, team_name: t"
            raw_row_pairs_in = "factory_name: t, parent_campaign_name: t, org_name"
            raw_row_pairs_in = "factory_name: t"

        if raw_aggregate_pairs_in is None:
            # raw_aggregate_pairs_in = "[('addresses_count', 'sum'),]"
            raw_aggregate_pairs_in = "addresses_count: sum"

    row_pairs = parse_elements(raw_row_pairs_in)
    # check pair formats and options
    check_string_elements_for_errors(row_pairs, option_list=['t', 'f'])
    # convert list of 'elements' to proper 'pairs' substituting default 'option' if missing
    row_pairs_out = fill_field_pairs(row_pairs, 'f')

    aggregate_pairs = parse_elements(raw_aggregate_pairs_in)
    check_string_elements_for_errors(aggregate_pairs, option_list=VALID_AGG_TYPES)
    aggregate_pairs_out = fill_field_pairs(aggregate_pairs, 'sum')

    # replace var names with lowercase now that all are pairs
    row_pairs_out = [[var.lower(), option] for var, option in row_pairs_out]
    aggregate_pairs_out = [[var.lower(), option] for var, option in aggregate_pairs_out]

    # raw_row_pairs_out = str(row_pairs_out)
    # raw_aggregate_pairs_out = str(aggregate_pairs_out)

    return input_file, df_in, row_pairs_out, aggregate_pairs_out, all_default_fields



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


def check_string_elements_for_errors(elements, *, valid_field_pattern="^[A-Za-z0-9 _-]*$", option_list=None):
    """ check if var_string in proper format; raise exception if not.
    Proper format is a list of elements separated by commas, each element either a valid dataframe field name or a
    fielname followed by an option separated by a colon.
    'option' must be in list.

    Args:
        pairs (): string of comma separated fields or 'fields:option' like "field1, field2:mean"

    >>> check_string_elements_for_errors([['var1!']], valid_field_pattern=None)  # special char not checked for
    >>> check_string_elements_for_errors([['var1!']])  # special char not allowed in field name (_-ok)
    Traceback (most recent call last):
    Exception: First item contains other than alphanumeric, underscore or dash
    >>> check_string_elements_for_errors([['var1!']], valid_field_pattern="^[A-Za-z0-9!_-]*$")  # ! added to ok list
    >>> check_string_elements_for_errors([['var1','sumx'], ['var2']], option_list=VALID_AGG_TYPES)
    Traceback (most recent call last):
    Exception: Option not in accepted list
    >>> check_string_elements_for_errors([['var1', 'sum'], ['var2']], option_list=VALID_AGG_TYPES)
    >>> check_string_elements_for_errors([['var1', 'True'], ['var2']], option_list=['True', 'False'])  # booleans are read as str
    >>> check_string_elements_for_errors([['var1', 'True'], ['var2']], option_list=[True, False])  # booleans are read as str
    Traceback (most recent call last):
    Exception: Option not in accepted list
    >>> check_string_elements_for_errors(None, option_list=VALID_AGG_TYPES)  # TODO how should no fields-summary line only be treated
    Traceback (most recent call last):
    TypeError: 'NoneType' object is not iterable
    >>> check_string_elements_for_errors([['999']], option_list=VALID_AGG_TYPES)

    """
    import re
    from loguru import logger

    # Characters allowed in dataframe field names
    # valid_field_pattern = "^[A-Za-z0-9_-]*$"

    # elements = parse_elements(pairs)

    # check elements to make sure they are list of variables or of variable, agg_type
    for element in elements:  #
        # should be string (variable) or pair of string/variable and agg_type
        if len(element) > 2:
            logger.info(f"'{element}' has more than two items.")
            raise Exception("Element has more than two items.")
        if len(element) > 0:
            # if isinstance(element[0], str):  # variable  FIXME check for valid characters using regex
            if valid_field_pattern is not None:
                if bool(re.match(valid_field_pattern, element[0])):  # field contains only
                # alphanumeric, underscore or dash
                   pass
                else:
                    logger.info(f"First item '{element[0]}' contains other than alphanumeric, underscore or dash.")
                    raise Exception("First item contains other than alphanumeric, underscore or dash")
        if len(element) > 1:
            if option_list is not None:
                if element[1] in option_list:  # acceptable option
                    pass
                else:
                    logger.info(f"Second item '{element[1]}' is not a valid option, '{option_list}'.")
                    raise Exception('Option not in accepted list')
        if len(element) <= 0:
            logger.info(f"Length of '{element}' 0 or less.")
            raise Exception("Length of 'element' 0 or less.")


def fill_field_pairs(elements, default_param):
    """ fill the second argument in a field list with optional second parameter

    Args:
        string_elements (): string of comma separated fields or 'fields:option' like "field1, field2:mean"
        default_param (): value to fill blank option item of non-paird elements

    >>> fill_field_pairs([['var1']], 'mean')
    [['var1', 'mean']]
    >>> fill_field_pairs([['var1'], ['var2', 'count']], 'sum')
    [['var1', 'sum'], ['var2', 'count']]
    """

    pairs = []
    # evaled_string_elements = eval(string_elements)
    # elements = check_string_elements_for_errors(string_elements, VALID_AGG_TYPES)

    for element in elements:  # will be string (variable) or pair of string/variable and True/False
        if len(element) == 1:  # variable w no option
            pair = [element[0], default_param]
        else:  # var/option
            pair = element
        pairs.append(pair)

    return pairs


def write_xls_report(df_pt, *, wks_name=None, title1: str = "SUMMARY REPORT", title2="", title3="", title4="", **kwargs):
    """ write and format a df to xls """

    import pandas as pd
    from pathlib import Path
    from bekutils import autosize_xls_cols
    from openpyxl.styles import Font
    from loguru import logger

    if wks_name is None:
        # op_file =op_file
        op_file = Path(__file__).stem
    else:
        op_file = wks_name

    writer = pd.ExcelWriter(op_file + ".xlsx")

    logger.info(f"ready to write to excel")

    df_pt.to_excel(writer, sheet_name="Summary Report", startrow=6)

    logger.info(f"wrote to excel")

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


def groupby_w_totals_check(df_in: pd.DataFrame, row_pairs, aggregate_pairs):
    """ last check on element format, make sure fields are in df,
    Args:
        df_in (): dataframe to summarize.
        row_pairs (): list of fields in df to be grouped-by, lowercase list.
        aggregate_pairs (): list of fields in df to be aggregated.  Specified as pairs of (field,agg).
    """

    from loguru import logger
    from bekutils import setup_loguru
    from bekutils.bek_funcs import exit_yes

    check_string_elements_for_errors(aggregate_pairs, option_list=VALID_AGG_TYPES)

    # make sure all fields are in df_in
    aggregate_fields = [var for var, sum_flag in aggregate_pairs]
    aggregate_fields_not_in_df = set(aggregate_fields) - set(df_in.columns)
    if len(aggregate_fields_not_in_df) != 0:
        exit_yes(f"Aggregate fields {aggregate_fields_not_in_df} are not in file to be summarized.", "MISSING FIELD", )

    check_string_elements_for_errors(row_pairs, option_list=['t', 'f'])

    row_fields = [var for var, sum_flag in row_pairs]
    row_fields_not_in_df = set(row_fields) - set(df_in.columns)
    if len(row_fields_not_in_df) != 0:
        exit_yes(f"Row fields {row_fields_not_in_df} are not in file to be summarized.", "MISSING FIELD", )


def groupby_w_totals(df_in, row_pairs, aggregate_pairs):
    """ pivot with sumtotals"""

    import itertools
    import numpy as np
    import pandas as pd
    from loguru import logger

    logger.info("Just go into groupby_w_totals")
    # vlue to represent totalled lines; must have special char prefix to sort correctly
    TOTAL_STR = '_TOTAL'

    def rename_agg_fields(df, agg_dict):
        """ rename the agg fields with a postfix of the uppercase agg function """
        for field, func in agg_dict.items():
            df = df.rename(columns={field: field + '_' + func.upper()})
        return df

    row_field_dict = {val[0]: val[1] for val in row_pairs}
    row_fields = list(row_field_dict.keys())
    # row_fields_to_aggregate = [field for index, (field, sum_flag) in enumerate(index_pairs) if sum_flag]
    row_fields_to_aggregate = [field for index, (field, sum_flag) in enumerate(row_pairs) if sum_flag.lower() == 't']

    # replace nan with " " to make sorting with _TOTAL correct
    df_in[row_fields] = df_in[row_fields].fillna('')

    # TODO make aggtype part of sumvar pair
    # dictionary of all summed fields field:'sum'
    aggregate_fields_dict = {fld: option for fld, option in aggregate_pairs}

    # create df summed by break of all fields in row_fields
    df_base = df_in.groupby(row_fields, dropna=False).agg(aggregate_fields_dict)

    # Put agg function on end of variable name, eg 'address' becomes 'address_COUNT'
    df_base = rename_agg_fields(df_base, aggregate_fields_dict)

    separate_indexes = list(zip(*df_base.index.values))
    fieldname_to_separate_indexes = dict(zip(row_fields, separate_indexes))
    fieldname_to_index_array_position = {name: idx for idx, name in enumerate(df_base.index.names)}

    # grouped_dfs is a list of df objects, each a summ on a different level
    grouped_dfs = []

    # series1 is grand total for all
    df_grand_total = df_in.groupby(lambda x: True).agg(aggregate_fields_dict)  # lambda is trick to use groupby with
    df_grand_total = rename_agg_fields(df_grand_total, aggregate_fields_dict)

    grouped_dfs.append(df_grand_total)

    logger.info('combinations')
    # in itertools.combinations, second param is the length of the subsequences (eg 2 would produce pairs, 3 triples).
    # creates dataframes summed by combinations of variables
    # Skip summary dfs if len(row_fields_to_aggregate)==0 and don't run final if seq_len == len(row_fields) because that
    # would duplicate base_df
    if True:
        if len(row_fields_to_aggregate) > 0:
            for seq_len in range(1, min(len(row_fields_to_aggregate) + 1, len(row_fields))):
                for temp_aggregate_fields in itertools.combinations(row_fields_to_aggregate, seq_len):
                    # logger.debug(f"{seq_len=},{temp_aggregate_fields=}")
                    # create summed df and add to summed_dfs list
                    # summed_dfs.append(df_base.groupby(level=temp_aggregate_fields).sum())
                    grouped_dfs.append(df_base.groupby(level=temp_aggregate_fields, dropna=False).sum())
    else:
        for fieldname in row_fields_to_aggregate:
            temp_df = df_in.groupby(fieldname, dropna=False).agg(aggregate_dict)
            grouped_dfs.append(temp_df)
            a = 1

    # grouped_dfs.append(df_base.groupby(level=['factory_name'], dropna=False).sum())
    # grouped_dfs.append(df_base.groupby(level=['factory_name', 'team_name'], dropna=False).sum())

    # for every summary df except base, create a multiindex starting with all TOTALs then replacing corresponding
    # columns with index values.
    for df in grouped_dfs:
        # below fills an array to number of index_vars (len(index_vars)) repeating (*) a list filled with the
        # TOTAL_STR, like [['_TOTAL'], ['_TOTAL']], then uses the array to create a multiindex

        # row_fields_to_aggregate = [field for index, (field, total_flag) in enumerate(row_elements) if total_flag]

        # first fill with blanks, then total field columns with TOTAL
        # total_index_array = len(row_fields) * [len(df.index.values) * ['_TOTAL']]
        total_index_array = len(row_fields) * [len(df.index.values) * ['']]
        # for fieldname in row_fields_to_aggregate:
        for fieldname in row_fields:
            index_number_in_index_array = fieldname_to_index_array_position[fieldname]
            total_index_array[index_number_in_index_array] = len(df.index.values) * ['_TOTAL']

        index_obj = df.index.values[0]  # so we can check index type, multi, single field or grand total

        if isinstance(index_obj, (list, tuple)):  # multiindex
            separate_indexes = list(zip(*df.index.values))
            fieldname_to_separate_indexes = dict(zip(df.index.names, separate_indexes))
            for fieldname in df.index.names:
                # replace total row with index vals matched to field name
                index_number_in_index_array = fieldname_to_index_array_position[fieldname]
                total_index_array[index_number_in_index_array] = fieldname_to_separate_indexes[fieldname]
            # df.index = pd.MultiIndex.from_arrays(total_index_array)
        # elif type(df.index.values[0]) == np.int64:  # grand total, single number
        elif type(df.index.values[0]) == np.bool_:  # grand total, single number
            pass  # total_index_array is ok as is - all TOTALs
        elif len(df.index.names) == 1:  # index of one variable, not multiindex
            # replace corresponding column in total_index_array

            # below - df.index.names[0] is solo index field name
            # if df.index.names[0] is None:  # df_grand_total does not have field
            #     index_number_in_index_array = 0
            # else:
            #     index_number_in_index_array = fieldname_to_index_array_position[df.index.names[0]]

            index_number_in_index_array = fieldname_to_index_array_position[df.index.names[0]]
            total_index_array[index_number_in_index_array] = df.index.values
        # else:
        #     logger.error(df.index.values[0], ' is not pair or string or np.int64')
        #     index_array = df.index.values + \
        #                   (len(index_vars) - len(df.index.values[0])) * [[TOTAL_STR]]
        index_tuples = zip(*total_index_array)
        # if len(row_fields) == 1:
        #     total_index_array = ['_TOTAL']
        df.index = pd.MultiIndex.from_arrays(total_index_array)
        a=1

    # concat all dataframes together, sort index
    df_out = df_base
    for df in grouped_dfs:
        df_out = pd.concat([df_out, df])

    df_out.index.names = row_fields
    # level_list = list(range(0, len(row_fields) - 1))

    df_out = df_out.sort_index(key=lambda x: x.str.upper())
    # df_out = df_out.sort_index(level=None, key=lambda x: x.str.upper(), inplace=True)
    logger.debug('df_combine index names', df.index.names)

    logger.info("df created - returning")

    return df_out

def groupby_main( input_file: str = None, df_in: pd.DataFrame = None,
                 raw_row_pairs_in: str = None, raw_aggregate_pairs_in: str = None, default_agg_type: str = 'sum',
                 filter_df: str = None,
                 create_wks: bool = False,
                 title1: str = "SUMMARY REPORT", title2: str = None, title3: str = None,
                 **kwargs):
    """ """

    # INPUT_FILE, df, row_fields, aggregate_fields, all_default_fields = groupby_w_totals_setup(**kwargs)
    INPUT_FILE, df, row_fields, aggregate_fields, all_default_fields = groupby_w_totals_setup(
                input_file=input_file, df_in=df_in,
                raw_row_pairs_in=raw_row_pairs_in, raw_aggregate_pairs_in=raw_aggregate_pairs_in,
                default_agg_type=default_agg_type,
                filter_df=filter_df,
                create_wks=create_wks, title1=kwargs['title1'], title2=title2, title3=title3, )

    # check info created above
    groupby_w_totals_check(df, row_fields, aggregate_fields)

    # create summary df with totals
    df_pt = groupby_w_totals(df, row_fields, aggregate_fields)

    # no row or agg fields were passed to setup so perform default after summ calculations if warranted
    if all_default_fields:
        if 'parent-campaign-address-counts' in str(INPUT_FILE):
            # df_pt['percent assigned to rooms'] = round(100 * df_pt['assigned to organizations_SUM'] /
            #                                            df_pt['total addresses_SUM'], 0)
            # df_pt['percent assigned to writers'] = round(100 * df_pt['assigned to writers_SUM'] /
            #                                              df_pt['total addresses_SUM'], 0)

            # code = compile('for i in range(3): print("Python is cool")',
            #                     'foo.py', 'exec')
            # eval(code)
            #

            code = compile("df_pt['percent assigned to rooms'] = df_pt['assigned to organizations_SUM'] / df_pt['total addresses_SUM']; df_pt['percent assigned to writers'] = df_pt['assigned to writers_SUM'] / df_pt['total addresses_SUM'];", '<string>', 'exec')
            eval(code)
            a=1

    # if kwargs['create_wks']:
    if create_wks:
        # write_xls_report(df_pt, title1= "Summary Report", title3=f"Source data: {INPUT_FILE.name}", **kwargs)
        write_xls_report(df_pt, title3=f"Source data: {INPUT_FILE.name}", **kwargs)

    return df_pt


if __name__ == '__main__':
    # check_string_elements_for_errors("var1*",VALID_AGG_TYPES)  # specified option_list ok
    # check_string_elements_for_errors("var1: True, var2", ['True', 'False'])  # specified option_list ok
    # check_string_elements_for_errors("var1 : sumx", VALID_AGG_TYPES)
    # check_string_elements_for_errors("var1, var2, ", VALID_AGG_TYPES)

    # print(f"{parse_elements(' x')=}")
    # print(f"{parse_elements(' x, y')=}")
    # print(f"{parse_elements('x,  y,  z:  sum')=}")

    raw_row_pairs_in = "factory_name: t, parent_campaign_name: t, org_name"
    raw_row_pairs_in = "factory_name: t, parent_campaign_name: t"
    raw_row_pairs_in = "factory_name: t"

    INPUT_FILE = "/Users/Denise/Downloads/all-parent-campaigns-requests-2024-05-01.csv"
    INPUT_FILE = "/Users/Denise/Downloads/parent-campaign-address-counts-2024-06-17.csv"
    # sincere_data = sincere_data[(sincere_data['Factory'].notna() & ~sincere_data['Name'].str.lower().str.contains("test"))]
    # sincere_data = sincere_data[(~sincere_data['Factory'].str.lower().str.contains("zzz"))]
    #
    # # limit to factories containing factory_must_have_string
    # if factory_must_have_string is not None:
    #     sincere_data = sincere_data[(sincere_data['Factory'].str.lower().str.contains(factory_must_have_string))]
    groupby_main(input_file=INPUT_FILE,
                 filter_df="df_in[(df_in['factory'].notna() "
                           "& ~df_in['name'].str.lower().str.contains('test') "
                           "& ~df_in['name'].str.lower().str.contains('zzz'))]",
                 create_wks=True, title1="TITLE 1 FROM MAIN CALL")
    # groupby_main(input_file=INPUT_FILE, raw_row_pairs_in = raw_row_pairs_in, create_wks=True, wks_name='test')
    # groupby_main(create_wks=True)
    # groupby_w_totals_setup(input_file=INPUT_FILE, raw_row_pairs_in=raw_row_pairs_in)

    a=1
