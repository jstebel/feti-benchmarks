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

path_to_flow="../flow123d_rel/build-JS_feti"

test_dir=$(echo "$testname" | rev | cut -d"/" -f2 | rev)
output_dir_base="test_results/$(basename "$testname" .yaml)"

for n in $nproc
do
    echo "Running on $n procs"

    output_dir=$output_dir_base.$n
    mkdir -p $test_dir/$output_dir
    hostname > "$test_dir/$output_dir/output.log"
    $path_to_flow/bin/mpiexec -genv I_MPI_PIN=1 -genv I_MPI_PIN_DOMAIN=core -n $n $path_to_flow/bin/flow123d -s $testname -o $output_dir | tee -a "$test_dir/$output_dir/output.log"
done