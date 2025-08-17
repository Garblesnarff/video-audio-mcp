
import ffmpeg
from ..utils import _run_ffmpeg_with_fallback

def set_video_bitrate(input_video_path: str, output_video_path: str, video_bitrate: str) -> str:
    """Sets the video bitrate of a video, attempting to copy the audio stream.
    Args:
        input_video_path: Path to the source video file.
        output_video_path: Path to save the video with the new video bitrate.
        video_bitrate: Target video bitrate (e.g., '1M', '2500k').
    Returns:
        A status message indicating success or failure.
    """
    primary_kwargs = {'video_bitrate': video_bitrate, 'acodec': 'copy'}
    fallback_kwargs = {'video_bitrate': video_bitrate} # Re-encode audio
    return _run_ffmpeg_with_fallback(input_video_path, output_video_path, primary_kwargs, fallback_kwargs)
