#!/bin/bash

python3 ../analyze_geiger_run.py run-1b.csv \
  --out-prefix run_1B_direct_geometry \
  --run-id 1B \
  --half-window-us 10 \
  --center-us 0 \
  --orientation "direct" \
  --geometry "detectors horizontally separated in standard positions" \
  --detector-separation "66.86mm" \
  --source-position "centered" \
  --shielding "none" \
  --aluminum "none" \
  --notes "source present and centered, maximizes detection rate of simultaineous pairs over false positives"

  # Use: "none, direct / parallel / perpendicular / off-axis" for orientation
