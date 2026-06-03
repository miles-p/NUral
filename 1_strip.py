import argparse
import csv
import json
from pathlib import Path


def iter_records(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def iter_imu_rows(path):
    for rec in iter_records(path):
        if rec.get("type") != "message.platform.RawSensors":
            continue
        data = rec.get("data", {})
        accel = data.get("accelerometer", {}) or {}
        gyro = data.get("gyroscope", {}) or {}
        yield {
            "record_timestamp": rec.get("timestamp"),
            "accel_x": accel.get("x"),
            "accel_y": accel.get("y"),
            "accel_z": accel.get("z"),
            "gyro_x": gyro.get("x"),
            "gyro_y": gyro.get("y"),
            "gyro_z": gyro.get("z"),
        }


def iter_optitrack_rows(path):
    for rec in iter_records(path):
        if rec.get("type") != "message.input.MotionCapture":
            continue
        data = rec.get("data", {})
        rigid_bodies = data.get("rigid_bodies", []) or []
        for body in rigid_bodies:
            position = body.get("position", {}) or {}
            rotation = body.get("rotation", {}) or {}
            yield {
                "record_timestamp": rec.get("timestamp"),
                "pos_x": position.get("x"),
                "pos_y": position.get("y"),
                "pos_z": position.get("z"),
                "rot_x": rotation.get("x"),
                "rot_y": rotation.get("y"),
                "rot_z": rotation.get("z"),
                "rot_t": rotation.get("t"),
            }


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args():
    parser = argparse.ArgumentParser(description="Extract IMU and OptiTrack data.")
    parser.add_argument(
        "--input",
        default="data/recording.json",
        help="Path to the JSONL recording file.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to write output CSV files.",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Optional prefix for output filenames.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    prefix = args.prefix

    imu_rows = list(iter_imu_rows(input_path))
    optitrack_rows = list(iter_optitrack_rows(input_path))

    imu_path = output_dir / f"{prefix}data/imu.csv"
    optitrack_path = output_dir / f"{prefix}data/optitrack.csv"

    if imu_rows:
        write_csv(
            imu_path,
            imu_rows,
            fieldnames=list(imu_rows[0].keys()),
        )

    if optitrack_rows:
        write_csv(
            optitrack_path,
            optitrack_rows,
            fieldnames=list(optitrack_rows[0].keys()),
        )

    print(f"Wrote {len(imu_rows)} IMU rows to {imu_path}")
    print(f"Wrote {len(optitrack_rows)} OptiTrack rows to {optitrack_path}")


if __name__ == "__main__":
    main()