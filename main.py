import argparse
import os
import sys
from tqdm import tqdm
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


def process_video(file_path, args, input_base_dir, output_base_dir):
    """
    Processes a single video file: rotates and/or compresses it based on the provided arguments.
    Maintains the directory structure within the output directory.
    """
    try:
        # Determine relative path to maintain directory structure
        relative_path = os.path.relpath(file_path, input_base_dir)
        relative_dir = os.path.dirname(relative_path)
        output_dir = os.path.join(output_base_dir, relative_dir)
        os.makedirs(output_dir, exist_ok=True)

        # Define output file paths
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        rotated_video_path = os.path.join(output_dir,
                                          f"{base_name}_rotated.mp4")
        compressed_video_path = os.path.join(output_dir,
                                             f"{base_name}_compressed.mp4")

        print(f"\nProcessing '{file_path}'...")

        # Initialize the final output path
        final_output_path = file_path

        # Rotate the video if rotation angle is provided
        if args.rot is not None:
            if not (0 <= args.rot < 360):
                print(
                    "  Error: Rotation angle must be between 0 and 360 degrees."
                )
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

            print(f"  Compressing to '{compressed_video_path}'...")
            try:
                compress_video(input_path=final_output_path,
                               output_path=compressed_video_path,
                               handbrake_cli_path=args.handbrake_path)
                final_output_path = compressed_video_path

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
            print(f"  Moving to '{args.output}'...")
            os.rename(final_output_path, args.output)
            final_output_path = args.output

        print(f"  Final output saved at: {final_output_path}")
        return True

    except Exception as e:
        print(f"  Unexpected error: {e}")
        return False


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
        help="Path for the final output video or directory. "
        "If input is a directory and output is not specified, an output directory named as the input folder with '_output' appended will be created."
    )

    args = parser.parse_args()

    # Validate input path
    if not os.path.exists(args.input):
        print(f"Error: Input path not found at {args.input}.")
        sys.exit(1)

    # Determine if input is a directory or a single file
    if os.path.isdir(args.input):
        input_base_dir = os.path.abspath(args.input)
        # Define output directory
        if args.output:
            output_base_dir = os.path.abspath(args.output)
        else:
            parent_dir = os.path.dirname(input_base_dir)
            input_folder_name = os.path.basename(input_base_dir)
            output_base_dir = os.path.join(parent_dir,
                                           f"{input_folder_name}_output")

        # Create output directory if it doesn't exist
        if not os.path.exists(output_base_dir):
            try:
                os.makedirs(output_base_dir, exist_ok=True)
                print(f"Created output directory: {output_base_dir}")
            except Exception as e:
                print(
                    f"Error creating output directory '{output_base_dir}': {e}"
                )
                sys.exit(1)

        # Get all video files in the input directory
        video_files = get_video_files(input_base_dir)
        if not video_files:
            print(
                f"No supported video files found in directory: {input_base_dir}"
            )
            sys.exit(1)

        print(
            f"Found {len(video_files)} video file(s) in '{input_base_dir}'. Starting processing..."
        )

        success_count = 0
        # Use tqdm to display a progress bar
        for video_file in tqdm(video_files,
                               desc="Processing Videos",
                               unit="video"):
            success = process_video(video_file, args, input_base_dir,
                                    output_base_dir)
            if success:
                success_count += 1

        print(
            f"\nProcessing completed: {success_count}/{len(video_files)} files processed successfully."
        )
        print(f"All output files are saved in: {output_base_dir}")

    else:
        # Single file processing
        input_file = os.path.abspath(args.input)
        if args.output:
            output_file = os.path.abspath(args.output)
        else:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_compressed.mp4" if args.compress else f"{base_name}_rotated.mp4"

        print(f"Processing single file: '{input_file}'")
        success = process_video(input_file, args, os.path.dirname(input_file),
                                os.path.dirname(output_file))
        if not success:
            sys.exit(1)
        print(f"Final output saved at: {output_file}")


if __name__ == "__main__":
    main()
