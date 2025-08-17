
import ffmpeg
from ..utils import _run_ffmpeg_with_fallback

def set_video_audio_track_sample_rate(input_video_path: str, output_video_path: str, audio_sample_rate: int) -> str:
    """Sets the audio sample rate of a video's audio track, attempting to copy the video stream.
    Args:
        input_video_path: Path to the source video file.
        output_video_path: Path to save the video with the new audio sample rate.
        audio_sample_rate: Target audio sample rate in Hz (e.g., 44100, 48000).
    Returns:
        A status message indicating success or failure.
    """
    primary_kwargs = {'ar': audio_sample_rate, 'vcodec': 'copy'} # ar for audio sample rate
    fallback_kwargs = {'ar': audio_sample_rate} # Re-encode video
    return _run_ffmpeg_with_fallback(input_video_path, output_video_path, primary_kwargs, fallback_kwargs)
