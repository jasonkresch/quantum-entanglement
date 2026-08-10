#!/bin/bash

python3 ../analyze_geiger_run_enhanced.py run-0c.csv \
  --out-prefix run_0C_no_source_vertically_stacked \
  --run-id 0C \
  --half-window-us 10 \
  --center-us 0 \
  --orientation "none" \
  --geometry "one on top of the other, vertically stacked" \
  --detector-separation "0mm" \
  --source-position "not present" \
  --shielding "none" \
  --aluminum "none" \
  --notes "no source present, to measure cosmic rays, and see that lagged detections are less than simultaineous pairs"

  # Use: "none, direct / parallel / perpendicular / off-axis" for orientation
