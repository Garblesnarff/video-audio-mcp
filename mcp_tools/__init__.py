
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

# New video effects
from .video_effects.apply_video_filters import apply_video_filters
from .video_effects.advanced_transitions import apply_advanced_transitions
from .video_effects.motion_graphics import create_motion_graphics
from .video_effects.chroma_key import apply_chroma_key, create_virtual_background, advanced_chroma_key_with_lighting
from .video_effects.video_morphing import apply_video_morphing, create_shape_morph

# New audio effects
from .audio_effects.apply_audio_effects import apply_audio_effects, create_audio_chain
from .audio_effects.multitrack_mixing import mix_audio_tracks, create_audio_bed, create_stereo_mix, create_surround_mix, mix_with_timeline
from .audio_effects.audio_visualization import create_audio_visualization, create_lyric_visualization, create_music_video_template
from .audio_effects.voice_processing import process_voice, batch_voice_process
from .audio_effects.spatial_audio import create_spatial_audio, create_3d_audio_scene, convert_to_spatial_format

# Phase 2A: Video manipulation
from .video_manipulation.rotate_flip_video import rotate_video, flip_mirror_video, rotate_and_flip_video, auto_rotate_video
from .video_manipulation.picture_in_picture import create_picture_in_picture, create_multi_pip, create_animated_pip

# Phase 2A: Frame manipulation
from .frame_manipulation.extract_frames import extract_frames, extract_frame_at_time, extract_frames_batch, extract_frame_sequence
from .frame_manipulation.thumbnail_generator import extract_thumbnails, generate_smart_thumbnails, create_thumbnail_grid
from .frame_manipulation.reverse_video import reverse_video, reverse_video_section, create_boomerang_effect, reverse_with_speed_ramp

# Phase 2A: Video restoration
from .video_restoration.denoise_enhance import denoise_video, denoise_video_advanced, batch_denoise_videos

# Phase 2B: Layout & Composition
from .layout_composition.split_screen import create_split_screen, create_video_grid
from .layout_composition.crop_resize import crop_video, create_timelapse, create_slow_motion

# Phase 2C: Quality & Enhancement
from .quality_enhancement.upscale_enhance import upscale_video, color_correction, auto_enhance_video
from .quality_enhancement.stabilize_cleanup import stabilize_shaky_video, remove_background, batch_enhance_videos

# Phase 2D: Advanced Features
from .advanced_features.slideshow_gif import create_slideshow, create_gif_from_video, batch_process_videos
from .advanced_features.motion_effects import add_motion_blur, create_360_video, create_cinemagraph

# Phase 3A: AI Transcription
from .ai_transcription.whisper_transcription import transcribe_audio_whisper, transcribe_video_whisper, batch_transcribe_videos, create_styled_subtitles

# Phase 3B: Computer Vision
from .computer_vision.object_detection import detect_objects_yolo, generate_smart_thumbnails_ai, auto_crop_to_subject

# Phase 3C: YouTube Optimization
from .youtube_optimization.content_analyzer import detect_scene_changes, generate_youtube_chapters, analyze_content_density, extract_youtube_shorts

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
    # New video effects
    apply_video_filters,
    apply_advanced_transitions,
    create_motion_graphics,
    apply_chroma_key,
    create_virtual_background,
    advanced_chroma_key_with_lighting,
    apply_video_morphing,
    create_shape_morph,
    # New audio effects
    apply_audio_effects,
    create_audio_chain,
    mix_audio_tracks,
    create_audio_bed,
    create_stereo_mix,
    create_surround_mix,
    mix_with_timeline,
    create_audio_visualization,
    create_lyric_visualization,
    create_music_video_template,
    process_voice,
    batch_voice_process,
    create_spatial_audio,
    create_3d_audio_scene,
    convert_to_spatial_format,
    # Phase 2A: Video manipulation
    rotate_video,
    flip_mirror_video,
    rotate_and_flip_video,
    auto_rotate_video,
    create_picture_in_picture,
    create_multi_pip,
    create_animated_pip,
    # Phase 2A: Frame manipulation
    extract_frames,
    extract_frame_at_time,
    extract_frames_batch,
    extract_frame_sequence,
    extract_thumbnails,
    generate_smart_thumbnails,
    create_thumbnail_grid,
    reverse_video,
    reverse_video_section,
    create_boomerang_effect,
    reverse_with_speed_ramp,
    # Phase 2A: Video restoration
    denoise_video,
    denoise_video_advanced,
    batch_denoise_videos,
    # Phase 2B: Layout & Composition
    create_split_screen,
    create_video_grid,
    crop_video,
    create_timelapse,
    create_slow_motion,
    # Phase 2C: Quality & Enhancement
    upscale_video,
    color_correction,
    auto_enhance_video,
    stabilize_shaky_video,
    remove_background,
    batch_enhance_videos,
    # Phase 2D: Advanced Features
    create_slideshow,
    create_gif_from_video,
    batch_process_videos,
    add_motion_blur,
    create_360_video,
    create_cinemagraph,
    # Phase 3A: AI Transcription
    transcribe_audio_whisper,
    transcribe_video_whisper,
    batch_transcribe_videos,
    create_styled_subtitles,
    # Phase 3B: Computer Vision
    detect_objects_yolo,
    generate_smart_thumbnails_ai,
    auto_crop_to_subject,
    # Phase 3C: YouTube Optimization
    detect_scene_changes,
    generate_youtube_chapters,
    analyze_content_density,
    extract_youtube_shorts,
]
