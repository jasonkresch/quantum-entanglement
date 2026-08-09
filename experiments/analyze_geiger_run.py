#!/usr/bin/env python3
"""
Analyze Nano ESP32 / MightyOhm Geiger coincidence CSV logs.

This is an enhanced version of the earlier timing-histogram script.  In addition
to the histogram and coincidence-window scan, it writes a one-run log in CSV,
JSON, and human-readable TXT formats.  The log includes every run attribute that
can be inferred from the raw CSV, plus optional metadata supplied on the command
line.

Typical use:

    python3 analyze_geiger_run_enhanced.py run.csv \
        --run-id P1 \
        --half-window-us 10 \
        --center-us 0 \
        --orientation perpendicular \
        --geometry "Al blocks, 90-degree scatter" \
        --detector-separation "..." \
        --source-position "centered" \
        --shielding "none" \
        --aluminum present \
        --notes "overnight run"

Outputs:

    <prefix>_signed_delta_histogram.png
    <prefix>_window_scan.png
    <prefix>_window_scan_summary.csv
    <prefix>_run_log.csv
    <prefix>_run_log.json
    <prefix>_run_log.txt
"""

import argparse
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


DEFAULT_LAGS_US = [
    500_000, 1_000_000, 1_500_000, 2_000_000, 2_500_000, 3_000_000,
    -500_000, -1_000_000, -1_500_000, -2_000_000, -2_500_000, -3_000_000,
]

DEFAULT_THRESHOLDS_US = [
    1, 2, 3, 5, 7, 10, 15, 20, 25, 30,
    40, 50, 75, 100, 150, 200, 250, 500, 1000,
]


def parse_int_list(s: str):
    """Parse comma-separated integers, e.g. '500000,1000000,-500000'."""
    if s is None or str(s).strip() == "":
        return []
    return [int(x.strip()) for x in str(s).split(",") if x.strip()]


def safe_float(x):
    try:
        if x is None:
            return None
        v = float(x)
        if math.isnan(v):
            return None
        return v
    except Exception:
        return None


def safe_int(x):
    try:
        if x is None:
            return None
        if isinstance(x, float) and math.isnan(x):
            return None
        return int(x)
    except Exception:
        return None


