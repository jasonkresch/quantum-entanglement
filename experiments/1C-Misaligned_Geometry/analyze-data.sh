#!/bin/bash

python3 ../analyze_geiger_run.py run-1c.csv \
  --out-prefix run_1C_misaligned_geometry \
  --run-id 1C \
  --half-window-us 10 \
  --center-us 0 \
  --orientation "off-axis" \
  --geometry "detectors horizontally separated in standard positions" \
  --detector-separation "66.86mm" \
  --source-position "higher than both detectors" \
  --shielding "none" \
  --aluminum "none" \
  --notes "source present and off-axis, higher than normal, reduces detection rate of simultaineous pairs over false positives"

  # Use: "none, direct / parallel / perpendicular / off-axis" for orientation
