# Easy video tools with python

This Python script gives some tools to modify video in a easy way. It propose to rotates and/or compresses a video file, with options to customize the rotation angle, compression settings, and output path. If desired, it can apply only compression without rotation, allowing for flexible video processing.

## Installation

Before running the script, ensure you have python 3.6 or newer installed on your system and you need to install the required Python libraries. You can install them using the provided `requirements.txt` file.

```bash
pip install -r requirements.txt
```

- **HandBrakeCLI**: To enable video compression, install HandBrakeCLI from [HandBrake's website](https://handbrake.fr/downloads2.php) and provide its executable path if it differs from the default.

## Usage

To use the script, run it from the command line with the desired options.

```bash
python main.py [options]
```

## Options

- `-i`, `--input <file>`: Specify the path to the input video file. This option is required.

- `-r`, `--rot <angle>`: Specify the rotation angle (0-360 degrees) to rotate the video. If not specified, the rotation is skipped, and only compression is applied if enabled.

- `-c`, `--compress <bool>`: Set to `True` or `False` to enable or disable compression after rotation. Default is `True`. Compression is done using HandBrakeCLI, so ensure HandBrakeCLI is installed.

- `-hb`, `--handbrake-path <file>`: Specify the path to the `HandBrakeCLI` executable. Default is `"C:\Program Files\HandBrake\HandBrakeCLI.exe"` on Windows. Adjust this path if HandBrakeCLI is located elsewhere.

- `-o`, `--output <file>`: Specify the path of the final output video file. If not specified, the script will save the file with a default name based on the input file name and applied transformations.

- `-h`, `--help`: Display help information showing all command-line options.

## Example

To rotate a video by 90 degrees, compress it, and save it as `output_video.mp4`:

```bash
python main.py -i input_video.mp4 -r 90 -o output_video.mp4
```