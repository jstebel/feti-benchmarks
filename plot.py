import argparse
import math
import os
import re
import sys
import subprocess
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


NPROCS_ORDER = [2, 4, 8, 16, 32, 64]
LEVEL_DIR_RE = re.compile(r"^(?P<testname>.+?)(?:\.r(?P<ref>\d+))?\.(?P<nproc>\d+)$")
YAML_MESH_RE = re.compile(r"^\s*mesh_file:\s*(?P<path>\S+)\s*$")


def split_input_path(path_text):
    path = Path(path_text)
    base_dir = path.parent if str(path.parent) != "." else Path(".")
    testname = path.name
    return base_dir, testname


def discover_levels(base_dir, testname):
    test_results_dir = base_dir / "test_results"
    if not test_results_dir.is_dir():
        raise FileNotFoundError(f"Missing test_results directory: {test_results_dir}")

    levels = {}
    prefix = f"{testname}."

    for entry in test_results_dir.iterdir():
        if not entry.is_dir():
            continue
        match = LEVEL_DIR_RE.match(entry.name)
        if not match or match.group("testname") != testname:
            continue

        ref = int(match.group("ref")) if match.group("ref") is not None else 0
        nproc = int(match.group("nproc"))
        levels.setdefault(ref, {})[nproc] = entry / "output.log"

    if not levels:
        raise FileNotFoundError(f"No matching runs found under {test_results_dir} for {testname!r}")

    return levels


def parse_report_table(stdout_text):
    rows = {}

    for line in stdout_text.splitlines():
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 7:
            continue
        if not parts[0].isdigit():
            continue
        if parts[1].startswith("Soubor nenalezen"):
            continue

        def parse_int(cell):
            return None if cell == "N/A" else int(cell)

        def parse_float(cell):
            return None if cell == "N/A" else float(cell)

        nproc = int(parts[0])
        rows[nproc] = {
            "nproc": nproc,
            "reason": parse_int(parts[1]),
            "lin_it": parse_int(parts[2]),
            "hessian": parse_int(parts[3]),
            "cg": parse_int(parts[4]),
            "residual": parse_float(parts[5]),
            "duration": parse_float(parts[6]),
        }

    return rows


def mesh_file_for_level(base_dir, testname, ref):
    yaml_name = f"{testname}.yaml" if ref == 0 else f"{testname}.r{ref}.yaml"
    yaml_path = base_dir / yaml_name
    if not yaml_path.exists():
        return None

    mesh_rel = None
    with open(yaml_path, "r") as f:
        for line in f:
            match = YAML_MESH_RE.match(line)
            if match:
                mesh_rel = match.group("path")
                break

    if mesh_rel is None:
        return None

    mesh_path = base_dir / mesh_rel
    if mesh_path.exists():
        return mesh_path

    alt_mesh_path = base_dir / "mesh" / Path(mesh_rel).name
    if alt_mesh_path.exists():
        return alt_mesh_path

    return None


def count_mesh_elements(mesh_path):
    if mesh_path is None or not mesh_path.exists():
        return None

    with open(mesh_path, "r") as f:
        for line in f:
            if line.strip() == "$Elements":
                count_line = next(f, "").strip()
                if count_line.isdigit():
                    return int(count_line)
                break

    return None


def collect_series(base_dir, testname, levels, residual_tol, min_elems):
    series = []
    report_script = Path(__file__).with_name("report.py")

    for ref in sorted(levels):
        runs = levels[ref]
        x_values = []
        y_values = []
        t_values = []
        element_count = count_mesh_elements(mesh_file_for_level(base_dir, testname, ref))
        failed_runs = []
        level_input = str(base_dir / (testname if ref == 0 else f"{testname}.r{ref}"))

        if min_elems is not None and (element_count is None or element_count <= min_elems):
            print(
                f"Skipping r{ref}: mesh elements {element_count if element_count is not None else 'N/A'} "
                f"are not above {min_elems}",
                file=sys.stderr,
            )
            continue

        proc = subprocess.run(
            [sys.executable, str(report_script), level_input],
            check=True,
            capture_output=True,
            text=True,
        )
        rows_by_nproc = parse_report_table(proc.stdout)

        for nproc in sorted(runs):
            row = rows_by_nproc.get(nproc)
            if row is None:
                continue

            lin_it = row["lin_it"]
            reason = row["reason"]
            residual = row["residual"]
            duration = row["duration"]
            if lin_it is None or reason is None or residual is None:
                continue

            if reason <= 0 or residual > residual_tol:
                failed_runs.append(f"{testname}{'.r' + str(ref) if ref else ''}.{nproc} (reason={reason}, residual={residual:.3e})")
                continue

            x_values.append(nproc)
            y_values.append(lin_it)
            t_values.append(float("nan") if duration is None else duration)

        if x_values:
            if failed_runs:
                print(
                    f"Skipping unsuccessful runs for r{ref}: " + ", ".join(failed_runs),
                    file=sys.stderr,
                )
            series.append(
                {
                    "ref": ref,
                    "x": x_values,
                    "y": y_values,
                    "duration": t_values,
                    "elements": element_count,
                    "failed_runs": failed_runs,
                }
            )

    return series


