import pandas as pd
import numpy as np
import os
from kaggle.api.kaggle_api_extended import KaggleApi
import sqlite3
import zipfile
import shutil


class DataProcessing:
    def __init__(self):
        self.kaggle = KaggleApi()
        self.kaggle.authenticate()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.abspath(os.path.join(current_dir, os.pardir))
        self.data_path = os.path.join(base_path, 'data')
        database_name = 'Data.sqlite'
        self.db_path = os.path.join(self.data_path, database_name)

    def extract_files(self, base_path, file_name):
        with zipfile.ZipFile(f"{base_path}/{file_name}.zip", 'r') as zip_ref:
            zip_ref.extractall(f"{base_path}/temp")

    def rename_files(self, old_file_name, new_file_name):
        os.rename(old_file_name, new_file_name)

    def move_files(self, old_file_loc, new_file_loc):
        shutil.move(old_file_loc, new_file_loc)

    def remove_dir(self, dir_path):
        os.rmdir(dir_path)

    def delete_file(self, file_path):
        os.remove(file_path)

    def unemployement_data_transform(self,new_dataset_name):
        data = pd.read_csv(fr"{self.data_path}/{new_dataset_name}")
        data = data.dropna()
        unemployment_data = data.copy(deep=True)
        unemployment_data.rename(columns={'date':'Date'}, inplace=True)
        unemployment_data["Date"] = pd.to_datetime(unemployment_data["Date"]).dt.date
        conn = sqlite3.connect(self.db_path)
        unemployment_data.to_sql('unemployement_data', conn, index=False, if_exists='replace')

    def crime_data_transform(self,new_dataset_name):
        data = pd.read_csv(fr"{self.data_path}/{new_dataset_name}")
        data = data.dropna()
        cols_to_keep = ['Date Rptd', 'DATE OCC', 'AREA NAME', 'Part 1-2', 'Crm Cd Desc', 'Vict Age', 'Vict Sex',
                        'Premis Desc', 'Weapon Desc', 'LOCATION']
        crime_data = data[cols_to_keep].copy(deep=True)

        crime_data["Date Rptd"] = pd.to_datetime(crime_data["Date Rptd"]).dt.date
        crime_data["DATE OCC"] = pd.to_datetime(crime_data["DATE OCC"]).dt.date

        conn = sqlite3.connect(self.db_path)
        crime_data.to_sql('crime_data', conn, index=False, if_exists='replace')

    def get_data_from_kaggle(self, file_name, new_name, kaggle_file_path):
        file_name = file_name
        new_dataset_name = new_name
        if not os.path.exists(fr"{self.data_path}/{new_dataset_name}"):
            self.kaggle.dataset_download_file(dataset=kaggle_file_path, file_name=file_name, path=self.data_path)
            if file_name == "Crime_Data_from_2020_to_Present.csv":
                self.extract_files(fr"{self.data_path}", file_name)
                self.move_files(fr"{self.data_path}/temp/{file_name}", fr"{self.data_path}")
                self.remove_dir(fr"{self.data_path}/temp")
                self.delete_file(fr"{self.data_path}/{file_name}.zip")
            self.rename_files(fr"{self.data_path}/{file_name}", fr"{self.data_path}/{new_dataset_name}")

            if file_name == "Crime_Data_from_2020_to_Present.csv":
                self.crime_data_transform(new_dataset_name)

            elif file_name == "unemployed_population_1978-12_to_2023-07.csv":
                self.unemployement_data_transform(new_dataset_name)



        else:
            print(fr"File Already Exists {new_dataset_name}")


if __name__ == '__main__':
    data_processing = DataProcessing()
    data_processing.get_data_from_kaggle(file_name=fr'Crime_Data_from_2020_to_Present.csv', new_name="crime_data.csv",
                                        kaggle_file_path='ishmaelkiptoo/usa-los-angeles-crimes-data-2020-to-2023')
    data_processing.get_data_from_kaggle(file_name="unemployed_population_1978-12_to_2023-07.csv",
                                        new_name="Unemployement_data.csv",
                                        kaggle_file_path="asaniczka/unemployment-rates-by-demographics-1978-2023")
