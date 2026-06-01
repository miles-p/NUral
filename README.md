# how to use NUral
1. please don't.

# what to put where
1. put a json-extracted NBS file with RawSensors and Mocap data as `data/recording.json`
2. run [see below] and you'll get a `model.keras` file in `/models/`

# how to run
base command: `python3 main.py`

modes using `--mode **mode**`

## `generate_test`
turns NBS JSON into a paired-up file at `data/test.csv`. This can be used to compare IMU and Gyro to ground truth and get an error calculation of how shit your model is.

## `train`
pairs up and time-aligns an NBS JSON file, then trains a model which it will spit out to `models/model.keras`

## `test`
just tests the model you've made from `models/model.keras` against the test data you generated from `data/test.csv`

## `all`
loads NBS JSON, strips the data out of it, time-aligns it, trains a model, and tests the model against whatever data is in `data/test.csv`