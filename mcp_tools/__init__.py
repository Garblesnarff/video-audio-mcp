
from .audio_processing.extract_audio_from_video import extract_audio_from_video
from .audio_processing.convert_audio_properties import convert_audio_properties
from .audio_processing.convert_audio_format import convert_audio_format
from .audio_processing.set_audio_bitrate import set_audio_bitrate
from .audio_processing.set_audio_sample_rate import set_audio_sample_rate
from .audio_processing.set_audio_channels import set_audio_channels
from .audio_processing.set_video_audio_track_codec import set_video_audio_track_codec
from .audio_processing.set_video_audio_track_bitrate import set_video_audio_track_bitrate
from .audio_processing.set_video_audio_track_sample_rate import set_video_audio_track_sample_rate
from .audio_processing.set_video_audio_track_channels import set_video_audio_track_channels
from .audio_processing.remove_silence import remove_silence
from .audio_processing.generate_audio_waveform import generate_audio_waveform
from .audio_processing.normalize_audio import normalize_audio

from .video_processing.convert_video_properties import convert_video_properties
from .video_processing.change_aspect_ratio import change_aspect_ratio
from .video_processing.convert_video_format import convert_video_format
from .video_processing.set_video_resolution import set_video_resolution
from .video_processing.set_video_codec import set_video_codec
from .video_processing.set_video_bitrate import set_video_bitrate
from .video_processing.set_video_frame_rate import set_video_frame_rate
from .video_processing.correct_colors import correct_colors
from .video_processing.stabilize_video import stabilize_video

from .editing.trim_video import trim_video
from .editing.create_video_from_images import create_video_from_images
from .editing.concatenate_videos import concatenate_videos
from .editing.change_video_speed import change_video_speed
from .editing.add_b_roll import add_b_roll
from .editing.add_basic_transitions import add_basic_transitions
from .editing.split_video_by_scenes import split_video_by_scenes

from .overlays.add_subtitles import add_subtitles
from .overlays.add_text_overlay import add_text_overlay
from .overlays.add_image_overlay import add_image_overlay

ALL_TOOLS = [
    extract_audio_from_video,
    convert_audio_properties,
    convert_audio_format,
    set_audio_bitrate,
    set_audio_sample_rate,
    set_audio_channels,
    set_video_audio_track_codec,
    set_video_audio_track_bitrate,
    set_video_audio_track_sample_rate,
    set_video_audio_track_channels,
    remove_silence,
    generate_audio_waveform,
    normalize_audio,
    convert_video_properties,
    change_aspect_ratio,
    convert_video_format,
    set_video_resolution,
    set_video_codec,
    set_video_bitrate,
    set_video_frame_rate,
    correct_colors,
    stabilize_video,
    trim_video,
    create_video_from_images,
    concatenate_videos,
    change_video_speed,
    add_b_roll,
    add_basic_transitions,
    split_video_by_scenes,
    add_subtitles,
    add_text_overlay,
    add_image_overlay,
]
