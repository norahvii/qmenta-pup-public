#!/bin/bash

function move_FS_files() {
    fs_mri_path=`find INPUT/FreeSurfer/* -name "mri" -type d | head -n 1`
    fs_path=`echo ${fs_mri_path} | sed -e 's/\/mri//g'`; echo $fs_path
    mkdir -p ../../data/input/FreeSurfer
    mv ${fs_path}/* ../../data/input/FreeSurfer/
}

move_FS_files
echo "Finished moving FreeSurfer folders."

function move_PET_files() {
    find ./INPUT/PET -type f -name "*.dcm" -exec mkdir -p ../../data/input/PET/ \; -exec mv {} ../../data/input/PET/ \;
}

move_PET_files
echo "Finished moving PET files."

pushd ./OUTPUT/

# Loop over all .params files in the input directory
find /data/input/params -name "*.params" | while read params_file; do
    # Generate the output log file path based on the name of the input file
    log_file="$(basename "$params_file" .params).petlog"

    # Run petproc with the current parameter file and redirect output to the log file
    petproc "$params_file" > "$log_file"
done

# Return to the previous directory
popd

echo "petproc completed successfully!"
