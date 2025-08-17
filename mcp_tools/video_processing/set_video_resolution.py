
import ffmpeg
from ..utils import _run_ffmpeg_with_fallback

def set_video_resolution(input_video_path: str, output_video_path: str, resolution: str) -> str:
    """Sets the resolution of a video, attempting to copy the audio stream.
    Args:
        input_video_path: Path to the source video file.
        output_video_path: Path to save the video with the new resolution.
        resolution: Target video resolution (e.g., '1920x1080', '1280x720', or '720' for height).
    Returns:
        A status message indicating success or failure.
    """
    vf_filters = []
    if 'x' in resolution:
        vf_filters.append(f"scale={resolution}")
    else:
        vf_filters.append(f"scale=-2:{resolution}")
    vf_filter_str = ",".join(vf_filters)
    
    primary_kwargs = {'vf': vf_filter_str, 'acodec': 'copy'}
    fallback_kwargs = {'vf': vf_filter_str} # Re-encode audio
    return _run_ffmpeg_with_fallback(input_video_path, output_video_path, primary_kwargs, fallback_kwargs)
