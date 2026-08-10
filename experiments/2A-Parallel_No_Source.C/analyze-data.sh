#!/bin/bash

python3 ../analyze_geiger_run.py run-2a.csv \
  --out-prefix run_2A_parallel_no_source \
  --run-id 2A \
  --half-window-us 10 \
  --center-us 0 \
  --orientation "parallel" \
  --geometry "detectors arranged in parallel facing aluminum blocks, no source present" \
  --detector-separation "128.63mm" \
  --source-position "not present" \
  --shielding "none" \
  --aluminum "present" \
  --notes "source not present, establish baseline of background detections of simultaineous pairs minus false positives for parallel orientation"

  # Use: "none, direct / parallel / perpendicular / off-axis" for orientation
