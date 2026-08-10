#!/bin/bash

python3 ../analyze_geiger_run.py "run-0a.csv" \
  --out-prefix run_0A_no_source_medium_horizontal_separation \
  --run-id "0A" \
  --half-window-us "10" \
  --center-us "0" \
  --orientation "none" \
  --geometry "medium separation" \
  --detector-separation "67.18mm" \
  --source-position "not present" \
  --shielding "none" \
  --aluminum "none" \
  --notes "no source present, to measure baseline background, and cosmic rays, ensure electronics working, and that lagged detections approximately cancel out simultaineous pairs"

  # Use: "none, direct / parallel / perpendicular / off-axis" for orientation
