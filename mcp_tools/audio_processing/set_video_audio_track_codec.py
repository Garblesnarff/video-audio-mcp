
import ffmpeg
from ..utils import _run_ffmpeg_with_fallback

def set_video_audio_track_codec(input_video_path: str, output_video_path: str, audio_codec: str) -> str:
    """Sets the audio codec of a video's audio track, attempting to copy the video stream.
    Args:
        input_video_path: Path to the source video file.
        output_video_path: Path to save the video with the new audio codec.
        audio_codec: Target audio codec (e.g., 'aac', 'mp3').
    Returns:
        A status message indicating success or failure.
    """
    primary_kwargs = {'acodec': audio_codec, 'vcodec': 'copy'}
    fallback_kwargs = {'acodec': audio_codec} # Re-encode video
    return _run_ffmpeg_with_fallback(input_video_path, output_video_path, primary_kwargs, fallback_kwargs)
