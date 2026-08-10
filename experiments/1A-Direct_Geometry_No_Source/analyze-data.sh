#!/bin/bash

python3 ../analyze_geiger_run.py run-1a.csv \
  --out-prefix run_1A_direct_geometry_no_source \
  --run-id 1A \
  --half-window-us 10 \
  --center-us 0 \
  --orientation "none" \
  --geometry "detectors horizontally separated in standard positions with no source" \
  --detector-separation "66.86mm" \
  --source-position "not present" \
  --shielding "none" \
  --aluminum "none" \
  --notes "source not present, establish baseline of simultaineous pairs minus false positives"

  # Use: "none, direct / parallel / perpendicular / off-axis" for orientation
