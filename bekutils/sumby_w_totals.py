"""
Use sumBy but with subtotals sorted into output df.
Runs on report file from Sincere, prompted to input.
Now with git, generic name that replaces those with version numbers.
"""

# V2 play with total in multiindex
# V2.1 clean up commented lines; test replacing multiindex columns by position
# V3 specify fields to have total lines
# Started as V3

# TODO Is all the code below the if __file__ ok?  Especially the imports?  Is this how testing works?

# format of INDEX_VARS_W_SUMFLAG is list of tuples: (variable name, whether to subtotal)
# Order of variables is order/level of subtotaling

def sumby_w_totals(df_in, index_vars_w_sumflag, summed_fields, agg_type):
    """ pivot with sumtotals"""

    import itertools
    import numpy as np
    import pandas as pd
    from loguru import logger

    logger.info("Just go into sumby_w_totals")
    # vlue to represent totalled lines; must have special char prefix to sort correctly
    TOTAL_STR = '_TOTAL'

    # index_vars_w_sumflag = [('Parent Campaign', True), 'Child Organization', ('Name', True)]
    # index_vars_w_sumflag = [('Factory', False), ('Name', True)]
    # index_vars_w_sumflag = [('Factory', False), 'Name']
    # reformat original index field list replacing non-secified sum field with default of 'False'
    index_vars_w_sumflag_formatted = [list_obj if isinstance(list_obj, tuple) else (list_obj, False)
                             for list_obj in index_vars_w_sumflag]
    index_var_dict = {val[0]: val[1] for val in index_vars_w_sumflag_formatted}
    index_vars = list(index_var_dict.keys())
    # index_vars_to_sum = [tuple[0] for index, tuple in enumerate(index_vars_w_sumflag_formatted) if tuple[1]]
    index_vars_to_sum = [field for index, (field, sum_flag) in enumerate(index_vars_w_sumflag_formatted) if sum_flag]
    # sum_cols = [index for index, tuple in enumerate(index_vars_w_sumflag_formatted) if tuple[1]]
    # index_vars = ['Break_1', 'Factory', 'Name']

    # replace nan with " " to make sorting with _TOTAL correct
    df_in[index_vars] = df_in[index_vars]. fillna('')

    # TODO make aggtype part of sumvar tuple
    # dictionary of all summed fields field:'sum'
    summed_fields_dict = {fld: agg_type for fld in summed_fields}

    # create df summed by break of all fields in index_vars
    df_base = df_in.groupby(index_vars, dropna=False).agg(summed_fields_dict)
    a=1

    # df_base = df_combine.groupby(index_vars).agg({'Total Addresses':sum, 'Available Addresses':sum,
    #                                'Assigned to Organizations':sum, 'Assigned to Writers':sum})

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
            # The steps of forming the index are:
            #   1. create index_array, a list of lists (number of rows wide) by (# vars high) with index being
            #   column of variable, long filled with "_TOTAL" (var TOTAL_STR) like
            #       index 0 = [_TOTAL,_TOTAL,_TOTAL,_TOTAL,]
            #       index 1 = [_TOTAL,_TOTAL,_TOTAL,_TOTAL,]
            #   2. split df.index.values into a list of lists (actually tuples) where each list is the values down
            #   the rows. df.index.values is an array(list) of tuples, each tuple the index for the row, tuples being
            #   variable value combinations.  so df.index.values=[('a','1'),('b','1'),('c','2')] =>
            #   separate_indexes becomes [('a','b','c'),('1','1','2')]
            #   3. create a dictionary of filename to separate index
            #   4. replace the corresponding rows in the array with the index values
            #   5. create a multiindex for the df from the index array were row arrays become elements of index tuples
            index_array = len(index_vars) * [len(df.index.values) * [TOTAL_STR]]
            # below is a neat trick: list(zip(*summed_dfs[2].index.values)) unzips and produces a list of lists (actually
            # tuples), each the n position in all tuples of index.
            # https://stackoverflow.com/questions/12974474/how-to-unzip-a-list-of-tuples-into-individual-lists
            separate_indexes = list(zip(*df.index.values))

            # tuples of col name and list of index values
            # field_w_separate_indexes = list(zip(df.index.names, separate_indexes))

            # field_to_separate_indexes_dict = {field_and_index[0]: field_and_index[1] for field_and_index in field_w_separate_indexes}
            # dictionary = dict(zip(keys, values))
            field_to_separate_indexes_dict = dict(zip(index_vars, separate_indexes))

            for column_field in df.index.names:
                # below loops though to get index number in multiindex of field
                # index_in_multiindex = [index_vars_w_sumflag[0] for index_vars_w_sumflag in index_vars_w_sumflag_formatted].index(column_field)
                index_in_multiindex = index_vars.index(column_field)
                index_array[index_in_multiindex] = field_to_separate_indexes_dict[column_field]
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
            logger.error(df.index.values[0], ' is not tuple or string or np.int64')
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


if __name__ == '__main__':

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

    # get an input file
    if True:
        input_file = get_file_name("Pick File", "Pick a parent-campaign file to summarize (eg "
                                   "'parent-campaign-address-counts-2023-08-03.csv'",
                                   "~/Downloads/")
    else:
        input_file = "/Users/Denise/Downloads/parent-campaign-address-counts-2023-08-03.csv"
        # input_file = "/Users/Denise/Downloads/all-users-2024-01-06.csv"

    if False:
        if 'parent-campaign-address-counts' not in input_file:
            exit_yes("File must have 'parent-campaign-address-counts' in the name", "WRONG FILE TYPE")

    sincere_data = pd.read_csv(input_file)

    # FOR TESTING select only certain records
    # sincere_data = sincere_data.loc[sincere_data['Factory'] == "VA General BIPOC 7-2023"]
    # sincere_data = sincere_data[~sincere_data['Name'].str.lower().str.contains("test")]
    # sincere_data = sincere_data[sincere_data['organization'].str.lower().isin(["fl - entire state", "general",
    #                                                                            "national-bob haar"])]

    # sincere_data = sincere_data[~sincere_data['name'].str.lower().str.contains("test")]

    sincere_data['Remaining In Room'] = sincere_data['Assigned to Organizations'] - sincere_data[
        'Assigned to Writers']

    # fields to sum by. second parm is whether to total or not.
    index_vars_w_sumflag = [('Factory', True), ('Name', True), ]
    # index_vars_w_sumflag = [('organization', True), ('team', True),]

    # list of fields to sum/count
    sum_fields = ['Total Addresses', 'Available Addresses', 'Assigned to Organizations', 'Assigned to Writers',
                  'Remaining In Room']
    # sum_fields = ['email']
    df_pt = sumby_w_totals(sincere_data, index_vars_w_sumflag, sum_fields, 'sum')

    # op_file =op_file
    op_file = Path(__file__).stem
    writer = pd.ExcelWriter(op_file + ".xlsx")

    df_pt.to_excel(writer, sheet_name="Summary Report", startrow=6)
    wb = writer.book
    for sh in wb.worksheets:
        autosize_xls_cols(sh)

    for sh in wb.worksheets:
        sh['A1'].value = "Summary Report"
        sh['A1'].font = Font(b=True, size=20)
        sh['A3'].value = "Source data: " + input_file
        sh['A3'].font = Font(size=12)

    writer.close()

    a = 1
