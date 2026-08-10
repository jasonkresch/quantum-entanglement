#!/bin/bash

python3 ../analyze_geiger_run.py run-3b.csv \
  --out-prefix run_3B_perpendicular_no_blocks \
  --run-id 3B \
  --half-window-us 10 \
  --center-us 0 \
  --orientation "perpendicular" \
  --geometry "detectors arranged in perpendicular source present no aluminum blocks" \
  --detector-separation "126.94mm" \
  --source-position "not present" \
  --shielding "none" \
  --aluminum "none" \
  --notes "source not present, establish baseline of background detections of simultaineous pairs minus false positives for perpendicular orientation"

  # Use: "none, direct / parallel / perpendicular / off-axis" for orientation
