
import ffmpeg
import os

def stabilize_video(input_video_path: str, output_video_path: str) -> str:
    """Stabilizes a shaky video using a two-pass FFmpeg process.

    Args:
        input_video_path: Path to the source video file.
        output_video_path: Path to save the stabilized video.

    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"

    temp_trf_file = "transforms.trf" # Temporary file for stabilization data

    try:
        # Pass 1: Detect camera motion and generate transform data
        ffmpeg.input(input_video_path).output(
            '-', # Output to stdout
            vf='vidstabdetect=result={}:show=0'.format(temp_trf_file),
            f='null' # Output format null
        ).run(capture_stdout=True, capture_stderr=True)

        # Pass 2: Apply stabilization using the generated transform data
        ffmpeg.input(input_video_path).output(
            output_video_path,
            vf='vidstabtransform=input={}:zoom=0:smoothing=10'.format(temp_trf_file),
            acodec='copy' # Copy audio codec to avoid re-encoding
        ).run(capture_stdout=True, capture_stderr=True)

        return f"Video stabilized successfully and saved to {output_video_path}"
    except ffmpeg.Error as e:
        # Fallback if audio copy fails in pass 2
        try:
            ffmpeg.input(input_video_path).output(
                output_video_path,
                vf='vidstabtransform=input={}:zoom=0:smoothing=10'.format(temp_trf_file)
            ).run(capture_stdout=True, capture_stderr=True)
            return f"Video stabilized successfully (audio re-encoded) and saved to {output_video_path}"
        except ffmpeg.Error as e_recode:
            error_message = e_recode.stderr.decode('utf8') if e_recode.stderr else str(e_recode)
            return f"Error stabilizing video: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
    finally:
        # Clean up the temporary transform file
        if os.path.exists(temp_trf_file):
            os.remove(temp_trf_file)
