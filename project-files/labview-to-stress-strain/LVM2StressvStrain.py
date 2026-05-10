import pandas as pd
import os
import csv
import numpy as np

def convert_lvm_to_csv(lvm_file, csv_file):
    with open(lvm_file, 'r') as lvm:
        lines = lvm.readlines()

    # Find where the data starts, skipping header
    data_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "":  # Adjust according to actual file structure
            data_start = i + 1
            break
    
    data_lines = lines[data_start:]

    # Write the data to a CSV file
    with open(csv_file, 'w', newline='') as csv_out:
        writer = csv.writer(csv_out)
        for line in data_lines:
            # Assume tab-delimited data, you can modify this if it's different
            row = line.strip().split('\t')
            writer.writerow(row)

    #print(f"Conversion complete. {csv_file} saved.")

def get_file_paths(folder_path):
    file_paths = []
    
    # Walk through directory
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.lvm'):  # Filter files with .lvm extension
                # Get the full file path and add to list
                file_paths.append(os.path.join(root, file))
    
    return file_paths

def find_strain(length_i, length_D):
    if length_i == 0:
        return float(0)  # or return 0 or some other appropriate value
    return (length_D) / length_i

def find_stress(Area, Force):
    if Area == 0:
        return float(0)
    return (Force/Area)

