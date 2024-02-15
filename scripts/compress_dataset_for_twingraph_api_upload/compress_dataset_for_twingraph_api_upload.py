#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) Cosmo Tech.
# Licensed under the MIT license.


import os
import sys
import pathlib
import argparse
import tempfile


def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a zip archive of the input dataset, that can be uploaded '
                                                 'when using the Cosmo Tech twingraph API.')
    parser.add_argument("dataset_folder_path", help="Path to the folder of the dataset to process", type=pathlib.Path)
    parser.add_argument("-f", "--force", help="Force overwrite of output file", default=False, type=bool)
    args = parser.parse_args()
    return args


def check_output_does_not_exist(output_file_path):
    if os.path.exists(output_file_path):
        print(f'Output file {output_file_path} already exists. Use option -f to overwrite it')
        sys.exit(-1)


def validate_dataset_folder_structure(dataset_folder_path):
    if not os.path.exists(dataset_folder_path):
        print(f'Not found: {dataset_folder_path}')
        sys.exit(-1)
    if not os.path.isdir(dataset_folder_path):
        print(f'Not a folder: {dataset_folder_path}')
        sys.exit(-1)

    expected_files = {'arc_Satisfaction.csv', 'Bar.csv', 'Bar_vertex.csv', 'Customer.csv'}
    dataset_files = next(os.walk(dataset_folder_path), (None, None, []))[2]
    missing_files = list(expected_files-set(dataset_files))
    if len(missing_files) > 0:
        formatted_missing_files = "\n".join([f" - {f}" for f in missing_files])
        print(f'Missing files in dataset folder:\n{formatted_missing_files}')
        sys.exit(-1)


def generate_output_dataset(input_path, working_dir)


def main():
    args = parse_arguments()
    validate_dataset_folder_structure(args.dataset_folder_path)
    [base_folder, dataset_folder_name] = [args.dataset_folder_path.parent, args.dataset_folder_path.name]

    output_file_name = f'{dataset_folder_name}.zip'
    output_file_path = base_folder / output_file_name
    if not args.force:
        check_output_does_not_exist(output_file_path)

    with tempfile.TemporaryDirectory() as tmp_dir:
        os.mkdir()
        print('created temporary directory', tmpdirname)


if __name__ == "__main__":
    main()
