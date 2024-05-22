""" test how multiindex work with appending dataframes.  names option for levels """

import pandas as pd
import numpy as np
from pathlib import Path
import itertools
from bekutils import autosize_xls_cols

def rename_agg_fields(df, agg_dict):
    """ rename the agg fields with a postfix of the uppercase agg function """
    for field, func in agg_dict.items():
        df = df.rename(columns={field: field + '_' + func.upper()})
    return df


INPUT_FILE = "/Users/Denise/Downloads/all-parent-campaigns-requests-2024-05-01.csv"

df_in = pd.read_csv(INPUT_FILE)
# df_in = df_in.loc[(df_in['parent_campaign_name'] == 'VA-Albemarle-Primary 1-2024 **mail April 26 to June 3**')]
df_in = df_in.loc[(df_in['factory_name'] == 'GA Primary 1-2024') | (df_in['factory_name'] == 'VA Primary 1-2024')]

row_elements = [ ('org_name', True), ('factory_name', True), ('parent_campaign_name', False),
                ('team_name', False)]
row_fieldnames = [pair[0] for pair in row_elements]
row_fieldnames_totaled = [field for index, (field, total_flag) in enumerate(row_elements) if total_flag]

df_in[row_fieldnames] = df_in[row_fieldnames].fillna('')  # vars like Team have blanks which show as nan

# TODO allow more than one function to be performed on a variable.  Field name gets overwritten by last so only one
#  shows.
aggregate_elements = [('addresses_count', 'sum'), ('org_id', 'count'),]
aggregate_dict = dict(aggregate_elements)
# aggregate_func = [(field =(field, func)) for field, func in aggregate_elements]

# agg_func = [addresses_count_SUM=('addresses_count', 'sum'), org_id_COUNT=('org_id', 'count')]
# .agg(new_col_name=('col_name', 'agg_func')

df_base = df_in.groupby(row_fieldnames, dropna=False).agg(aggregate_dict)
# df_base = df_in.groupby(row_fieldnames, dropna=False).agg(addresses_count_SUM=('addresses_count', 'sum'),
#                                                           org_id_COUNT=('org_id', 'count'))
# df_base = df_in.groupby(row_fieldnames, dropna=False).agg(agg_func)

df_base = rename_agg_fields(df_base, aggregate_dict)

# for field, func in aggregate_dict.items():
#     df_base = df_base.rename(columns={field: field + '_' + func.upper()})

separate_indexes = list(zip(*df_base.index.values))
fieldname_to_separate_indexes = dict(zip(row_fieldnames, separate_indexes))
fieldname_to_index_array_position = {name: idx  for idx, name in enumerate(df_base.index.names)}

grouped_dfs = []

# series1 = df_base.sum()
df_grand_total = df_in.groupby(lambda x: True).agg(aggregate_dict)  # lambda is trick to use groupby with no index var
df_grand_total = rename_agg_fields(df_grand_total, aggregate_dict)

df_base = rename_agg_fields(df_base, aggregate_dict)

# for field, func in aggregate_dict.items():
#     df_grand_total = df_grand_total.rename(columns={field: field + '_' + func.upper()})
# series2 = df_base.count()
# grouped_dfs.append(series1.to_frame().transpose())
grouped_dfs.append(df_grand_total)

# in itertools.combinations, second param is the length of the subsequences (eg 2 would produce pairs, 3 triples).
# creates dataframes summed by combinations of variables
# Skip summary dfs if len(index_vars_to_sum)==0 and don't run final if seq_len == len(index_vars) because that
# would duplicate base_df
if True:
    if len(row_fieldnames_totaled) > 0:
        for seq_len in range(1, min(len(row_fieldnames_totaled) + 1, len(row_fieldnames))):
            for temp_sum_vars in itertools.combinations(row_fieldnames_totaled, seq_len):
                # logger.debug(f"{seq_len=},{temp_sum_vars=}")
                # create summed df and add to summed_dfs list
                # summed_dfs.append(df_base.groupby(level=temp_sum_vars).sum())
                grouped_dfs.append(df_base.groupby(level=temp_sum_vars, dropna=False).sum())
else:
    for fieldname in row_fieldnames_totaled:
        temp_df = df_in.groupby(fieldname, dropna=False).agg(aggregate_dict)
        grouped_dfs.append(temp_df)
        a=1

# grouped_dfs.append(df_base.groupby(level=['factory_name'], dropna=False).sum())
# grouped_dfs.append(df_base.groupby(level=['factory_name', 'team_name'], dropna=False).sum())

# for every summary df except base, create a multiindex starting with all TOTALs then replacing corresponding
# columns with index values.
for df in grouped_dfs:
    # below fills an array to number of index_vars (len(index_vars)) repeating (*) a list filled with the
    # TOTAL_STR, like [['_TOTAL'], ['_TOTAL']], then uses the array to create a multiindex

    # row_fieldnames_totaled = [field for index, (field, total_flag) in enumerate(row_elements) if total_flag]

    # first fill with blanks, then total field columns with TOTAL
    total_index_array = len(row_fieldnames) * [len(df.index.values) * ['_TOTAL']]
    total_index_array = len(row_fieldnames) * [len(df.index.values) * ['']]
    # for fieldname in row_fieldnames_totaled:
    for fieldname in row_fieldnames:
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
        index_number_in_index_array = fieldname_to_index_array_position[df.index.names[0]]
        total_index_array[index_number_in_index_array] = df.index.values
    # else:
    #     logger.error(df.index.values[0], ' is not pair or string or np.int64')
    #     index_array = df.index.values + \
    #                   (len(index_vars) - len(df.index.values[0])) * [[TOTAL_STR]]
    df.index = pd.MultiIndex.from_arrays(total_index_array)

a=1

df_out = df_base
for df in grouped_dfs:
    df_out = pd.concat([df_out, df])

df_out.index.names = row_fieldnames
# level_list = list(range(0, len(index_vars) - 1))

df_out = df_out.sort_index(key=lambda x: x.str.upper())

op_file = Path(__file__).stem
writer = pd.ExcelWriter(op_file + ".xlsx")
df_out.to_excel(writer, sheet_name="Summary Report", startrow=6)
wb = writer.book
ws = writer.sheets["Summary Report"]
autosize_xls_cols(ws)
writer.close()

a=1