def plot_series(base_dir, testname, series, residual_tol):
    if not series:
        raise RuntimeError(f"No plot data found for {testname!r}")

    fig, ax = plt.subplots(figsize=(7.5, 4.8), constrained_layout=True)

    colors = plt.cm.viridis(
        [0.15 + 0.7 * i / max(1, len(series) - 1) for i in range(len(series))]
    )

    for idx, item in enumerate(series):
        if item["ref"] == 0:
            label_prefix = "original"
        else:
            label_prefix = f"r{item['ref']}"

        if item["elements"] is not None:
            label = f"{item['elements']} elements"
        else:
            label = label_prefix

        ax.plot(
            item["x"],
            item["y"],
            marker="o",
            linewidth=1.8,
            markersize=5,
            color=colors[idx],
            label=label,
        )

    ax.set_xlabel("nproc")
    ax.set_ylabel("Lin. it")
    ax.set_title(f"{testname}: Lin. it vs nproc")
    ax.set_xscale("log")
    #ax.set_yscale("log")
    ax.set_xticks(NPROCS_ORDER)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.grid(True, which="both", linestyle=":", linewidth=0.7, alpha=0.8)
    ax.legend(title="Mesh size", frameon=False)

    subtitle = f"successful runs only, residual <= {residual_tol:g}"
    ax.text(0.5, -0.16, subtitle, transform=ax.transAxes, ha="center", va="top")

    output_path = base_dir / f"{testname}_lin_it_vs_nproc.pdf"
    fig.savefig(output_path, format="pdf")
    print(output_path)


def plot_time_series(base_dir, testname, series, residual_tol):
    if not series:
        raise RuntimeError(f"No plot data found for {testname!r}")

    fig, ax = plt.subplots(figsize=(7.5, 4.8), constrained_layout=True)

    colors = plt.cm.viridis(
        [0.15 + 0.7 * i / max(1, len(series) - 1) for i in range(len(series))]
    )

    for idx, item in enumerate(series):
        if item["ref"] == 0:
            label_prefix = "original"
        else:
            label_prefix = f"r{item['ref']}"

        if item["elements"] is not None:
            label = f"{item['elements']} elements"
        else:
            label = label_prefix

        ax.plot(
            item["x"],
            item["duration"],
            marker="o",
            linewidth=1.8,
            markersize=5,
            color=colors[idx],
            label=label,
        )

        timed_points = sorted(
            (nproc, duration)
            for nproc, duration in zip(item["x"], item["duration"])
            if math.isfinite(duration) and duration > 0
        )
        if timed_points:
            first_nproc, first_duration = timed_points[0]
            ideal_x = sorted(nproc for nproc in item["x"] if nproc >= first_nproc)
            ax.plot(
                ideal_x,
                [first_duration * first_nproc / nproc for nproc in ideal_x],
                color="grey",
                linestyle=":",
                linewidth=1.5,
                zorder=1,
            )

    ax.set_xlabel("nproc")
    ax.set_ylabel("Time [s]")
    ax.set_title(f"{testname}: time vs nproc")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(NPROCS_ORDER)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.grid(True, which="both", linestyle=":", linewidth=0.7, alpha=0.8)
    ax.legend(title="Mesh size", frameon=False)

    subtitle = f"successful runs only, residual <= {residual_tol:g}"
    ax.text(0.5, -0.16, subtitle, transform=ax.transAxes, ha="center", va="top")

    output_path = base_dir / f"{testname}_time_vs_nproc.pdf"
    fig.savefig(output_path, format="pdf")
    print(output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("test", help="Path like cube/cube-frac")
    parser.add_argument(
        "--tol",
        type=float,
        default=1e-3,
        help="Maximum allowed residual for a run to count as successful",
    )
    parser.add_argument(
        "--min_elems",
        type=int,
        default=None,
        help="Only include refinement levels with more than this many mesh elements",
    )
    args = parser.parse_args()

    base_dir, testname = split_input_path(args.test)
    levels = discover_levels(base_dir, testname)
    series = collect_series(base_dir, testname, levels, args.tol, args.min_elems)
    plot_series(base_dir, testname, series, args.tol)
    plot_time_series(base_dir, testname, series, args.tol)


if __name__ == "__main__":
    main()
