import os
import re
import sys
from datetime import datetime

def parse_logs(testname, nprocs):
    # Regulární výrazy pro hledání hodnot
    regex_lin_it = re.compile(r"\[mech solver\] lin\. it:\s+(\d+), reason: (-?\d+), residual: ([\d\.\+-e]+)")
    regex_hessian = re.compile(r"number of Hessian multiplications\s+(\d+)")
    regex_cg = re.compile(r"number of CG steps\s+(\d+)")
    # Regex pro čas a značku (zachytí HH:MM:SS.SSS a zbytek řádku)
    regex_time = re.compile(r"^(\d{2}:\d{2}:\d{2}\.\d{3})\s+MESSAGE\.(\[.*?\])")

    print(f"{'nproc':<6} | {'Reason':<8} | {'Lin. It.':<10} | {'Hessian':<8} | {'CG Steps':<10} | { 'Residual':<10} | {'Time [s]':<8}")
    print("-" * 78)

    for n in nprocs:
        log_path = f"test_results/{testname}.{n}/output.log" # Upravte cestu dle reality
        
        if not os.path.exists(log_path):
            print(f"{n:<6} | Soubor nenalezen ({log_path})")
            continue

        res = reason = lin_it = hessian = cg = "N/A"
        t_start = t_end = None

        with open(log_path, 'r') as f:
            for line in f:
                # Hledání iterací a matic (pouze první výskyt)
                if lin_it == "N/A":
                    match = regex_lin_it.search(line)
                    if match:
                        lin_it = match.group(1)
                        reason = match.group(2)
                        res = match.group(3)
                
                if hessian == "N/A":
                    match = regex_hessian.search(line)
                    if match: hessian = match.group(1)

                if cg == "N/A":
                    match = regex_cg.search(line)
                    if match: cg = match.group(1)

                # Hledání časů pro rozdíl
                time_match = regex_time.search(line)
                if time_match:
                    timestamp_str = time_match.group(1)
                    tag = time_match.group(2)
                    
                    # Převod na objekt datetime pro výpočty
                    current_t = datetime.strptime(timestamp_str, "%H:%M:%S.%f")

                    if "[mech solver]" in tag and t_end is None:
                        t_end = current_t
                    if "[nonlinear solver]" in tag and t_start is None:
                        t_start = current_t

        # Výpočet rozdílu času
        duration_str = "N/A"
        if t_start and t_end:
            diff = t_end - t_start
            duration_str = f"{diff.total_seconds():.3f}"

        print(f"{n:<6} | {reason:<8} | {lin_it:<10} | {hessian:<8} | {cg:<10} | {res:<10} | {duration_str:<8}")

if __name__ == "__main__":
    # Nastavte jméno testu a nprocs podle vašeho předchozího skriptu
    TEST_NAME = sys.argv[1]
    NPROCS = [2, 4, 8, 16, 32, 64]
    parse_logs(TEST_NAME, NPROCS)