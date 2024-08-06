import numpy as np
import pandas as pd
import argparse
from pathlib import Path


def generate_field_file(file_prefix, library_df, total_columns, total_rows, num_drops=2, write_files=False):
    '''
    Generate a CSV file for the array print and a CSV file for the pinlist.
    The array print CSV file will contain the plate positions (format: "1A1", "1A2"...) for each sample in the print.
    The pinlist CSV file will contain the print indices (format (1,1), (1,2) ... ) and the sample ID for each sample in the print.
    Inputs:
        file_prefix: Prefix for the output files
        library_df: Dataframe containing the library information
        total_columns: Total columns in the print
        total_rows: Total rows in the print
    Returns:
        print_df: Dataframe containing the plate positions for each sample in the print
        pin_df: Dataframe containing the print indices and sample ID for each sample
        If write_files is True, the function will write the CSV files to the current working directory.
    '''

    #len_library = len(library_members)
    total_wells = (total_columns*total_rows)

    # Calculate number of replicates from total wells
    # NOTE: does not flatten repeat library members in dataframe
    replicates = int(total_wells/len(library_df))
    
    # Create list of the location for each sample by (plate_number, plate_position)
    sample_locations = list(zip(library_df["plate_number"].to_list(), library_df["plate_position"].to_list()))
    # Then, convert to the format scineon expects. Instead of (1, A25), we want 1A25.
    sample_locations = [str(x[0]) + x[1] for x in sample_locations]

    print_array = np.array(sample_locations * replicates)

    # Fill unclaimed wells
    num_remaining_chambers = total_wells - len(print_array)
    remaining_chambers = np.random.choice(sample_locations, num_remaining_chambers)
    
    # Add to print_array
    print_array = np.append(print_array, remaining_chambers)

    # Shuffle order of list
    np.random.shuffle(print_array)

    # Convert list to df with dimensions of print
    print_array = print_array.reshape(total_rows,total_columns)
    print_df = pd.DataFrame(print_array, columns = list(range(total_columns)))

    # Output the array CSV file!
    cwd = Path.cwd()
    array_filename = cwd / (file_prefix + '_array.csv')
    if write_files:
        array_filename.parent.mkdir(parents=True, exist_ok=True)
        print_df.to_csv(array_filename)
    
    ### ADD pinlist generator to output:
    # Indices, MutantID
    # (1,1),   buffer_1
    # (1,2),   1167
    field_dict = {}
    for row in range(len(print_df)):
        for col in range(len(print_df.iloc[0,:])):
            field_dict[(col+1, row+1)] = print_df.iloc[row,col]
    pin_dicts = []
    for idx, source_well in field_dict.items():
        plate_position = source_well[1:]
        plate_number = source_well[0]
        #print(plate_position, plate_number)
        mutant_ID = library_df[(library_df["plate_position"] == plate_position) & (library_df["plate_number"] == int(plate_number))]["member_name"].item()
        #print(mutant_ID)
        pin_dicts.append({"Indices": idx,
        "MutantID": mutant_ID})
    pin_df = pd.DataFrame(pin_dicts)
    
    # Output the pinlist CSV file!
    if write_files:
        pin_filename = cwd / (file_prefix + '_pinlist.csv')
        pin_df.to_csv(pin_filename, index=False)

    # Create field file:
    if write_files:
        field_filename = cwd / (file_prefix + '_fld.txt')
        with open(field_filename, 'w') as f:
            for i in range(0, total_rows):
                for j in range(0, total_columns):
                    current_fld_loc = str(i + 1) + '/' + str(j + 1) # add ones to change from 0-indexing
                    current_array_val = print_df.iloc[i][j]

                    # Insert blank for NaN values
                    if type(current_array_val) != str:
                        current_array_val = '\t'

                    array_loc_print = current_array_val
                    f.write(current_fld_loc + '\t' + array_loc_print + ',' + '\t' + str(num_drops) + ',' + '\n')

    return print_df, pin_df

def split_multi_plate_field_file(field_file_name, num_plates):
    '''
    Split a multi-plate field file into individual field files for each plate.
    Inputs:
        field_file_name: Name of the multi-plate field file
        num_plates: Number of plates in the field file
    Returns:
        None
        Outputs individual field files for each plate.
    '''
    output_field_file_prefix = Path(field_file_name).stem
    for i in range(num_plates):
        with open(field_file_name, 'r') as f, open(output_field_file_prefix + '_plate' + str(i+1) + '.txt', 'w') as f_out:
            field_file_lines = f.readlines()
            for line in field_file_lines:
                split_line = line.split('\t')
                plate_num = int(split_line[1][0])-1 # 0-indexed

                if plate_num == i:
                    #adjust the line so the plate number is always 1:
                    split_line[1] = '1' + split_line[1][1:]
                    new_line = '\t'.join(split_line)
                    f_out.write(new_line)
                else:
                    #otherwise, write a blank line
                    f_out.write(split_line[0] + '\t' + '\t' + '\n')

if __name__ == '__main__':
    ### Parse arguments ###
    parser = argparse.ArgumentParser()
    parser.add_argument("library_csv", help="Path to the library CSV file")
    parser.add_argument("output_file_prefix", help="Prefix for the output files")
    parser.add_argument("--total_columns", help="Total columns in the print", default=32)
    parser.add_argument("--total_rows", help="Total rows in the print", default=56)
    parser.add_argument("--number_of_drops", help="Number of drops per well", default=2)
    parser.add_argument("--num_field_files_to_split", help="If you want to split the field file over multiple plates, specify the number of plates", default=1)
    
    args = parser.parse_args()

    ### Rename some arguments for clarity ###
    library_csv = args.library_csv
    output_file_prefix = args.output_file_prefix
    total_columns = int(args.total_columns)
    total_rows = int(args.total_rows)
    num_drops = int(args.number_of_drops)
    num_plates = int(args.num_field_files_to_split)

    ### Pass arguments to function to write out "field file" and "pinlist" ###
    library_df = pd.read_csv(library_csv)
    print_df, pin_df = generate_field_file(output_file_prefix, library_df, total_columns, total_rows, num_drops=num_drops, write_files=True)

    if num_plates > 1:
        split_multi_plate_field_file(output_file_prefix + '_fld.txt', num_plates) #split the field file into individual plates