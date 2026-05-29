# FETI benchmarks

Each subdirectory contains:
- several YAML configurations for Flow123d simulations
- mesh files
- scripts for running the tests on multiple processes and for evaluating the convergence

Example usage:
```cd square; sh run_test.sh square.r3.yaml; python3 report.py square.r3```
