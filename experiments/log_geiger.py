import argparse
import csv
import datetime as dt
import sys
import time

import serial # pip install pyserial


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Log Arduino Geiger serial data to CSV.")
    parser.add_argument("--port", required=True, help="Serial port, e.g. COM5, /dev/ttyACM0, /dev/cu.usbmodemXXXX")
    parser.add_argument("--baud", type=int, default=230400)
    parser.add_argument("--out", default="geiger_log.csv")
    args = parser.parse_args()

    with serial.Serial(args.port, args.baud, timeout=1) as ser, open(args.out, "a", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "host_time_utc",
            "host_time_unix",
            "record_type",
            "board_t_us",
            "detector",
            "pin",
            "prompt_matches",
            "delayed_matches",
            "left_cpm",
            "right_cpm",
            "prompt_cpm",
            "delayed_cpm",
            "total_left",
            "total_right",
            "total_prompt",
            "total_delayed",
            "dropped",
            "raw_line",
        ])
        f.flush()

        print(f"Logging {args.port} at {args.baud} baud to {args.out}")
        print("Press Ctrl+C to stop.")

        while True:
            raw = ser.readline()
            if not raw:
                continue

            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue

            host_iso = utc_now_iso()
            host_unix = time.time()

            # Print everything so you can watch live.
            print(line)

            # Comments/header lines from Arduino.
            if line.startswith("#"):
                writer.writerow([host_iso, host_unix, "COMMENT", "", "", "", "", "", "", "", "", "", "", "", "", "", "", line])
                f.flush()
                continue

            parts = line.split(",")

            if parts[0] == "E" and len(parts) >= 6:
                _, board_t_us, detector, pin, prompt_matches, delayed_matches = parts[:6]
                writer.writerow([
                    host_iso,
                    host_unix,
                    "E",
                    board_t_us,
                    detector,
                    pin,
                    prompt_matches,
                    delayed_matches,
                    "", "", "", "", "", "", "", "", "",
                    line,
                ])

            elif parts[0] == "S" and len(parts) >= 11:
                (
                    _,
                    board_t_us,
                    left_cpm,
                    right_cpm,
                    prompt_cpm,
                    delayed_cpm,
                    total_left,
                    total_right,
                    total_prompt,
                    total_delayed,
                    dropped,
                ) = parts[:11]

                writer.writerow([
                    host_iso,
                    host_unix,
                    "S",
                    board_t_us,
                    "", "", "", "",
                    left_cpm,
                    right_cpm,
                    prompt_cpm,
                    delayed_cpm,
                    total_left,
                    total_right,
                    total_prompt,
                    total_delayed,
                    dropped,
                    line,
                ])

            else:
                writer.writerow([host_iso, host_unix, "UNKNOWN", "", "", "", "", "", "", "", "", "", "", "", "", "", "", line])

            f.flush()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nStopped.")
        raise SystemExit(0)