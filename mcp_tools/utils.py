
import ffmpeg
import os
import re
import tempfile
import shutil
import subprocess

def _run_ffmpeg_with_fallback(input_path: str, output_path: str, primary_kwargs: dict, fallback_kwargs: dict) -> str:
    """Helper to run ffmpeg command with primary kwargs, falling back to other kwargs on ffmpeg.Error."""
    try:
        ffmpeg.input(input_path).output(output_path, **primary_kwargs).run(capture_stdout=True, capture_stderr=True)
        return f"Operation successful (primary method) and saved to {output_path}"
    except ffmpeg.Error as e_primary:
        try:
            ffmpeg.input(input_path).output(output_path, **fallback_kwargs).run(capture_stdout=True, capture_stderr=True)
            return f"Operation successful (fallback method) and saved to {output_path}"
        except ffmpeg.Error as e_fallback:
            err_primary_msg = e_primary.stderr.decode('utf8') if e_primary.stderr else str(e_primary)
            err_fallback_msg = e_fallback.stderr.decode('utf8') if e_fallback.stderr else str(e_fallback)
            return f"Error. Primary method failed: {err_primary_msg}. Fallback method also failed: {err_fallback_msg}"
    except FileNotFoundError:
        return f"Error: Input file not found at {input_path}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def _parse_time_to_seconds(time_str: str) -> float:
    """Converts HH:MM:SS.mmm or seconds string to float seconds."""
    if isinstance(time_str, (int, float)):
        return float(time_str)
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        else:
            raise ValueError(f"Invalid time format: {time_str}")
    return float(time_str)

def _get_media_properties(media_path: str) -> dict:
    """Probes media file and returns key properties."""
    try:
        probe = ffmpeg.probe(media_path)
        video_stream_info = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        audio_stream_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
        
        props = {
            'duration': float(probe['format'].get('duration', 0.0)),
            'has_video': video_stream_info is not None,
            'has_audio': audio_stream_info is not None,
            'width': int(video_stream_info['width']) if video_stream_info and 'width' in video_stream_info else 0,
            'height': int(video_stream_info['height']) if video_stream_info and 'height' in video_stream_info else 0,
            'avg_fps': 0, # Default, will be calculated if possible
            'sample_rate': int(audio_stream_info['sample_rate']) if audio_stream_info and 'sample_rate' in audio_stream_info else 44100,
            'channels': int(audio_stream_info['channels']) if audio_stream_info and 'channels' in audio_stream_info else 2,
            'channel_layout': audio_stream_info.get('channel_layout', 'stereo') if audio_stream_info else 'stereo'
        }
        if video_stream_info and 'avg_frame_rate' in video_stream_info and video_stream_info['avg_frame_rate'] != '0/0':
            num, den = map(int, video_stream_info['avg_frame_rate'].split('/'))
            if den > 0:
                props['avg_fps'] = num / den
            else:
                props['avg_fps'] = 30 # Default if denominator is 0
        else: # Fallback if avg_frame_rate is not useful
            props['avg_fps'] = 30 # A common default

        return props
    except ffmpeg.Error as e:
        raise RuntimeError(f"Error probing file {media_path}: {e.stderr.decode('utf8') if e.stderr else str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error probing file {media_path}: {str(e)}")


def _prepare_clip_for_concat(source_path: str, start_time_sec: float, end_time_sec: float,
                               target_props: dict, temp_dir: str, segment_index: int) -> str:
    """Prepares a clip segment (trims, scales, sets common properties) for concatenation.
    Returns path to the temporary processed clip.
    """
    try:
        # Create a unique temp file name
        temp_output_path = os.path.join(temp_dir, f"segment_{segment_index}.mp4")
        
        input_stream = ffmpeg.input(source_path, ss=start_time_sec, to=end_time_sec)
        
        processed_video_stream = None
        processed_audio_stream = None

        # Video processing
        if target_props['has_video']:
            video_s = input_stream.video
            video_s = video_s.filter(
                'scale',
                width=str(target_props['width']), 
                height=str(target_props['height']), 
                force_original_aspect_ratio='decrease'
            )
            video_s = video_s.filter(
                'pad',
                width=str(target_props['width']),
                height=str(target_props['height']),
                x='(ow-iw)/2',
                y='(oh-ih)/2',
                color='black'
            )
            video_s = video_s.filter('setsar', '1/1') # Use ratio e.g. 1/1 for square pixels
            video_s = video_s.filter('setpts', 'PTS-STARTPTS')
            processed_video_stream = video_s
        
        # Audio processing
        if target_props['has_audio']:
            audio_s = input_stream.audio
            audio_s = audio_s.filter('asetpts', 'PTS-STARTPTS')
            audio_s = audio_s.filter(
                'aformat',
                sample_fmts='s16', # Common format for compatibility
                sample_rates=str(target_props['sample_rate']),
                channel_layouts=target_props['channel_layout']
            )
            processed_audio_stream = audio_s

        output_params = {
            'vcodec': 'libx264',
            'pix_fmt': 'yuv420p',
            'r': target_props['avg_fps'], # Frame rate
            'acodec': 'aac',
            'ar': target_props['sample_rate'], # Audio sample rate
            'ac': target_props['channels'],   # Audio channels
            'strict': '-2' # Needed for some AAC experimental features or if defaults change
        }

        output_streams_for_ffmpeg = []
        if processed_video_stream:
            output_streams_for_ffmpeg.append(processed_video_stream)
        if processed_audio_stream:
            output_streams_for_ffmpeg.append(processed_audio_stream)
        
        if not output_streams_for_ffmpeg:
            # This can happen if the source has no video/audio or target_props indicates so.
            # For a concatenation tool, we expect valid media.
            raise ValueError(f"No video or audio streams identified to process for segment {segment_index} from {source_path}")

        ffmpeg.output(*output_streams_for_ffmpeg, temp_output_path, **output_params).run(capture_stdout=True, capture_stderr=True)
        return temp_output_path

    except ffmpeg.Error as e:
        err_msg = e.stderr.decode('utf8') if e.stderr else str(e)
        raise RuntimeError(f"Error preparing segment {segment_index} from {source_path}: {err_msg}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error preparing segment {segment_index} from {source_path}: {str(e)}")
