#!/bin/bash
READER=ellips
NXDL=NXellipsometry

function update_test_file {
  echo "Update reference files"
  dataconverter test-data.dat  eln_data.yaml --reader $READER --nxdl $NXDL --output test-data.nxs
}

project_dir=$(dirname $(dirname $(realpath $0)))
cd $project_dir/tests/data
update_test_file