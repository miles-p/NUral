import tensorflow as tf
import csv
import argparse

# training defaults
epochs = 100
batch_size = 32

def args():
    parser = argparse.ArgumentParser(description="Train a model to predict position and rotation changes from IMU data.")
    parser.add_argument("--epochs", type=int, default=epochs, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=batch_size, help="Training batch size")
    return parser.parse_args()

args = args()

## pull all the data in

with open("data/paired.csv", "r", encoding="utf-8") as f:
    data = f.readlines()

reader = csv.DictReader(data)
rows = list(reader)

## read "accel_x", "accel_y", "accel_z" as input, and "pos_x", "pos_y", "pos_z", "rot_x", "rot_y", "rot_z" as output

inputs = []
outputs = []

for row in rows:
    if (row["accel_x"] == "" or row["accel_y"] == "" or row["accel_z"] == "" or
        row["gyro_x"] == "" or row["gyro_y"] == "" or row["gyro_z"] == "" or
        row["d_pos_x"] == "" or row["d_pos_y"] == "" or row["d_pos_z"] == "" or
        row["d_rot_x"] == "" or row["d_rot_y"] == "" or row["d_rot_z"] == ""):
        continue
    inputs.append([float(row["accel_x"]), float(row["accel_y"]), float(row["accel_z"]), float(row["gyro_x"]), float(row["gyro_y"]), float(row["gyro_z"])])
    outputs.append([float(row["d_pos_x"]), float(row["d_pos_y"]), float(row["d_pos_z"]), float(row["d_rot_x"]), float(row["d_rot_y"]), float(row["d_rot_z"])])

inputs = tf.stack(inputs)
outputs = tf.stack(outputs)

model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(6)
])

model.compile(
    optimizer='adam',
    loss='mse'
)

model.fit(inputs, outputs, epochs=args.epochs, batch_size=args.batch_size)

print("Training complete!")

model.save("models/model.keras")