#!/bin/bash

python3 ../analyze_geiger_run.py run-2c.csv \
  --out-prefix run_2C_parallel \
  --run-id 2C \
  --half-window-us 10 \
  --center-us 0 \
  --orientation "parallel" \
  --geometry "detectors arranged in parallel facing aluminum blocks, source centered" \
  --detector-separation "128.63mm" \
  --source-position "centered" \
  --shielding "none" \
  --aluminum "present" \
  --notes "source present, establish baseline of simultaineous pairs minus false positives for parallel orientation"

  # Use: "none, direct / parallel / perpendicular / off-axis" for orientation
