
import ffmpeg

def trim_video(video_path: str, output_video_path: str, start_time: str, end_time: str) -> str:
    """Trims a video to the specified start and end times.

    Args:
        video_path: The path to the input video file.
        output_video_path: The path to save the trimmed video file.
        start_time: The start time for trimming (HH:MM:SS or seconds).
        end_time: The end time for trimming (HH:MM:SS or seconds).
    Returns:
        A status message indicating success or failure.
    """
    try:
        input_stream = ffmpeg.input(video_path, ss=start_time, to=end_time)
        # Attempt to copy codecs to avoid re-encoding if possible
        output_stream = input_stream.output(output_video_path, c='copy') 
        output_stream.run(capture_stdout=True, capture_stderr=True)
        return f"Video trimmed successfully (codec copy) to {output_video_path}"
    except ffmpeg.Error as e:
        error_message_copy = e.stderr.decode('utf8') if e.stderr else str(e)
        try:
            # Fallback to re-encoding if codec copy fails
            input_stream_recode = ffmpeg.input(video_path, ss=start_time, to=end_time)
            output_stream_recode = input_stream_recode.output(output_video_path)
            output_stream_recode.run(capture_stdout=True, capture_stderr=True)
            return f"Video trimmed successfully (re-encoded) to {output_video_path}"
        except ffmpeg.Error as e_recode:
            error_message_recode = e_recode.stderr.decode('utf8') if e_recode.stderr else str(e_recode)
            return f"Error trimming video. Copy attempt: {error_message_copy}. Re-encode attempt: {error_message_recode}"
    except FileNotFoundError:
        return f"Error: Input video file not found at {video_path}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
