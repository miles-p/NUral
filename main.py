import subprocess
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Run the full IMU-OptiTrack processing pipeline.")
    parser.add_argument("--input", help="Input file for processing (if needed).", default="data/recording.json")
    parser.add_argument("--mode", help="Mode to run: 'generate_test', 'train', 'test', or 'all'.", default="all")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if args.mode == "generate_test":
        print("Generating test data...")
        subprocess.run(["python3", "1_strip.py", "--input", args.input], check=True)
        subprocess.run(["python3", "2_pair_up.py", "--output", "data/test.csv"], check=True)
    if args.mode == "train":
        print("Training model...")
        subprocess.run(["python3", "2_pair_up.py", "--output", "data/paired.csv"], check=True)
        subprocess.run(["python3", "3_train.py"], check=True)
    if args.mode == "test":
        print("Testing model...")
        subprocess.run(["python3", "4_test.py"], check=True)
    if args.mode == "all":
        print("Running full pipeline...")
        subprocess.run(["python3", "1_strip.py", "--input", args.input], check=True)
        subprocess.run(["python3", "2_pair_up.py", "--output", "data/paired.csv"], check=True)
        subprocess.run(["python3", "3_train.py"], check=True)
        subprocess.run(["python3", "4_test.py"], check=True)
        subprocess.run(["python3", "-m", "tf2onnx.convert", "--keras", "models/model.keras", "--output", "models/model.onnx"], check=True)