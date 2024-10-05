import csv
import glob
import re
from datetime import datetime

import netCDF4
import numpy


def dataset_to_csv(month_dataset, formatted_date):
    latitudes = month_dataset.variables['lat'][:]
    longitudes = month_dataset.variables['lon'][:]
    densities = month_dataset.variables['DUCMASS'][:]
    return [
        [formatted_date, latitudes[i], longitudes[j], numpy.mean(densities[:, i, j])]
        for i in range(len(latitudes))
        for j in range(len(longitudes))
    ]

def process_files():
    file_pattern = "./netcdf/MERRA2_400.tavgU_2d_aer_Nx.*.nc4.nc4"
    files = sorted(glob.glob(file_pattern))

    with open('test.csv', 'w', newline='') as csvfile:
        fieldnames = ['datestamp', 'lat', 'lon', 'density']
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fieldnames)

        for file in files:
            with netCDF4.Dataset(file, "r") as month_dataset:
                match = re.search(r'\.(\d{6})\.nc4', file)
                date_str = match.group(1)
                formatted_date = datetime.strptime(date_str, "%Y%m").strftime("%Y-%m-01")
                csvwriter.writerows(dataset_to_csv(month_dataset, formatted_date))


process_files()
