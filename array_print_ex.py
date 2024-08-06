### ARGUMENTS ###
library_csv = "data/20240718_mpro_print.csv"
output_file_prefix = "output/1/output_file_1"
num_plates = 2

### Create Pandas array ###
import pandas as pd
library_df = pd.read_csv(library_csv)

### Create the output files ###
from array_print_pro import generate_field_file, split_multi_plate_field_file
generate_field_file(output_file_prefix, library_df, 32, 56, write_files=True)

### If you want to use multiple input plates on the scieneon, split the field file into individual plates ###
if num_plates > 1:
    split_multi_plate_field_file(output_file_prefix + '_fld.txt', num_plates) #split the field file into individual plates