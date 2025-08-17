
import ffmpeg
from ..utils import _run_ffmpeg_with_fallback

def set_video_frame_rate(input_video_path: str, output_video_path: str, frame_rate: int) -> str:
    """Sets the frame rate of a video, attempting to copy the audio stream.
    Args:
        input_video_path: Path to the source video file.
        output_video_path: Path to save the video with the new frame rate.
        frame_rate: Target video frame rate (e.g., 24, 30, 60).
    Returns:
        A status message indicating success or failure.
    """
    primary_kwargs = {'r': frame_rate, 'acodec': 'copy'}
    fallback_kwargs = {'r': frame_rate} # Re-encode audio
    return _run_ffmpeg_with_fallback(input_video_path, output_video_path, primary_kwargs, fallback_kwargs)
