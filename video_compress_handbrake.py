import subprocess
import sys


def compress_video(input_path, output_path, handbrake_cli_path):
    """
    Compresses a video using HandBrakeCLI with optimized settings and suppressed logs.

    Parameters:
    - input_path: Path to the input video file.
    - output_path: Path to save the compressed video.
    - handbrake_cli_path: Path to the HandBrakeCLI executable.
    """
    # HandBrakeCLI command with custom settings for quality and compression
    command = [
        handbrake_cli_path,
        '-i',
        input_path,
        '-o',
        output_path,
        '--preset',
        'Fast 1080p30',  # Base preset
        '--quality',
        '25',  # Constant Quality RF level
        '--encoder-preset',
        'slower'  # Optimize encoding time for better compression
    ]

    print("Starting compression using HandBrakeCLI...")
    try:
        # Run the HandBrakeCLI command and suppress logs
        subprocess.run(command,
                       check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        print(f"Video compression complete. Saved as {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during compression: {e}")
        sys.exit(1)
