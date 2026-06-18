#!/usr/bin/sh

# Get YAML file name of the test
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <test_name> <nproc>"
    exit 1
else
    testname="$1"
fi

# Set number(s) of procs to run with
if [ "$#" -eq 1 ]; then
    nproc="2 4 8 16 32 64"
else
    nproc="$2"
fi

path_to_flow="../../build-JS_feti"
output_dir_base="test_results/$(basename "$testname" .yaml)"

for n in $nproc
do
    echo "Running on $n procs"

    output_dir=$output_dir_base.$n
    mkdir -p $output_dir
    $path_to_flow/bin/mpiexec -n $n $path_to_flow/bin/flow123d -s $testname -o $output_dir | tee "$output_dir/output.log"
done