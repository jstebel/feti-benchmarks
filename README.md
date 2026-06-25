# FETI benchmarks

Each subdirectory contains:
- several YAML configurations for Flow123d simulations
- mesh files
- scripts for running the tests on multiple processes and for evaluating the convergence

Example usage:
```sh run_test.sh square/square.r3.yaml; python3 report.py square/square.r3; python3 plot.py square/square```
