import argparse
import csv
from pathlib import Path


IMU_FIELDS = [
	"accel_x",
	"accel_y",
	"accel_z",
	"gyro_x",
	"gyro_y",
	"gyro_z",
]

OPTITRACK_FIELDS = [
	"pos_x",
	"pos_y",
	"pos_z",
	"rot_x",
	"rot_y",
	"rot_z",
	"rot_t",
]


def parse_float(value):
	if value is None:
		return None
	if value == "":
		return None
	try:
		return float(value)
	except ValueError:
		return None


def read_csv_rows(path, expected_fields):
	rows = []
	with open(path, "r", encoding="utf-8", newline="") as f:
		reader = csv.DictReader(f)
		for row in reader:
			timestamp_raw = row.get("record_timestamp")
			if timestamp_raw in (None, ""):
				continue
			try:
				timestamp = int(timestamp_raw)
			except ValueError:
				continue
			parsed = {"record_timestamp": timestamp}
			for field in expected_fields:
				parsed[field] = parse_float(row.get(field))
			rows.append(parsed)
	rows.sort(key=lambda r: r["record_timestamp"])
	return rows


def find_closest_by_timestamp(optitrack_rows, start_index, target_timestamp):
	idx = start_index
	while idx + 1 < len(optitrack_rows) and optitrack_rows[idx + 1]["record_timestamp"] <= target_timestamp:
		idx += 1

	best_idx = idx
	best_dt = optitrack_rows[idx]["record_timestamp"] - target_timestamp

	if idx + 1 < len(optitrack_rows):
		next_dt = optitrack_rows[idx + 1]["record_timestamp"] - target_timestamp
		if abs(next_dt) < abs(best_dt):
			best_idx = idx + 1
			best_dt = next_dt

	return best_idx, best_dt


def pair_up(imu_rows, optitrack_rows, max_gap_us=None):
	if not imu_rows or not optitrack_rows:
		return []

	aligned = []
	opti_idx = 0
	for imu in imu_rows:
		target_ts = imu["record_timestamp"]
		opti_idx, dt = find_closest_by_timestamp(optitrack_rows, opti_idx, target_ts)
		if max_gap_us is not None and abs(dt) > max_gap_us:
			continue
		aligned.append((imu, optitrack_rows[opti_idx], dt))
	return aligned


def compute_deltas(aligned_rows):
	output = []
	prev_imu = {field: None for field in IMU_FIELDS}
	prev_opti = {field: None for field in OPTITRACK_FIELDS}

	for imu, opti, dt in aligned_rows:
		row = {
			"record_timestamp": imu["record_timestamp"],
		}

		for field in IMU_FIELDS:
			value = imu.get(field)
			row[field] = value
			prev_value = prev_imu.get(field)
			row[f"d_{field}"] = value - prev_value if value is not None and prev_value is not None else None
			if value is not None:
				prev_imu[field] = value

		for field in OPTITRACK_FIELDS:
			value = opti.get(field)
			row[field] = value
			prev_value = prev_opti.get(field)
			row[f"d_{field}"] = value - prev_value if value is not None and prev_value is not None else None
			if value is not None:
				prev_opti[field] = value

		output.append(row)

	return output


def write_csv(path, rows):
	if not rows:
		return
	path.parent.mkdir(parents=True, exist_ok=True)
	fieldnames = list(rows[0].keys())
	with open(path, "w", encoding="utf-8", newline="") as f:
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(rows)


def parse_args():
	parser = argparse.ArgumentParser(description="Time-align IMU and OptiTrack streams.")
	parser.add_argument("--imu", default="data/imu.csv", help="Path to IMU CSV.")
	parser.add_argument("--optitrack", default="data/optitrack.csv", help="Path to OptiTrack CSV.")
	parser.add_argument("--output", default="data/paired.csv", help="Output CSV path.")
	parser.add_argument(
		"--max-gap-us",
		type=int,
		default=None,
		help="Optional maximum alignment gap in microseconds.",
	)
	return parser.parse_args()


def main():
	args = parse_args()
	imu_rows = read_csv_rows(Path(args.imu), IMU_FIELDS)
	optitrack_rows = read_csv_rows(Path(args.optitrack), OPTITRACK_FIELDS)
	aligned = pair_up(imu_rows, optitrack_rows, max_gap_us=args.max_gap_us)
	delta_rows = compute_deltas(aligned)
	write_csv(Path(args.output), delta_rows)

	print(f"Paired {len(delta_rows)} rows into {args.output}")


if __name__ == "__main__":
	main()
