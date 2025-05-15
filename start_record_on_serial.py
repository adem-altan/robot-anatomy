import serial
import time
import pyrealsense2 as rs
from datetime import datetime

# --- Configuration ---
SERIAL_PORT = 'COM9'        # Update this to your Arduino's COM port
BAUD_RATE = 9600
RECORD_SECONDS = 57
FPS = 30
BAG_OUTPUT_FOLDER = 'recordings'  # Make sure this folder exists

# --- Wait for signal from Arduino ---
def wait_for_start_signal():
    print(f"Listening for 'START' from Arduino on {SERIAL_PORT}...")
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        while True:
            line = ser.readline().decode().strip()
            if line == "START":
                print("Received START signal from Arduino.")
                return

# --- Start RealSense recording ---
def record_bag(duration_sec=57):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{BAG_OUTPUT_FOLDER}/record_{timestamp}.bag"

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, FPS)
    #config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, FPS)
    config.enable_record_to_file(filename)

    print(f"Starting recording: {filename}")
    pipeline.start(config)

    time.sleep(duration_sec)

    pipeline.stop()
    print("Recording complete.")
    return filename

# --- Run everything ---
if __name__ == "__main__":
    wait_for_start_signal()
    recorded_file = record_bag(RECORD_SECONDS)
