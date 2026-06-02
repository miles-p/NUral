import tensorflow as tf
import csv

with open("data/test.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    data = list(reader)

model = tf.keras.models.load_model("models/model.keras")

for row in data[1:]:
    accel_x = float(row[1])
    accel_y = float(row[3])
    accel_z = float(row[5])
    gyro_x = float(row[7])
    gyro_y = float(row[9])
    gyro_z = float(row[11])

    if '' in [accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, row[14], row[16], row[18], row[20], row[22], row[24], row[26]]:
        print("Skipping row with missing data")
        continue

    ground_truth_d_pos_x = float(row[14])
    ground_truth_d_pos_y = float(row[16])
    ground_truth_d_pos_z = float(row[18])
    ground_truth_d_rot_x = float(row[20])
    ground_truth_d_rot_y = float(row[22])
    ground_truth_d_rot_z = float(row[24])
    ground_truth_d_rot_t = float(row[26])

    input_tensor = tf.constant([[accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z]])
    output = model(input_tensor)

    print(f"Input: accel=({accel_x}, {accel_y}, {accel_z}), gyro=({gyro_x}, {gyro_y}, {gyro_z})")
    print(f"Output: {output.numpy()}")

    # compute error
    pred_pos_x, pred_pos_y, pred_pos_z, pred_rot_x, pred_rot_y, pred_rot_z = output.numpy()[0]
    pos_error = ((pred_pos_x - ground_truth_d_pos_x) ** 2 + (pred_pos_y - ground_truth_d_pos_y) ** 2 + (pred_pos_z - ground_truth_d_pos_z) ** 2) ** 0.5
    rot_error = ((pred_rot_x - ground_truth_d_rot_x) ** 2 + (pred_rot_y - ground_truth_d_rot_y) ** 2 + (pred_rot_z - ground_truth_d_rot_z) ** 2) ** 0.5

    print(f"Position error: {pos_error}, Rotation error: {rot_error}")
    print("-" * 50)