import os
import sys
from pathlib import Path
import csv
from tempfile import NamedTemporaryFile
import shutil
import glob


def main():
    parametersFolder = Path(os.environ["CSM_PARAMETERS_ABSOLUTE_PATH"])
    parametersFile = parametersFolder / "parameters.csv"
    if not parametersFile.exists():
        print(f"No parameters file in {parametersFile}")
        sys.exit(-1)

    values = {
        'stock': 0,
        'restock_qty': 0,
        'nb_waiters': 0,
        'initial_stock_dataset': ''
    }
    expectedParameters = list(values.keys())
    with open(parametersFile, 'r') as csvfile:
        parametersReader = csv.reader(csvfile)
        print('Start reading parameters.csv file')
        for row in parametersReader:
            parameter_name = row[0]
            parameterValue = row[1]
            if parameter_name not in expectedParameters:
                print(f'Unknown parameter {parameter_name}')
            else:
                print(f'Value for {parameter_name}: "{parameterValue}"')
                values[parameter_name] = parameterValue

    if values['initial_stock_dataset'] == '':
        print('\nInitial stock file not uploaded, skipping this part...')
    else:
        datasetFolder = parametersFolder / 'initial_stock_dataset'
        datasetFiles = os.listdir(datasetFolder)
        if not datasetFiles:
            print('\nNo files in folder: "{datasetFolder}"')
        else:
            print(f'\nParsing rows of {datasetFiles[0]}')
            with open(datasetFolder/datasetFiles[0], 'r') as initialStockFile:
                datasetReader = csv.reader(initialStockFile)
                for row in datasetReader:
                    print(row)
                    values['stock'] = row[1]
                    break

    dataFolder = Path(os.environ["CSM_DATASET_ABSOLUTE_PATH"])
    files = '\n'.join([f' - {path}' for path in glob.glob(str(dataFolder / "**"), recursive=True)])
    print(f'\nData files:\n{files}')

    tempfile = NamedTemporaryFile('w+t', newline='', delete=False)
    barPath = dataFolder / "Bar.csv"
    print('\nPatching dataset file Bar.csv with parameters values...')
    with open(barPath, newline='') as barFile:
        bar_reader = csv.reader(barFile)
        barWriter = csv.writer(tempfile)

        header = next(bar_reader)
        barWriter.writerow(header)
        column_indices = {'stock': -1, 'restock_qty': -1, 'nb_waiters': -1}
        csv_column_mapping = {'Stock': 'stock', 'RestockQty': 'restock_qty', 'NbWaiters': 'nb_waiters'}
        for index, column in enumerate(header):
            if column in csv_column_mapping:
                parameter_name = csv_column_mapping[column]
                column_indices[parameter_name] = index

        for row in bar_reader:
            for parameter_name, columnIndex in column_indices.items():
                if columnIndex == -1:
                    print(f' - {parameter_name}: parameter never found in CSV header:')
                    print(f'    - CSV header: "{header}"')
                    print(f'    - column mapping: "{csv_column_mapping}"')
                    continue
                previous_value = row[columnIndex]
                new_value = values[parameter_name]
                row[columnIndex] = new_value
                print(f' - {parameter_name}: {previous_value} => {new_value}')
            barWriter.writerow(row)

    tempfile.close()
    shutil.move(tempfile.name, barPath)


if __name__ == "__main__":
    main()
