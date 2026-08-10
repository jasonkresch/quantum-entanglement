#!/bin/bash

python3 ../analyze_geiger_run.py run-2b.csv \
  --out-prefix run_2B_parallel_no_blocks \
  --run-id 2B \
  --half-window-us 10 \
  --center-us 0 \
  --orientation "parallel" \
  --geometry "detectors arranged in parallel, source centered without aluminum blocks" \
  --detector-separation "128.63mm" \
  --source-position "centered" \
  --shielding "none" \
  --aluminum "none" \
  --notes "source present, establish baseline of simultaineous pairs minus false positives for parallel orientation"

  # Use: "none, direct / parallel / perpendicular / off-axis" for orientation
