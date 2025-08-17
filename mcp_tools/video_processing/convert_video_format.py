
import ffmpeg
from ..utils import _run_ffmpeg_with_fallback

def convert_video_format(input_video_path: str, output_video_path: str, target_format: str) -> str:
    """Converts a video file to the specified target format, attempting to copy codecs first.
    Args:
        input_video_path: Path to the source video file.
        output_video_path: Path to save the converted video file.
        target_format: Desired output video format (e.g., 'mp4', 'mov', 'avi').
    Returns:
        A status message indicating success or failure.
    """
    primary_kwargs = {'format': target_format, 'vcodec': 'copy', 'acodec': 'copy'}
    fallback_kwargs = {'format': target_format} # Re-encode both streams
    return _run_ffmpeg_with_fallback(input_video_path, output_video_path, primary_kwargs, fallback_kwargs)