def delete_first_9_rows(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Skip the first 9 rows
        for _ in range(9):
            next(reader, None)
        
        # Write the remaining rows to the output file
        for row in reader:
            writer.writerow(row)

def round_to_nearest(value):
    return round(value / 0.005) * 0.005

def StressvStrainCare(df, Strain, Stress):
    # Assuming the columns are named 'Strain' and 'Stress'. Adjust as needed.
    strain_column = Strain  # Replace with the actual strain column name
    stress_column = Stress  # Replace with the actual stress column name

# Group by strain and calculate the mean stress for each unique strain value
    grouped_df = df.groupby(strain_column, as_index=False)[stress_column].mean()

# Add the new strain and average stress columns to the original dataframe
    if 'ext' in Strain:
        df[f'Unique {Strain}'] = grouped_df[strain_column]
        df[f'Average ext {Stress}'] = grouped_df[stress_column]
    else:
        df[f'Unique {Strain}'] = grouped_df[strain_column]
        df[f'Average {Stress}'] = grouped_df[stress_column]
    return df

folder_path = '/Users/hoodieb/Desktop/Data_Test'  # Replace with your folder path
files_list = get_file_paths(folder_path)
#print(files_list)
csv_file_list = []
iter = 1
df = pd.read_excel('/Users/hoodieb/Desktop/MECH331B_Corrosion_Lab_Group_4_Data.xlsx')
#print(df.head)
len_list = df['Length (mm)']
area_list = df['Area (mm^2)']
name_list = ['PG1_','PG2_']
print('Variables set')

for i in files_list:
    csv_file_path = f'{i[0:-4]}.csv'
    convert_lvm_to_csv(i, csv_file_path)
    csv_file_path2 = f'{csv_file_path[0:-4]}update.csv'
    delete_first_9_rows(csv_file_path,csv_file_path2)
#headers = ['X_Value', 'Extensometer Displacement-mm (Mean)', 'Force-N (Mean)', 'Global Displacement-mm (Mean)', 'Comment', 'Strain Unrounded', 'Strain Rounded', 
#          'Strain ext Unrounded', 'Strain ext Rounded', 'Stress (MPa)', 'Unique Strain ext Rounded',  'Average ext Stress (MPa)', 'Unique Strain Rounded', 'Average Stress (MPa)']

headers = ['Unique Strain ext Rounded',  'Average ext Stress (MPa)', 'Unique Strain Rounded', 'Average Stress (MPa)']
print('lvm to csv done')
with pd.ExcelWriter('/Users/hoodieb/Desktop/DATA_TEST/MECH331_Corrosion.xlsx', engine='openpyxl', mode='w') as writer:
    for init_i in range(0,len(len_list)):
        for n_list in name_list:
            for ii in range(0,25,5):
                # Create the blank DataFrame
                #blank_df = pd.DataFrame(columns=headers)
                #data = [[0] * len(headers)]  # Create a list of zeros with the same length as headers
                #blank_df = pd.DataFrame(data, columns=headers)
                for iii in range(1,6):
                    string4Now = f'/Users/hoodieb/Desktop/DATA_TEST/{ii}{n_list}{iii}update.csv'
                    #print(f'/Users/hoodieb/Desktop/DATA_TEST/{ii}{n_list}{iii}.lvm')
                    if f'/Users/hoodieb/Desktop/Data_Test/{ii}{n_list}{iii}.lvm' in files_list:
                        #print('working')
                        temp_df = pd.read_csv(string4Now)
                        #print(len(temp_df))
                        #print(temp_df.head)
                        glob_disp = temp_df['Global Displacement-mm (Mean)']
                        ext_disp = temp_df['Extensometer Displacement-mm (Mean)']
                        force_df = temp_df['Force-N (Mean)']
                        temp_df['Strain Unrounded'] = np.nan
                        temp_df['Strain Rounded'] = np.nan
                        temp_df['Strain ext Unrounded'] = np.nan
                        temp_df['Strain ext Rounded'] = np.nan
                        temp_df['Stress (MPa)'] = np.nan
                        for iiii in range(0,len(temp_df)):
                            #print(len_list[init_i],glob_disp[iiii],area_list[init_i],force_df[iiii],ext_disp[iiii])
                            a = find_strain(len_list[init_i],glob_disp[iiii])
                            b = round_to_nearest(a)
                            c = find_strain(len_list[init_i],ext_disp[iiii])
                            d = round_to_nearest(c)
                            e = find_stress(area_list[init_i],force_df[iiii])
                            temp_df.at[iiii, 'Strain Unrounded'] = a
                            temp_df.at[iiii, 'Strain Rounded'] = b
                            temp_df.at[iiii, 'Strain ext Unrounded'] = c
                            temp_df.at[iiii, 'Strain ext Rounded'] = d
                            temp_df.at[iiii, 'Stress (MPa)'] = e
                            #print(temp_df.head)
                        temp_df = StressvStrainCare(temp_df, 'Strain ext Rounded', 'Stress (MPa)')
                        temp_df = StressvStrainCare(temp_df, 'Strain Rounded', 'Stress (MPa)')
                        #print(temp_df.head)
                        #break
                    else: 
                        continue
                    temp_df.to_excel(writer, sheet_name=f'{ii}{n_list}{iii}', index=False)
                    #break
                temp_df_sub = temp_df[headers]
                temp_df.fillna(0, inplace=True)
                #blank_df = pd.concat([blank_df, temp_df_sub], ignore_index=True)
            
            #if n_list == 'PG2_' and ii in [0,5,15] or n_list == 'PG1_':
                #if not blank_df.empty:
                #blank_df.to_excel(writer2, sheet_name=f'{ii}{n_list}_All', index=False)
            #break
        #break
        #print(iter)
        #iter += 1

print('done')

file_path = '/Users/hoodieb/Desktop/DATA_TEST/MECH331_Corrosion.xlsx'
blank_df = pd.DataFrame(columns=headers)
data = [[0] * len(headers)]  # Create a list of zeros with the same length as headers
blank_df = pd.DataFrame(data, columns=headers)
with pd.ExcelWriter('/Users/hoodieb/Desktop/DATA_TEST/MECH331_Corrosion_Cumulative.xlsx', engine='openpyxl', mode='w') as writer:
    for init_i in range(0,len(len_list)):
            for n_list in name_list:
                for ii in range(0,25,5):
                    for iii in range(1,6):
                        sheet_name = f'{ii}{n_list}{iii}'
                        data_df = pd.read_excel(file_path, sheet_name=sheet_name)
                        data_df_sub = data_df[headers]
                        data_df_sub.fillna(0, inplace = True)
                        blank_df = pd.concat([blank_df, data_df_sub], ignore_index = True)
                    if n_list == 'PG2_' and ii in [0,5,15] or n_list == 'PG1_':
                    #if not blank_df.empty:
                        blank_df.to_excel(writer, sheet_name=f'{ii}{n_list}_All', index=False)