def load_csv_and_event_times(csv_path: str):
    """
    Load event lines from the logger CSV.

    Expected columns from your logger:
      record_type, board_t_us, detector

    Event rows:
      record_type == "E"
      detector == "L" or "R"
      board_t_us = Arduino/Nano ESP32 timestamp in microseconds
    """
    df = pd.read_csv(csv_path)

    required = {"record_type", "board_t_us", "detector"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

    events = df[df["record_type"] == "E"].copy()
    events["board_t_us"] = pd.to_numeric(events["board_t_us"], errors="coerce")
    events = events.dropna(subset=["board_t_us", "detector"])
    events["board_t_us"] = events["board_t_us"].astype(np.int64)

    left = events.loc[events["detector"] == "L", "board_t_us"].to_numpy(np.int64).copy()
    right = events.loc[events["detector"] == "R", "board_t_us"].to_numpy(np.int64).copy()

    left.sort()
    right.sort()

    if len(left) == 0 or len(right) == 0:
        raise ValueError("Need at least one L event and one R event.")

    t0 = int(min(left[0], right[0]))
    t1 = int(max(left[-1], right[-1]))
    duration_s = (t1 - t0) / 1_000_000.0

    if duration_s <= 0:
        raise ValueError("Run duration is zero or negative; check board_t_us data.")

    return df, events, left, right, t0, t1, duration_s


def extract_host_time_info(df: pd.DataFrame):
    """
    Extract host-side start/end timestamps if the serial logger CSV includes them.

    Existing logger script usually writes:
      host_time_utc
      host_time_unix
    """
    info = {
        "host_start_utc": "",
        "host_end_utc": "",
        "host_duration_s": "",
    }

    if "host_time_utc" in df.columns:
        host_times = df["host_time_utc"].dropna().astype(str)
        host_times = host_times[host_times != ""]
        if len(host_times) > 0:
            info["host_start_utc"] = host_times.iloc[0]
            info["host_end_utc"] = host_times.iloc[-1]

    if "host_time_unix" in df.columns:
        unix = pd.to_numeric(df["host_time_unix"], errors="coerce").dropna()
        if len(unix) >= 2:
            info["host_duration_s"] = float(unix.iloc[-1] - unix.iloc[0])

    return info


def extract_final_arduino_summary(df: pd.DataFrame):
    """
    Pull final summary-row values if the CSV includes record_type == 'S'.

    These are not used as the primary analysis numbers, because this script
    recomputes prompt/lag counts from raw event timestamps.  They are useful for
    cross-checks and for dropped-event diagnostics.
    """
    out = {
        "arduino_final_left_cpm": "",
        "arduino_final_right_cpm": "",
        "arduino_final_prompt_cpm": "",
        "arduino_final_delayed_cpm": "",
        "arduino_final_total_left": "",
        "arduino_final_total_right": "",
        "arduino_final_total_prompt": "",
        "arduino_final_total_delayed": "",
        "arduino_final_dropped": "",
        "arduino_max_dropped": "",
    }

    if "record_type" not in df.columns:
        return out

    summaries = df[df["record_type"] == "S"].copy()
    if len(summaries) == 0:
        # Some logger versions may still have dropped field on event rows.
        if "dropped" in df.columns:
            dropped = pd.to_numeric(df["dropped"], errors="coerce").dropna()
            if len(dropped) > 0:
                out["arduino_max_dropped"] = int(dropped.max())
        return out

    last = summaries.iloc[-1]

    mapping = {
        "left_cpm": "arduino_final_left_cpm",
        "right_cpm": "arduino_final_right_cpm",
        "prompt_cpm": "arduino_final_prompt_cpm",
        "delayed_cpm": "arduino_final_delayed_cpm",
        "total_left": "arduino_final_total_left",
        "total_right": "arduino_final_total_right",
        "total_prompt": "arduino_final_total_prompt",
        "total_delayed": "arduino_final_total_delayed",
        "dropped": "arduino_final_dropped",
    }

    for src, dst in mapping.items():
        if src in summaries.columns:
            val = last.get(src)
            if pd.notna(val) and val != "":
                # Preserve as numeric when possible.
                fv = safe_float(val)
                out[dst] = fv if fv is not None else str(val)

    if "dropped" in summaries.columns:
        dropped = pd.to_numeric(summaries["dropped"], errors="coerce").dropna()
        if len(dropped) > 0:
            out["arduino_max_dropped"] = int(dropped.max())

    return out


def signed_pair_deltas(left_times, right_times, max_abs_us):
    """
    For every left event, find all right events within ±max_abs_us.
    Return signed deltas:

      delta = t_right - t_left

    This produces the prompt histogram.
    """
    deltas = []

    for t_left in left_times:
        lo = t_left - max_abs_us
        hi = t_left + max_abs_us

        i = np.searchsorted(right_times, lo, side="left")
        j = np.searchsorted(right_times, hi, side="right")

        if j > i:
            deltas.extend((right_times[i:j] - t_left).tolist())

    return np.array(deltas, dtype=np.int64)


def count_window(deltas, center_us, half_width_us):
    """
    Count deltas inside:

      center_us - half_width_us <= delta <= center_us + half_width_us
    """
    return int(np.sum(
        (deltas >= center_us - half_width_us) &
        (deltas <= center_us + half_width_us)
    ))


def li_ma_significance(n_on, n_off, alpha):
    """
    Li & Ma on/off significance, Eq. 17 style, with sign.

    n_on: prompt-window count.
    n_off: total count across off/lag windows.
    alpha: exposure ratio.  If there are M equal lag windows, alpha = 1/M.

    This is a better one-number significance than net/sqrt(prompt+background)
    when background is estimated from multiple off windows.
    """
    n_on = float(n_on)
    n_off = float(n_off)
    alpha = float(alpha)

    if alpha <= 0:
        return float("nan")
    if n_on < 0 or n_off < 0:
        return float("nan")
    if n_on == 0 and n_off == 0:
        return 0.0

    total = n_on + n_off
    if total <= 0:
        return 0.0

    term_on = 0.0
    if n_on > 0:
        term_on = n_on * math.log(((1 + alpha) / alpha) * (n_on / total))

    term_off = 0.0
    if n_off > 0:
        term_off = n_off * math.log((1 + alpha) * (n_off / total))

    val = 2.0 * (term_on + term_off)
    if val < 0 and val > -1e-12:
        val = 0.0

    z = math.sqrt(max(0.0, val))
    expected_background = alpha * n_off
    if n_on < expected_background:
        z = -z
    return z


def normal_one_sided_p_from_z(z):
    """Upper-tail one-sided p-value for a normal z."""
    if z is None or math.isnan(z):
        return float("nan")
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def normal_two_sided_p_from_z(z):
    """Two-sided p-value for a normal z."""
    if z is None or math.isnan(z):
        return float("nan")
    return math.erfc(abs(z) / math.sqrt(2.0))


def make_histogram_plot(
    prompt_deltas,
    lag_deltas_combined,
    n_lags,
    out_path,
    hist_range_us,
    bin_width_us,
    title,
):
    bins = np.arange(-hist_range_us, hist_range_us + bin_width_us, bin_width_us)
    centers = (bins[:-1] + bins[1:]) / 2

    prompt_hist, _ = np.histogram(prompt_deltas, bins=bins)
    lag_hist_combined, _ = np.histogram(lag_deltas_combined, bins=bins)

    # Average lagged background per lag offset.
    lag_hist_avg = lag_hist_combined / n_lags

    plt.figure(figsize=(10, 5.5))
    plt.step(centers, prompt_hist, where="mid", label="Prompt L/R pairs")
    plt.step(centers, lag_hist_avg, where="mid", label="Average lagged background")

    plt.xlabel("Signed timing difference, t_right - t_left (µs)")
    plt.ylabel(f"Count per {bin_width_us} µs bin")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def make_window_scan_plot(summary_df, out_path):
    plt.figure(figsize=(10, 5.5))
    plt.plot(summary_df["half_window_us"], summary_df["li_ma_z"], marker="o", label="Li & Ma z")
    plt.plot(summary_df["half_window_us"], summary_df["approx_z"], marker="o", label="simple z", alpha=0.7)
    plt.xscale("log")
    plt.xlabel("Coincidence half-window (µs)")
    plt.ylabel("Significance estimate")
    plt.title("Coincidence-window scan")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def compute_counts_for_window(prompt_deltas, lag_deltas_by_lag, center_us, half_window_us, duration_s):
    prompt_count = count_window(prompt_deltas, center_us, half_window_us)

    lag_counts = np.array([
        count_window(deltas, center_us, half_window_us)
        for deltas in lag_deltas_by_lag
    ], dtype=float)

    n_lags = len(lag_counts)
    total_lag_count = float(lag_counts.sum())
    avg_lag_count = float(lag_counts.mean()) if n_lags > 0 else float("nan")
    lag_std = float(lag_counts.std(ddof=1)) if n_lags > 1 else 0.0

    net_count = float(prompt_count - avg_lag_count)

    denom = math.sqrt(prompt_count + avg_lag_count) if prompt_count + avg_lag_count > 0 else float("nan")
    approx_z = net_count / denom if denom and not math.isnan(denom) else float("nan")

    alpha = 1.0 / n_lags if n_lags > 0 else float("nan")
    li_ma_z = li_ma_significance(prompt_count, total_lag_count, alpha)

    prompt_cpm = prompt_count / duration_s * 60.0
    lag_cpm = avg_lag_count / duration_s * 60.0
    net_cpm = net_count / duration_s * 60.0

    return {
        "center_us": float(center_us),
        "half_window_us": int(half_window_us),
        "prompt_count": int(prompt_count),
        "total_lag_count_across_lags": total_lag_count,
        "avg_lag_count": avg_lag_count,
        "lag_count_std": lag_std,
        "net_count": net_count,
        "approx_z": approx_z,
        "li_ma_z": li_ma_z,
        "li_ma_one_sided_p": normal_one_sided_p_from_z(li_ma_z),
        "li_ma_two_sided_p": normal_two_sided_p_from_z(li_ma_z),
        "prompt_cpm": prompt_cpm,
        "lag_cpm": lag_cpm,
        "net_cpm": net_cpm,
        "n_lags": n_lags,
        "alpha": alpha,
        "lag_counts_by_offset": [int(x) for x in lag_counts.tolist()],
    }


def build_window_scan(prompt_deltas, lag_deltas_by_lag, center_us, thresholds, duration_s):
    rows = []
    for half_window_us in thresholds:
        rows.append(compute_counts_for_window(
            prompt_deltas=prompt_deltas,
            lag_deltas_by_lag=lag_deltas_by_lag,
            center_us=center_us,
            half_window_us=half_window_us,
            duration_s=duration_s,
        ))
    return pd.DataFrame(rows)


def sanitize_for_csv(d):
    """
    Convert list/dict values to JSON strings so a one-row CSV stays readable.
    """
    out = {}
    for k, v in d.items():
        if isinstance(v, (list, dict, tuple)):
            out[k] = json.dumps(v)
        else:
            out[k] = v
    return out


def write_run_logs(run_log, out_prefix):
    csv_path = Path(f"{out_prefix}_run_log.csv")
    json_path = Path(f"{out_prefix}_run_log.json")
    txt_path = Path(f"{out_prefix}_run_log.txt")

    pd.DataFrame([sanitize_for_csv(run_log)]).to_csv(csv_path, index=False)

    with open(json_path, "w") as f:
        json.dump(run_log, f, indent=2)

    # Human-readable text summary.
    ordered_keys = [
        "run_id",
        "raw_csv_filename",
        "host_start_utc",
        "host_end_utc",
        "duration_s",
        "duration_min",
        "duration_h",
        "coincidence_window",
        "center_us",
        "half_window_us",
        "lag_offsets_us",
        "detector_geometry",
        "detector_separation",
        "source_position",
        "shielding_collimator_condition",
        "aluminum_blocks",
        "detector_orientation",
        "left_total_counts",
        "right_total_counts",
        "left_cpm",
        "right_cpm",
        "prompt_count",
        "avg_lag_count",
        "net_count",
        "prompt_cpm",
        "lag_cpm",
        "net_cpm",
        "approx_z",
        "li_ma_z",
        "li_ma_one_sided_p",
        "li_ma_two_sided_p",
        "arduino_max_dropped",
        "notes",
    ]

    with open(txt_path, "w") as f:
        f.write("Geiger coincidence run log\n")
        f.write("==========================\n\n")
        for key in ordered_keys:
            if key in run_log:
                f.write(f"{key}: {run_log[key]}\n")

        f.write("\nAdditional fields\n")
        f.write("-----------------\n")
        for key in sorted(run_log.keys()):
            if key not in ordered_keys:
                f.write(f"{key}: {run_log[key]}\n")

    return csv_path, json_path, txt_path


def analyze(
    csv_path,
    out_prefix=None,
    max_abs_us=1000,
    hist_range_us=100,
    bin_width_us=5,
    center_us=0.0,
    half_window_us=10,
    use_best_window=False,
    lags_us=None,
    thresholds=None,
    run_id="",
    detector_geometry="",
    detector_separation="",
    source_position="",
    shielding="",
    aluminum="",
    orientation="",
    notes="",
):
    csv_path = Path(csv_path)

    if out_prefix is None:
        out_prefix = csv_path.with_suffix("").name

    out_prefix = Path(out_prefix)

    if lags_us is None:
        lags_us = DEFAULT_LAGS_US
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS_US
    if half_window_us not in thresholds:
        thresholds = sorted(set(list(thresholds) + [int(half_window_us)]))

    df, events, left, right, t0_us, t1_us, duration_s = load_csv_and_event_times(str(csv_path))
    host_info = extract_host_time_info(df)
    arduino_summary = extract_final_arduino_summary(df)

    left_cpm = len(left) / duration_s * 60.0
    right_cpm = len(right) / duration_s * 60.0

    print()
    print("Run summary")
    print("-----------")
    print(f"Input file:      {csv_path}")
    print(f"Duration:        {duration_s:.1f} s = {duration_s / 60:.2f} min = {duration_s / 3600:.3f} h")
    print(f"Left events:     {len(left):,}")
    print(f"Right events:    {len(right):,}")
    print(f"Left CPM:        {left_cpm:.1f}")
    print(f"Right CPM:       {right_cpm:.1f}")

    # Prompt deltas.
    prompt_deltas = signed_pair_deltas(left, right, max_abs_us=max_abs_us)

    # Multiple lag offsets for a more stable accidental-background estimate.
    lag_deltas_by_lag = []
    for lag in lags_us:
        shifted_right = right + int(lag)
        lag_deltas_by_lag.append(
            signed_pair_deltas(left, shifted_right, max_abs_us=max_abs_us)
        )

    lag_deltas_combined = np.concatenate(lag_deltas_by_lag) if lag_deltas_by_lag else np.array([], dtype=np.int64)

    # Histogram plot.
    hist_path = Path(f"{out_prefix}_signed_delta_histogram.png")
    make_histogram_plot(
        prompt_deltas=prompt_deltas,
        lag_deltas_combined=lag_deltas_combined,
        n_lags=len(lags_us),
        out_path=hist_path,
        hist_range_us=hist_range_us,
        bin_width_us=bin_width_us,
        title=f"Timing-difference histogram: {csv_path.name}",
    )

    # Window scan.
    summary = build_window_scan(
        prompt_deltas=prompt_deltas,
        lag_deltas_by_lag=lag_deltas_by_lag,
        center_us=center_us,
        thresholds=thresholds,
        duration_s=duration_s,
    )
    summary["lag_offsets_us"] = json.dumps(lags_us)

    summary_path = Path(f"{out_prefix}_window_scan_summary.csv")
    summary.to_csv(summary_path, index=False)

    scan_plot_path = Path(f"{out_prefix}_window_scan.png")
    make_window_scan_plot(summary, scan_plot_path)

    # Select the primary run-log window.
    if use_best_window:
        # Use Li & Ma z, not simple z, for selecting best window.
        best_idx = summary["li_ma_z"].idxmax()
        selected = summary.loc[best_idx].to_dict()
        selection_method = "best_li_ma_z_from_scan"
    else:
        selected = compute_counts_for_window(
            prompt_deltas=prompt_deltas,
            lag_deltas_by_lag=lag_deltas_by_lag,
            center_us=center_us,
            half_window_us=half_window_us,
            duration_s=duration_s,
        )
        selection_method = "preselected_half_window"

    # Accidental estimate from singles rates.  This is an independent sanity check,
    # not the primary background estimate.
    full_window_s = (2.0 * float(selected["half_window_us"])) / 1_000_000.0
    left_rate_s = len(left) / duration_s
    right_rate_s = len(right) / duration_s
    expected_accidentals_count_from_singles = left_rate_s * right_rate_s * full_window_s * duration_s
    expected_accidentals_cpm_from_singles = expected_accidentals_count_from_singles / duration_s * 60.0

    run_log = {
        # User/log metadata
        "run_id": run_id if run_id else csv_path.with_suffix("").name,
        "raw_csv_filename": csv_path.name,
        "raw_csv_path": str(csv_path),
        "detector_geometry": detector_geometry,
        "detector_separation": detector_separation,
        "source_position": source_position,
        "shielding_collimator_condition": shielding,
        "aluminum_blocks": aluminum,
        "detector_orientation": orientation,
        "notes": notes,

        # Time/duration
        **host_info,
        "board_start_t_us": t0_us,
        "board_end_t_us": t1_us,
        "duration_s": duration_s,
        "duration_min": duration_s / 60.0,
        "duration_h": duration_s / 3600.0,

        # Analysis configuration
        "selection_method": selection_method,
        "coincidence_window": f"{selected['center_us']:+.1f} ± {int(selected['half_window_us'])} µs",
        "center_us": float(selected["center_us"]),
        "half_window_us": int(selected["half_window_us"]),
        "lag_offsets_us": [int(x) for x in lags_us],
        "max_abs_us": int(max_abs_us),
        "hist_range_us": int(hist_range_us),
        "bin_width_us": int(bin_width_us),

        # Counts and rates
        "left_total_counts": int(len(left)),
        "right_total_counts": int(len(right)),
        "left_cpm": left_cpm,
        "right_cpm": right_cpm,
        "prompt_count": int(selected["prompt_count"]),
        "total_lag_count_across_lags": float(selected["total_lag_count_across_lags"]),
        "avg_lag_count": float(selected["avg_lag_count"]),
        "lag_count_std": float(selected["lag_count_std"]),
        "lag_counts_by_offset": selected["lag_counts_by_offset"],
        "net_count": float(selected["net_count"]),
        "prompt_cpm": float(selected["prompt_cpm"]),
        "lag_cpm": float(selected["lag_cpm"]),
        "net_cpm": float(selected["net_cpm"]),

        # Significance
        "approx_z": float(selected["approx_z"]),
        "li_ma_z": float(selected["li_ma_z"]),
        "li_ma_one_sided_p": float(selected["li_ma_one_sided_p"]),
        "li_ma_two_sided_p": float(selected["li_ma_two_sided_p"]),
        "background_exposure_alpha": float(selected["alpha"]),
        "n_lag_windows": int(selected["n_lags"]),

        # Independent accidental-rate sanity check
        "expected_accidentals_count_from_singles": expected_accidentals_count_from_singles,
        "expected_accidentals_cpm_from_singles": expected_accidentals_cpm_from_singles,
        "full_window_s_for_singles_estimate": full_window_s,

        # Cross-check fields from Arduino summary rows, if present
        **arduino_summary,
    }

    log_csv_path, log_json_path, log_txt_path = write_run_logs(run_log, out_prefix)

    # Print compact table.
    print()
    print("Window scan")
    print("-----------")
    print(summary[[
        "half_window_us",
        "prompt_count",
        "avg_lag_count",
        "net_count",
        "approx_z",
        "li_ma_z",
        "prompt_cpm",
        "lag_cpm",
        "net_cpm",
    ]].to_string(index=False, float_format=lambda x: f"{x:.3f}"))

    best = summary.loc[summary["li_ma_z"].idxmax()]
    print()
    print("Best simple window in this scan")
    print("-------------------------------")
    print(f"Center:       {center_us:+.1f} µs")
    print(f"Half-window:  ±{int(best['half_window_us'])} µs")
    print(f"Prompt:       {int(best['prompt_count'])}")
    print(f"Avg lag:      {best['avg_lag_count']:.2f}")
    print(f"Net:          {best['net_count']:.2f}")
    print(f"Simple z:     {best['approx_z']:.2f}")
    print(f"Li & Ma z:    {best['li_ma_z']:.2f}")
    print(f"Net CPM:      {best['net_cpm']:.3f}")

    print()
    print("Selected run-log window")
    print("-----------------------")
    print(f"Method:       {selection_method}")
    print(f"Center:       {selected['center_us']:+.1f} µs")
    print(f"Half-window:  ±{int(selected['half_window_us'])} µs")
    print(f"Prompt:       {int(selected['prompt_count'])}")
    print(f"Avg lag:      {selected['avg_lag_count']:.2f}")
    print(f"Net:          {selected['net_count']:.2f}")
    print(f"Simple z:     {selected['approx_z']:.2f}")
    print(f"Li & Ma z:    {selected['li_ma_z']:.2f}")
    print(f"One-sided p:  {selected['li_ma_one_sided_p']:.4g}")
    print(f"Two-sided p:  {selected['li_ma_two_sided_p']:.4g}")
    print(f"Net CPM:      {selected['net_cpm']:.4f}")

    print()
    print("Files written")
    print("-------------")
    print(hist_path)
    print(scan_plot_path)
    print(summary_path)
    print(log_csv_path)
    print(log_json_path)
    print(log_txt_path)

    return run_log


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Nano ESP32 / MightyOhm Geiger coincidence CSV logs and write a run log."
    )

    parser.add_argument("csv", help="CSV file produced by the serial logger.")

    parser.add_argument(
        "--out-prefix",
        default=None,
        help="Output filename prefix. Default: input filename without extension."
    )

    parser.add_argument(
        "--max-abs-us",
        type=int,
        default=1000,
        help="Maximum absolute L/R timing difference to compute, in µs. Default: 1000."
    )

    parser.add_argument(
        "--hist-range-us",
        type=int,
        default=100,
        help="Histogram x-axis range, ±this many µs. Default: 100."
    )

    parser.add_argument(
        "--bin-width-us",
        type=int,
        default=5,
        help="Histogram bin width in µs. Default: 5."
    )

    parser.add_argument(
        "--center-us",
        type=float,
        default=0.0,
        help="Coincidence-window center offset in µs. Default: 0."
    )

    parser.add_argument(
        "--half-window-us",
        type=int,
        default=10,
        help="Primary run-log coincidence half-window in µs. Default: 10."
    )

    parser.add_argument(
        "--use-best-window",
        action="store_true",
        help="Use the scan window with the highest Li & Ma significance for the run log. "
             "For unbiased reporting, prefer a preselected --half-window-us."
    )

    parser.add_argument(
        "--lags-us",
        default=",".join(str(x) for x in DEFAULT_LAGS_US),
        help="Comma-separated lag offsets in µs. Default: ±0.5M, ±1.0M, ..., ±3.0M."
    )

    parser.add_argument(
        "--thresholds-us",
        default=",".join(str(x) for x in DEFAULT_THRESHOLDS_US),
        help="Comma-separated half-window values for scan."
    )

    # Optional run metadata that cannot be inferred from the raw CSV.
    parser.add_argument("--run-id", default="", help="Run ID, e.g. P1, Q1, Run_03.")
    parser.add_argument("--geometry", default="", help="Detector geometry description.")
    parser.add_argument("--detector-separation", default="", help="Detector separation, e.g. '18 cm tube-to-tube'.")
    parser.add_argument("--source-position", default="", help="Source position, e.g. centered/off-axis.")
    parser.add_argument("--shielding", default="", help="Shielding/collimator condition.")
    parser.add_argument("--aluminum", default="", help="Aluminum blocks absent/present/description.")
    parser.add_argument("--orientation", default="", help="Detector orientation: direct / parallel / perpendicular / off-axis.")
    parser.add_argument("--notes", default="", help="Free-text notes: bumps, rewiring, source moved, display reset, etc.")

    args = parser.parse_args()

    analyze(
        csv_path=args.csv,
        out_prefix=args.out_prefix,
        max_abs_us=args.max_abs_us,
        hist_range_us=args.hist_range_us,
        bin_width_us=args.bin_width_us,
        center_us=args.center_us,
        half_window_us=args.half_window_us,
        use_best_window=args.use_best_window,
        lags_us=parse_int_list(args.lags_us),
        thresholds=parse_int_list(args.thresholds_us),
        run_id=args.run_id,
        detector_geometry=args.geometry,
        detector_separation=args.detector_separation,
        source_position=args.source_position,
        shielding=args.shielding,
        aluminum=args.aluminum,
        orientation=args.orientation,
        notes=args.notes,
    )


if __name__ == "__main__":
    main()
