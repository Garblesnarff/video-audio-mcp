
import ffmpeg
from ..utils import _run_ffmpeg_with_fallback

def set_video_codec(input_video_path: str, output_video_path: str, video_codec: str) -> str:
    """Sets the video codec of a video, attempting to copy the audio stream.
    Args:
        input_video_path: Path to the source video file.
        output_video_path: Path to save the video with the new video codec.
        video_codec: Target video codec (e.g., 'libx264', 'libx265', 'vp9').
    Returns:
        A status message indicating success or failure.
    """
    primary_kwargs = {'vcodec': video_codec, 'acodec': 'copy'}
    fallback_kwargs = {'vcodec': video_codec} # Re-encode audio
    return _run_ffmpeg_with_fallback(input_video_path, output_video_path, primary_kwargs, fallback_kwargs)
