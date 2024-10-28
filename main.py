import argparse
import os
import sys
from video_rotate import rotate_video
from video_compress_handbrake import compress_video


def str2bool(v):
    """
    Converts a string argument to a boolean value.
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main():
    parser = argparse.ArgumentParser(
        description=
        "Rotate a video by a specified angle and optionally compress it using HandBrakeCLI."
    )
    parser.add_argument("-i",
                        "--input",
                        type=str,
                        required=True,
                        help="Path to the input video file.")
    parser.add_argument("-r",
                        "--rot",
                        type=float,
                        required=True,
                        help="Rotation angle between 0 and 360 degrees.")
    parser.add_argument(
        "-c",
        "--compress",
        type=str2bool,
        nargs='?',
        const=True,
        default=True,
        help="Whether to compress the video after rotation (default: True).")
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        default=r"C:\\Program Files\\HandBrake\\HandBrakeCLI.exe",
        help=
        "Path to the HandBrakeCLI executable (default: 'C:\\Program Files\\HandBrake\\HandBrakeCLI.exe')."
    )

    args = parser.parse_args()

    # Validate input video path
    if not os.path.exists(args.input):
        print(f"Error: Input video file not found at {args.input}.")
        sys.exit(1)

    # Validate rotation angle
    if not (0 <= args.rot < 360):
        print("Error: Rotation angle must be between 0 and 360 degrees.")
        sys.exit(1)

    # Rotate the video
    print(f"Starting rotation of '{args.input}' by {args.rot} degrees...")
    rotated_video_path = rotate_video(args.input, args.rot)

    # Check if rotation was successful
    if not os.path.exists(rotated_video_path):
        print("Error: Video rotation failed.")
        sys.exit(1)

    final_output_path = rotated_video_path  # Initialize final output path

    # Compress the video if requested
    if args.compress:
        # Validate HandBrakeCLI path
        if not os.path.exists(args.path):
            print(
                f"Error: HandBrakeCLI not found at {args.path}. Please ensure HandBrakeCLI is installed."
            )
            sys.exit(1)

        # Define the compressed video output path
        base_name = os.path.splitext(rotated_video_path)[0]
        compressed_output_path = f"{base_name}_compressed.mp4"

        print(f"Starting compression of '{rotated_video_path}'...")
        try:
            compress_video(input_path=rotated_video_path,
                           output_path=compressed_output_path,
                           handbrake_cli_path=args.path)
            final_output_path = compressed_output_path

            # Remove the intermediate rotated video
            os.remove(rotated_video_path)
            print(f"Removed intermediate rotated video: {rotated_video_path}")

        except Exception as e:
            print(f"Error during compression: {e}")
            sys.exit(1)

    print(f"Final output saved at: {final_output_path}")


if __name__ == "__main__":
    main()
