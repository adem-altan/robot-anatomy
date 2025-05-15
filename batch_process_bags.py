import pyrealsense2 as rs
import numpy as np
import pandas as pd
import os

# CONFIGURATION
DATA_DIR = "data"
RESULTS_DIR = os.path.join(DATA_DIR, "results")
START_DISTANCE = 0.1
ACTUATOR_SPEED_MPS = 0.057
FPS = 30

os.makedirs(RESULTS_DIR, exist_ok=True)

def process_bag_to_csv(bag_file_path, output_csv_path):
    pipeline = rs.pipeline()
    config = rs.config()

    try:
        rs.config.enable_device_from_file(config, bag_file_path, repeat_playback=False)
        # ⛔ DO NOT manually enable any streams
        pipeline.start(config)
    except RuntimeError as e:
        print(f"❌ Cannot open {bag_file_path}: {e}")
        return

    profile = pipeline.get_active_profile()
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()

    results = []
    frame_index = 0

    try:
        while True:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            if not depth_frame:
                continue

            depth_image = np.asanyarray(depth_frame.get_data()).astype(float) * depth_scale
            valid_pixels = depth_image[depth_image > 0]

            expected_distance = START_DISTANCE + (frame_index / FPS) * ACTUATOR_SPEED_MPS
            mean_depth = np.mean(valid_pixels) if valid_pixels.size > 0 else np.nan
            completeness = (valid_pixels.size / depth_image.size) * 100
            rmse = np.sqrt(np.mean((valid_pixels - expected_distance) ** 2)) if valid_pixels.size > 0 else np.nan

            results.append({
                "frame_index": frame_index,
                "expected_distance_m": round(expected_distance, 3),
                "mean_depth_m": round(mean_depth, 3),
                "rmse_mm": round(rmse * 1000, 2),
                "completeness_percent": round(completeness, 2)
            })

            frame_index += 1

    except RuntimeError:
        pass  # End of file reached
    finally:
        pipeline.stop()

    df = pd.DataFrame(results)
    df.to_csv(output_csv_path, index=False)
    print(f"✅ Processed and saved: {output_csv_path}")

def batch_process_by_folder():
    for folder_name in os.listdir(DATA_DIR):
        folder_path = os.path.join(DATA_DIR, folder_name)
        if not os.path.isdir(folder_path) or folder_name == "results":
            continue

        bag_files = [f for f in os.listdir(folder_path) if f.endswith(".bag")]
        if not bag_files:
            print(f"⚠️ No .bag file found in {folder_name}")
            continue

        bag_path = os.path.join(folder_path, bag_files[0])
        output_path = os.path.join(RESULTS_DIR, f"{folder_name}_results.csv")
        print(f"📂 Processing {folder_name}: {os.path.basename(bag_path)}")
        process_bag_to_csv(bag_path, output_path)

if __name__ == "__main__":
    batch_process_by_folder()
