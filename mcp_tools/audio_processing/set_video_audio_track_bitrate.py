
import ffmpeg
from ..utils import _run_ffmpeg_with_fallback

def set_video_audio_track_bitrate(input_video_path: str, output_video_path: str, audio_bitrate: str) -> str:
    """Sets the audio bitrate of a video's audio track, attempting to copy the video stream.
    Args:
        input_video_path: Path to the source video file.
        output_video_path: Path to save the video with the new audio bitrate.
        audio_bitrate: Target audio bitrate (e.g., '128k', '192k').
    Returns:
        A status message indicating success or failure.
    """
    primary_kwargs = {'audio_bitrate': audio_bitrate, 'vcodec': 'copy'}
    fallback_kwargs = {'audio_bitrate': audio_bitrate} # Re-encode video
    return _run_ffmpeg_with_fallback(input_video_path, output_video_path, primary_kwargs, fallback_kwargs)
