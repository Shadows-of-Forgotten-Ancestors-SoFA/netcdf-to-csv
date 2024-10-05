import csv
import glob
import re
from datetime import datetime
import time

import netCDF4
import numpy

def dataset_to_csv(current_dataset, previous_datasets, formatted_date):
    rows = []
    latitudes = current_dataset.variables['lat'][:]
    longitudes = current_dataset.variables['lon'][:]
    densities = current_dataset.variables['DUCMASS'][:]

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # top, bottom, left, right

    for i in range(len(latitudes)):
        for j in range(len(longitudes)):
            current_value = numpy.mean(densities[:, i, j])

            neighbor_values = []
            for di, dj in directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < len(latitudes) and 0 <= nj < len(longitudes):
                    neighbor_values.append(numpy.mean(densities[:, ni, nj]))
                else:
                    neighbor_values.append(current_value)
            top, bottom, left, right = neighbor_values

            previous_values = [numpy.mean(ds.variables['DUCMASS'][:, i, j]) for ds in previous_datasets]

            rows.append([
                formatted_date,
                latitudes[i],
                longitudes[j],
                current_value,
                top, bottom, left, right,
                *previous_values
            ])

    return rows

def process_files(months_lag):
    files = sorted(glob.glob("./netcdf/MERRA2_400.tavgU_2d_aer_Nx.*.nc4.nc4"))

    with open('test.csv', 'w', newline='') as csvfile:
        fieldnames = ['datestamp', 'lat', 'lon', 'density', 'top', 'bottom', 'left', 'right']
        fieldnames += [f'month-{i+1}' for i in range(months_lag)]
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fieldnames)

        for i in range(months_lag, len(files)):
            current = files[i]
            previous_files = files[i-months_lag:i]

            previous_datasets = [netCDF4.Dataset(prev, "r") for prev in previous_files]

            with netCDF4.Dataset(current, "r") as month_dataset:
                date_str = re.search(r'\.(\d{6})\.nc4', current).group(1)
                formatted_date = int(datetime.strptime(date_str, "%Y%m").timestamp())
                csvwriter.writerows(dataset_to_csv(month_dataset, previous_datasets, formatted_date))

            for ds in previous_datasets:
                ds.close()

process_files(1)
