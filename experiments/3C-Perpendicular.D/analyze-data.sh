#!/bin/bash

python3 ../analyze_geiger_run.py run-3c.csv \
  --out-prefix run_3C_perpendicular \
  --run-id 3C \
  --half-window-us 10 \
  --center-us 0 \
  --orientation "perpendicular" \
  --geometry "detectors arranged in perpendicular facing aluminum blocks, source centered" \
  --detector-separation "104.47mm" \
  --source-position "centered" \
  --shielding "none" \
  --aluminum "present" \
  --notes "source present, establish baseline of simultaineous pairs minus false positives for perpendicular orientation"

  # Use: "none, direct / parallel / perpendicular / off-axis" for orientation
