import os
import pandas as pd

def summarize_data(directory):

    complete_df = []

    all_roots = []
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            if 'dataframe.csv' in file:
                temp_df = pd.read_csv(os.path.join(root, file))

                cell_number = file.split('_')[1]
                temp_df['cell_number'] = f"cell_{cell_number}"
                complete_df.append(temp_df)

    final_df = pd.concat(complete_df)

    final_df.to_csv(directory + '/01_final_df.csv')
