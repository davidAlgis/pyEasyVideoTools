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


def get_video_files(input_path):
    """
    Retrieves a list of video file paths from the input directory.
    Supports common video file extensions.
    """
    supported_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv',
                            '.mpeg', '.mpg')
    video_files = []

    for root, _, files in os.walk(input_path):
        for file in files:
            if file.lower().endswith(supported_extensions):
                video_files.append(os.path.join(root, file))

    return video_files


def process_video(file_path, args):
    """
    Processes a single video file: rotates and/or compresses it based on the provided arguments.
    """
    print(f"\nProcessing '{file_path}'...")

    # Initialize the final output path
    final_output_path = file_path

    # Rotate the video if rotation angle is provided
    if args.rot is not None:
        if not (0 <= args.rot < 360):
            print("Error: Rotation angle must be between 0 and 360 degrees.")
            return False

        print(f"  Rotating by {args.rot} degrees...")
        rotated_video_path = rotate_video(file_path, args.rot)

        # Check if rotation was successful
        if not os.path.exists(rotated_video_path):
            print("  Error: Video rotation failed.")
            return False

        final_output_path = rotated_video_path  # Update final output to the rotated video path

    # Compress the video if requested
    if args.compress:
        # Validate HandBrakeCLI path
        if not os.path.exists(args.handbrake_path):
            print(
                f"  Error: HandBrakeCLI not found at {args.handbrake_path}. Please ensure HandBrakeCLI is installed."
            )
            return False

        # Define the output path for compression
        if args.output:
            # If input is a directory, maintain directory structure in output
            if os.path.isdir(args.input):
                relative_path = os.path.relpath(file_path, args.input)
                output_path = os.path.join(args.output, relative_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                compressed_output_path = os.path.splitext(
                    output_path)[0] + "_compressed.mp4"
            else:
                # Single file input
                compressed_output_path = args.output
        else:
            # Default output path based on transformations
            base_name = os.path.splitext(final_output_path)[0]
            compressed_output_path = f"{base_name}_compressed.mp4"

        print(f"  Compressing to '{compressed_output_path}'...")
        try:
            compress_video(input_path=final_output_path,
                           output_path=compressed_output_path,
                           handbrake_cli_path=args.handbrake_path)
            final_output_path = compressed_output_path

            # Remove the intermediate rotated video if rotation was applied and compression was successful
            if args.rot is not None and os.path.exists(rotated_video_path):
                os.remove(rotated_video_path)
                print(
                    f"  Removed intermediate rotated video: {rotated_video_path}"
                )

        except Exception as e:
            print(f"  Error during compression: {e}")
            return False
    elif args.output:
        # If compression is not applied but output is specified, rename the rotated video
        if os.path.isdir(args.input):
            relative_path = os.path.relpath(file_path, args.input)
            output_path = os.path.join(args.output, relative_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            final_output_path = os.path.splitext(output_path)[0] + ".mp4"
        else:
            final_output_path = args.output

        os.rename(final_output_path, args.output)
        print(f"  Renamed to '{args.output}'.")

    print(f"  Final output saved at: {final_output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description=
        "Rotate videos by a specified angle and/or compress them using HandBrakeCLI. "
        "Supports single video files or directories containing multiple videos."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Path to the input video file or directory containing videos.")
    parser.add_argument("-r",
                        "--rot",
                        type=float,
                        help="Rotation angle between 0 and 360 degrees.")
    parser.add_argument(
        "-c",
        "--compress",
        type=str2bool,
        nargs='?',
        const=True,
        default=True,
        help="Whether to compress the video(s) (default: True).")
    parser.add_argument(
        "-hb",
        "--handbrake-path",
        type=str,
        default=r"C:\\Program Files\\HandBrake\\HandBrakeCLI.exe",
        help=
        "Path to the HandBrakeCLI executable (default: 'C:\\Program Files\\HandBrake\\HandBrakeCLI.exe')."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help=
        "Path for the final output video or directory. If input is a directory and output is not specified, compressed videos will be saved alongside the originals with '_compressed' suffix."
    )

    args = parser.parse_args()

    # Validate input path
    if not os.path.exists(args.input):
        print(f"Error: Input path not found at {args.input}.")
        sys.exit(1)

    # If input is a directory, get all video files
    if os.path.isdir(args.input):
        video_files = get_video_files(args.input)
        if not video_files:
            print(f"No supported video files found in directory: {args.input}")
            sys.exit(1)

        # If output directory is specified, create it if it doesn't exist
        if args.output:
            if not os.path.exists(args.output):
                try:
                    os.makedirs(args.output, exist_ok=True)
                    print(f"Created output directory: {args.output}")
                except Exception as e:
                    print(
                        f"Error creating output directory '{args.output}': {e}"
                    )
                    sys.exit(1)

        print(
            f"Found {len(video_files)} video file(s) in '{args.input}'. Starting processing..."
        )

        success_count = 0
        for video_file in video_files:
            success = process_video(video_file, args)
            if success:
                success_count += 1

        print(
            f"\nProcessing completed: {success_count}/{len(video_files)} files processed successfully."
        )

    else:
        # Single file processing
        success = process_video(args.input, args)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
