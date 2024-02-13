import os
import sys
from pathlib import Path
import csv
from tempfile import NamedTemporaryFile
import shutil
import glob


def main():
    parameters_folder = Path(os.environ["CSM_PARAMETERS_ABSOLUTE_PATH"])
    parameters_file = parameters_folder / "parameters.csv"
    if not parameters_file.exists():
        print(f"No parameters file in {parameters_file}")
        sys.exit(-1)

    values = {
        'stock': 0,
        'restock_qty': 0,
        'nb_waiters': 0,
        'initial_stock_dataset': ''
    }
    expected_parameters = list(values.keys())
    with open(parameters_file, 'r') as csvfile:
        parameters_reader = csv.reader(csvfile)
        next(parameters_reader)  # Skip header row
        print('Start reading parameters.csv file')
        for row in parameters_reader:
            parameter_name = row[0]
            parameter_value = row[1]
            if parameter_name not in expected_parameters:
                print(f'Unknown parameter {parameter_name}')
            else:
                print(f'Value for {parameter_name}: "{parameter_value}"')
                values[parameter_name] = parameter_value

    if values['initial_stock_dataset'] == '':
        print('\nInitial stock file not uploaded, skipping this part...')
    else:
        dataset_folder = parameters_folder / 'initial_stock_dataset'
        dataset_files = os.listdir(dataset_folder)
        if not dataset_files:
            print(f'\nNo files in folder: "{dataset_folder}"')
        else:
            print(f'\nParsing rows of {dataset_files[0]}')
            with open(dataset_folder/dataset_files[0], 'r') as initial_stock_file:
                dataset_reader = csv.reader(initial_stock_file)
                for row in dataset_reader:
                    print(row)
                    values['stock'] = row[1]
                    break

    data_folder = Path(os.environ["CSM_DATASET_ABSOLUTE_PATH"])
    files = '\n'.join([f' - {path}' for path in glob.glob(str(data_folder / "**"), recursive=True)])
    print(f'\nData files:\n{files}')

    temp_file = NamedTemporaryFile('w+t', newline='', delete=False)
    bar_file_path = data_folder / "Bar.csv"
    print('\nPatching dataset file Bar.csv with parameters values...')
    with open(bar_file_path, newline='') as bar_file:
        bar_reader = csv.reader(bar_file)
        bar_writer = csv.writer(temp_file)

        header = next(bar_reader)
        bar_writer.writerow(header)
        column_indices = {'stock': -1, 'restock_qty': -1, 'nb_waiters': -1}
        csv_column_mapping = {'Stock': 'stock', 'RestockQty': 'restock_qty', 'NbWaiters': 'nb_waiters'}
        for index, column in enumerate(header):
            if column in csv_column_mapping:
                parameter_name = csv_column_mapping[column]
                column_indices[parameter_name] = index

        for row in bar_reader:
            for parameter_name, column_index in column_indices.items():
                if column_index == -1:
                    print(f' - {parameter_name}: parameter never found in CSV header:')
                    print(f'    - CSV header: "{header}"')
                    print(f'    - column mapping: "{csv_column_mapping}"')
                    continue
                previous_value = row[column_index]
                new_value = values[parameter_name]
                row[column_index] = new_value
                print(f' - {parameter_name}: {previous_value} => {new_value}')
            bar_writer.writerow(row)

    temp_file.close()
    shutil.move(temp_file.name, bar_file_path)


if __name__ == "__main__":
    main()
