import camelot
import cv2
import pandas as pd
import os
from pathlib import Path
import file_process



almaty = pd.DataFrame([], columns=['consumption', 'temperature', 'humidity'], index=[])
parent_path = Path(os.path.abspath(__file__)).parents[1]
data_path = 'dataset\consumption_data'
directory = os.path.join(parent_path, data_path)


def after_parse_edit(full_path):
    file_process.del_early_report(full_path)
    file_process.rename_file(full_path)
    file_process.extract_zip(full_path)
    file_process.doc_to_pdf(full_path)

after_parse_edit(directory)


for file in os.listdir(directory):
        if file.endswith(".pdf"):
            try:
                filepath = os.path.join(directory, file)
                filename = os.path.split(filepath)[-1][:-4]
                if not almaty.index.isin([filename]).any():
                    tables = camelot.read_pdf(filepath, pages='2-4', flavor='lattice')
                    df = pd.concat([table.df for table in tables], ignore_index=True)
                    df.set_index(df.columns[0], inplace=True)
                    almaty_row = df.loc[df.index.str.contains('Алматинская', case=False)]
                    if almaty_row.shape[1] == 8:
                        value = almaty_row.iloc[0, 4]
                    elif almaty_row.shape[1] == 6:
                        value = almaty_row.iloc[0, 3]
                    almaty.loc[filename, 'consumption'] = value
                    if '2012' in filename:
                        if almaty_row.shape[1] == 8:
                            value = almaty_row.iloc[0, 5]
                        elif almaty_row.shape[1] == 6:
                            value = almaty_row.iloc[0, 4]
                        almaty.loc["2011" + filename[4:], 'consumption'] = value
            except Exception as e:
                 print(file, e)

almaty.sort_index(inplace=True)

directory_path = Path(directory).parents[0]
filename = 'dataset.csv'
save_path = directory_path / filename

almaty.to_csv(save_path, sep='\t', encoding='utf-8')