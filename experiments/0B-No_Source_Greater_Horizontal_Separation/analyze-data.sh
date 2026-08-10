#!/bin/bash

python3 ../analyze_geiger_run.py run-0d.csv \
  --out-prefix run_0B_no_source_greater_horizontal_separation \
  --run-id 0B \
  --half-window-us 10 \
  --center-us 0 \
  --orientation "none" \
  --geometry "detectors horizontally separated as far as possible" \
  --detector-separation "273.40mm" \
  --source-position "not present" \
  --shielding "none" \
  --aluminum "none" \
  --notes "no source present, to minimize background cosmic rays, and see that lagged detections approximately equal simultaineous pairs"

  # Use: "none, direct / parallel / perpendicular / off-axis" for orientation
