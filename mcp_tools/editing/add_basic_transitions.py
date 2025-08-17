
import ffmpeg
import os
from ..utils import _get_media_properties

def add_basic_transitions(video_path: str, output_video_path: str, transition_type: str, duration_seconds: float) -> str:
    """Adds basic fade transitions to the beginning or end of a video.

    Args:
        video_path: Path to the input video file.
        output_video_path: Path to save the video with the transition.
        transition_type: Type of transition. Options: 'fade_in', 'fade_out'.
                         (Note: 'crossfade_from_black' is like 'fade_in', 'crossfade_to_black' is like 'fade_out')
        duration_seconds: Duration of the fade effect in seconds.
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(video_path):
        return f"Error: Input video file not found at {video_path}"
    if duration_seconds <= 0:
        return "Error: Transition duration must be positive."

    try:
        props = _get_media_properties(video_path)
        video_total_duration = props['duration']

        if duration_seconds > video_total_duration:
            return f"Error: Transition duration ({duration_seconds}s) cannot exceed video duration ({video_total_duration}s)."

        input_stream = ffmpeg.input(video_path)
        video_stream = input_stream.video
        audio_stream = input_stream.audio
        
        processed_video = None

        if transition_type == 'fade_in' or transition_type == 'crossfade_from_black':
            processed_video = video_stream.filter('fade', type='in', start_time=0, duration=duration_seconds)
        elif transition_type == 'fade_out' or transition_type == 'crossfade_to_black':
            fade_start_time = video_total_duration - duration_seconds
            processed_video = video_stream.filter('fade', type='out', start_time=fade_start_time, duration=duration_seconds)
        else:
            return f"Error: Unsupported transition_type '{transition_type}'. Supported: 'fade_in', 'fade_out'."

        # Attempt to copy audio, fallback to re-encoding if necessary
        output_streams = []
        if props['has_video']:
            output_streams.append(processed_video)
        if props['has_audio']:
            output_streams.append(audio_stream) # Audio is passed through without fade
        else: # Video only
            pass
        
        if not output_streams:
            return "Error: No suitable video or audio streams found to apply transition."

        try:
            ffmpeg.output(*output_streams, output_video_path, acodec='copy').run(capture_stdout=True, capture_stderr=True)
            return f"Transition '{transition_type}' applied successfully (audio copied). Output: {output_video_path}"
        except ffmpeg.Error as e_acopy:
            # Fallback: re-encode audio (or just output video if no audio originally)
            try:
                ffmpeg.output(*output_streams, output_video_path).run(capture_stdout=True, capture_stderr=True)
                return f"Transition '{transition_type}' applied successfully (audio re-encoded/processed). Output: {output_video_path}"
            except ffmpeg.Error as e_recode:
                err_acopy = e_acopy.stderr.decode('utf8') if e_acopy.stderr else str(e_acopy)
                err_recode = e_recode.stderr.decode('utf8') if e_recode.stderr else str(e_recode)
                return f"Error applying transition. Audio copy failed: {err_acopy}. Full re-encode failed: {err_recode}."

    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error applying basic transition: {error_message}"
    except ValueError as e: # For _parse_time or duration checks
        return f"Error with input values: {str(e)}"
    except RuntimeError as e: # For _get_media_properties error
        return f"Runtime error during transition processing: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred in add_basic_transitions: {str(e)}"
