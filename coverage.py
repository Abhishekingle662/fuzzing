import os, pathlib, sys
import re
from typing import List, Tuple


print("cwd  :", os.getcwd())
print("argv0:", os.path.abspath(sys.argv[0]))

def parse_time(name: str) -> float:
    return float(re.findall(",time:([0-9]+),", name)[0]) / 1000

def compute_coverage(run_dir: str, cov_dir: str) -> List[Tuple[float, int]]:
    # Get queue files and sort by time
    queue_files = [f for f in os.listdir(run_dir) if f.startswith("id:")]
    queue_files.sort(key=lambda f: parse_time(f) if ",time:" in f else 0)
    
    # Map queue filenames to coverage files
    cov_files = {f: os.path.join(cov_dir, f) for f in queue_files}
    
    covered_locations = set()
    coverage_list = []
    
    for fname in queue_files:
        time = parse_time(fname) if ",time:" in fname else 0
        with open(cov_files[fname], "rb") as f:
            bitmap = f.read()
            for idx, byte in enumerate(bitmap):
                if byte != 0:
                    covered_locations.add(idx)
        coverage_list.append((time, len(covered_locations)))
    
    return coverage_list

#below code prints the coverage list for each run_dir and cov_dir

for x in range(10):
    run_dir = f"/lab/02-Fuzzing/out/dir_asan/{x}/default/queue"
    cov_dir = f"/lab/02-Fuzzing/out/cov_asan_{x}"
    cov_list = compute_coverage(run_dir, cov_dir)
    print(cov_list)  # e.g., [(0.0, 10), (1.234, 15), ...]