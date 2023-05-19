#!/bin/bash

# Move the contents of what's in the INPUT folder here:
mv ./INPUT/* ../../data/input/

# Change to the output directory
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

echo "done"
