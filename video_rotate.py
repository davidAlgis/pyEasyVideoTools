import argparse
import cv2
import tqdm
import os
import math


def rotate_video(input_path, rotation_angle):
    # Open the input video
    video = cv2.VideoCapture(input_path)
    if not video.isOpened():
        print("Error: Could not open video.")
        return

    # Get video properties
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Calculate the rotation matrix and the new dimensions
    angle_rad = math.radians(rotation_angle)
    abs_cos = abs(math.cos(angle_rad))
    abs_sin = abs(math.sin(angle_rad))

    # Compute new width and height bounds
    new_width = int(height * abs_sin + width * abs_cos)
    new_height = int(height * abs_cos + width * abs_sin)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = f"{base_name}_rotated_{int(rotation_angle)}.mp4"
    out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))

    # Process each frame with a progress bar
    with tqdm.tqdm(total=frame_count, desc="Processing") as pbar:
        while True:
            ret, frame = video.read()
            if not ret:
                break

            # Get the rotation matrix
            center = (width / 2, height / 2)
            matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)

            # Adjust the rotation matrix to take into account translation
            matrix[0, 2] += (new_width / 2) - center[0]
            matrix[1, 2] += (new_height / 2) - center[1]

            # Apply the rotation
            rotated_frame = cv2.warpAffine(frame, matrix,
                                           (new_width, new_height))

            # Write the frame to the output video
            out.write(rotated_frame)
            pbar.update(1)

    # Release resources
    video.release()
    out.release()
    return output_path
