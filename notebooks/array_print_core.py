
import os
from unittest import skip

import numpy as np
import pandas as pd
import datetime
from random import shuffle
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# 
def csv_to_df(library_csv):
    csv_filepath = library_csv._selected_path + '/' + library_csv._selected_filename
    library_df = pd.read_csv(csv_filepath)
    column_names = list(library_df.columns)
    display(library_df)
    library_members = library_df['plate_position'].to_list()

    return library_df, column_names, library_members

def count_replicates(library_df, total_columns, total_rows, empty_columns, skip_rows):
    # calculate available positions on chip
    library_members = set(library_df['plate_position'])
    library_size = len(library_members)
    empty_rows = total_rows/2
    columns = total_columns - empty_columns
    rows = total_rows
    replicates = int((rows * columns)/(library_size))

    if skip_rows == 'n':
        print('Library contains', library_size, 'members. Will array', int(replicates), 'replicates per library member.')
    else:
        print('Library contains', library_size, 'members. Accounting for skipped rows, the script will array', int(replicates/2), 'replicates per library member.')

    return library_members, library_size, empty_rows, columns, rows, replicates

def generate_array(filename, library_df, total_columns, total_rows, skip_rows, column_names):

    total_wells = (total_columns*total_rows)

    # Calculate number of replicates from total wells
    # NOTE: does not flatten repeat library members in dataframe
    ideal_replicates = int(total_wells/len(library_df))

    plate_number = column_names[0]
    plate_position = column_names[1]

    zipped_list = zip(library_df[plate_number].to_list(), library_df[plate_position].to_list())
    muts_list = [str(x[0]) + x[1] for x in zipped_list]

    full_list = muts_list * ideal_replicates

    # Fill unclaimed wells
    remaining_chambers = total_wells - len(full_list)

    for i in range(int(remaining_chambers)):
        full_list.append(np.random.choice(muts_list))

    # Shuffle order of list
    shuffle(full_list)

    # Convert list to df with dimensions of print
    print_array = np.array(full_list)
    print_array = print_array.reshape(total_rows,total_columns)
    print_df = pd.DataFrame(print_array, columns = list(range(total_columns)))

    # Insert NA for skips
    if skip_rows == 'y':
        print_df.iloc[1::2] = np.nan

    print(print_df)
    
    # Sum library member counts
    counts = print_df.apply(pd.value_counts, dropna=True)
    counts['Replicate counts'] = counts.sum(axis=1)
    # counts = counts['Replicate counts']
    if skip_rows == 'y':
        counts['Blank wells'] = counts[np.nan]
        counts = counts.drop(labels = [np.nan])
    
    print('Library counts:')
    # display(counts.sort_values())
    
    # Save array
    cwd = os.getcwd()
    project_path = cwd + '/' + filename
    try:
        os.mkdir(project_path)
    except OSError as error: 
        print(error)

    time = datetime.datetime.now()
    time = "_" + str(time).replace(" ", "_")
    
    pd.DataFrame(print_df).to_csv(project_path + '/' + filename + '_array' + time + '.csv')

    # # plot slide
    # im = plt.imshow(print_array)
    # library_mems = library_df['plate_position'].to_list()
    # library_indexed = dict(zip(library_mems, range(len(library_mems))))

    # values = list(library_indexed.values())
    # colors = [ im.cmap(im.norm(value)) for value in values ]
    # patches = [ mpatches.Patch(color = colors[i], label = "{l}".format(l = list(init_member_idx.keys())[i])) for i in range(len(values)) ]

    # # plot array and print
    # plt.legend(handles = patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=1)
    # plt.tight_layout()
    # plt.savefig("%s.png" % filename, dpi = 300, transparent = False)
    # plt.show()

    # ax = counts.plot.bar(x='Library Member', y='Replicates')
    # plt.xlabel('Library Member')
    # plt.ylabel('Replicates')
    # plt.tight_layout()
    # plt.show()

    # fig, ax = plt.subplots(nrows=2, ncols=2)

    # for row in ax:
    #     for col in row:
    #         counts.plot.bar(x='Library Member', y='Replicates')
    #         # col.xlabel('Library Member')
    #         # col.ylabel('Replicates')
    #         # col.tight_layout()
    #         # col.show()

    return print_df, project_path

def display_fld(print_df, total_columns, total_rows):
    for i in range(0, total_rows):
        for j in range(0, total_columns):
            current_fld_loc = str(i + 1) + '/' + str(j + 1) # add ones to change from 0-indexing
            current_array_val = print_df.iloc[i][j]

            # Insert blank for NaN values
            if type(current_array_val) != str:
                current_array_val = '\t'

            array_loc_print = current_array_val
            print(current_fld_loc + '\t' + array_loc_print + ',' + '\t' + '1,')

def write_fld(project_path, filename, print_df, total_columns, total_rows):
    time = datetime.datetime.now()
    time = "_" + str(time).replace(" ", "_")

    with open(project_path + '/' + filename + '_fld' + time + '.txt', 'w') as f:
        for i in range(0, total_rows):
            for j in range(0, total_columns):
                current_fld_loc = str(i + 1) + '/' + str(j + 1) # add ones to change from 0-indexing
                current_array_val = print_df.iloc[i][j]

                # Insert blank for NaN values
                if type(current_array_val) != str:
                    current_array_val = '\t'

                array_loc_print = current_array_val
                f.write(current_fld_loc + '\t' + array_loc_print + ',' + '\t' + '1,' + '\n')