#!/bin/bash

# Copyright (c) Cosmo Tech.
# Licensed under the MIT license.

set -e

if [ $# -lt 1 ]
  then
  echo "Missing parameter. Usage:"
  echo "  $0 input_dataset"
  exit 1
fi

dataset=$1
dataset_name=$(basename $dataset)
output_file_name=$dataset_name.zip
tmp_folder="_tmp"

mkdir $tmp_folder
cp -r $dataset $tmp_folder/
wd=$tmp_folder/$dataset_name

mkdir $wd/Nodes
mkdir $wd/Edges
mv $wd/Bar.csv $wd/Nodes
mv $wd/Customer.csv $wd/Nodes
mv $wd/arc_Satisfaction.csv $wd/Edges
mv $wd/Bar_vertex.csv $wd/Edges

pushd $tmp_folder > /dev/null
  zip -r $output_file_name $dataset_name > /dev/null
popd > /dev/null

mv $tmp_folder/$output_file_name .
rm -r $tmp_folder
echo "Dataset archive created: $output_file_name"
