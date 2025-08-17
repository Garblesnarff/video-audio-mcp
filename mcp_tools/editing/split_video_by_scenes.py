
import ffmpeg
import os
import re
import math

def split_video_by_scenes(input_video_path: str, output_directory: str, threshold: float = 0.08) -> str:
    """Splits a video into multiple clips based on scene changes.

    Args:
        input_video_path: Path to the source video file.
        output_directory: Directory where the split video clips will be saved.
        threshold: Scene change detection threshold (0.0 to 1.0). Lower values detect more changes. Default: 0.08.

    Returns:
        A status message indicating success or failure, or the path to the output directory.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"

    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)

    try:
        # Step 1: Detect scene changes using scdet filter
        # The output of scdet is written to stderr
        scene_detection_process = (
            ffmpeg
            .input(input_video_path)
            .filter('scdet', threshold=threshold)
            .output('-', format='null') # Output to null as we only need stderr
            .run_async(pipe_stderr=True)
        )
        _, stderr_bytes = scene_detection_process.communicate()
        stderr_str = stderr_bytes.decode('utf8')

        # Step 2: Parse scene change timestamps from stderr
        # Example output: [scdet @ 0x...] lavfi.scdet.score: 0.123456 lavfi.scdet.time: 1.234567
        scene_times = []
        for line in stderr_str.splitlines():
            match = re.search(r'lavfi.scdet.time: (\d+\.?\d*)', line)
            if match:
                scene_times.append(float(match.group(1)))
        
        # Add start and end of video to scene times if not already present
        if 0.0 not in scene_times:
            scene_times.insert(0, 0.0)
        
        # Get total duration of the video
        probe = ffmpeg.probe(input_video_path)
        total_duration = float(probe['format']['duration'])
        if total_duration not in scene_times:
            scene_times.append(total_duration)

        # Ensure timestamps are sorted and unique
        scene_times = sorted(list(set(scene_times)))

        if len(scene_times) < 2:
            return f"No significant scene changes detected with threshold {threshold}. No clips were split."

        # Step 3: Split video into clips based on detected scene changes
        for i in range(len(scene_times) - 1):
            start_time = scene_times[i]
            end_time = scene_times[i+1]
            
            # Skip very short segments that might be artifacts
            if (end_time - start_time) < 0.1: # e.g., less than 0.1 seconds
                continue

            output_filename = os.path.join(output_directory, f"scene_{i+1:03d}_{start_time:.2f}-{end_time:.2f}.mp4")
            
            try:
                # Use ss (start time) and t (duration) for trimming
                # Using -c copy to avoid re-encoding for speed, but might fail if not keyframe aligned
                ffmpeg.input(input_video_path, ss=start_time, to=end_time).output(output_filename, c='copy').run(capture_stdout=True, capture_stderr=True)
            except ffmpeg.Error as e:
                # Fallback to re-encoding if copy fails (e.g., not keyframe aligned)
                try:
                    ffmpeg.input(input_video_path, ss=start_time, to=end_time).output(output_filename).run(capture_stdout=True, capture_stderr=True)
                except ffmpeg.Error as e_recode:
                    error_message = e_recode.stderr.decode('utf8') if e_recode.stderr else str(e_recode)
                    return f"Error splitting scene {i+1} ({start_time:.2f}-{end_time:.2f}s): {error_message}"

        return f"Video split into scenes successfully. Clips saved to: {output_directory}"

    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error detecting scenes: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
