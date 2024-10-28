import argparse
import subprocess
import os
import sys


def compress_video(input_path, output_path, handbrake_cli_path):
    """
    Compresses a video using HandBrakeCLI.

    Parameters:
    - input_path: Path to the input video file.
    - output_path: Path to save the compressed video.
    - handbrake_cli_path: Path to the HandBrakeCLI executable.
    """
    # HandBrakeCLI command with desired presets
    command = [
        handbrake_cli_path,
        '-i',
        input_path,
        '-o',
        output_path,
        '--preset',
        'Fast 1080p30'  # You can choose different presets as needed
    ]

    print(f"Starting compression using HandBrakeCLI...")
    try:
        # Run the HandBrakeCLI command
        subprocess.run(command, check=True)
        print(f"Video compression complete. Saved as {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during compression: {e}")
        sys.exit(1)
