
import ffmpeg
from ..utils import _run_ffmpeg_with_fallback

def set_video_audio_track_channels(input_video_path: str, output_video_path: str, audio_channels: int) -> str:
    """Sets the number of audio channels of a video's audio track, attempting to copy the video stream.
    Args:
        input_video_path: Path to the source video file.
        output_video_path: Path to save the video with the new audio channel layout.
        audio_channels: Number of audio channels (1 for mono, 2 for stereo).
    Returns:
        A status message indicating success or failure.
    """
    primary_kwargs = {'ac': audio_channels, 'vcodec': 'copy'} # ac for audio channels
    fallback_kwargs = {'ac': audio_channels} # Re-encode video
    return _run_ffmpeg_with_fallback(input_video_path, output_video_path, primary_kwargs, fallback_kwargs)
