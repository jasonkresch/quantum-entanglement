#!/bin/bash

python3 ../analyze_geiger_run.py run-3a.csv \
  --out-prefix run_3A_perpendicular_no_source \
  --run-id 3A \
  --half-window-us 10 \
  --center-us 0 \
  --orientation "perpendicular" \
  --geometry "detectors arranged in perpendicular facing aluminum blocks, no source present" \
  --detector-separation "126.94mm" \
  --source-position "not present" \
  --shielding "none" \
  --aluminum "present" \
  --notes "source not present, establish baseline of background detections of simultaineous pairs minus false positives for perpendicular orientation"

  # Use: "none, direct / parallel / perpendicular / off-axis" for orientation
