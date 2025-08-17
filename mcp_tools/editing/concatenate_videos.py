import ffmpeg
import os
import tempfile
import shutil
import subprocess
from ..utils import _get_media_properties

def concatenate_videos(video_paths: list[str], output_video_path: str,
                       transition_effect: str = None, transition_duration: float = None) -> str:
    """Concatenates multiple video files into a single output file.
    Supports optional xfade transition when concatenating exactly two videos.

    Args:
        video_paths: A list of paths to the video files to concatenate.
        output_video_path: The path to save the concatenated video file.
        transition_effect (str, optional): The xfade transition type. Options:
            - 'dissolve': Gradual blend between clips
            - 'fade': Simple fade through black
            - 'fadeblack': Fade through black
            - 'fadewhite': Fade through white
            - 'fadegrays': Fade through grayscale
            - 'distance': Distance transform transition
            - 'wipeleft', 'wiperight': Horizontal wipe
            - 'wipeup', 'wipedown': Vertical wipe
            - 'slideleft', 'slideright': Horizontal slide
            - 'slideup', 'slidedown': Vertical slide
            - 'smoothleft', 'smoothright': Smooth horizontal slide
            - 'smoothup', 'smoothdown': Smooth vertical slide
            - 'circlecrop': Rectangle crop transition
            - 'rectcrop': Rectangle crop transition
            - 'circleopen', 'circleclose': Circle open/close
            - 'vertopen', 'vertclose': Vertical open/close
            - 'horzopen', 'horzclose': Horizontal open/close
            - 'diagtl', 'diagtr', 'diagbl', 'diagbr': Diagonal transitions
            - 'hlslice', 'hrslice': Horizontal slice
            - 'vuslice', 'vdslice': Vertical slice
            - 'pixelize': Pixelize effect
            - 'radial': Radial transition
            - 'hblur': Horizontal blur
            Only applied if exactly two videos are provided. Defaults to None (no transition).
        transition_duration (float, optional): The duration of the xfade transition in seconds. 
                                             Required if transition_effect is specified. Defaults to None.
    
    Returns:
        A status message indicating success or failure.
    """
    if not video_paths:
        return "Error: No video paths provided for concatenation."
    if len(video_paths) < 1: # Allow single video to be "concatenated" (effectively copied/re-encoded)
        return "Error: At least one video is required."
    
    if transition_effect and transition_duration is None:
        return "Error: transition_duration is required when transition_effect is specified."
    if transition_effect and transition_duration <= 0:
        return "Error: transition_duration must be positive."

    # Validate transition_effect
    valid_transitions = {
        'dissolve', 'fade', 'fadeblack', 'fadewhite', 'fadegrays', 'distance',
        'wipeleft', 'wiperight', 'wipeup', 'wipedown',
        'slideleft', 'slideright', 'slideup', 'slidedown',
        'smoothleft', 'smoothright', 'smoothup', 'smoothdown',
        'circlecrop', 'rectcrop', 'circleopen', 'circleclose',
        'vertopen', 'vertclose', 'horzopen', 'horzclose',
        'diagtl', 'diagtr', 'diagbl', 'diagbr',
        'hlslice', 'hrslice', 'vuslice', 'vdslice',
        'pixelize', 'radial', 'hblur'
    }
    if transition_effect and transition_effect not in valid_transitions:
        return f"Error: Invalid transition_effect '{transition_effect}'. Valid options: {', '.join(sorted(valid_transitions))}"

    # Check if all input files exist
    for video_path in video_paths:
        if not os.path.exists(video_path):
            return f"Error: Input video file not found at {video_path}"

    # Handle single video case (copy or re-encode to target)
    if len(video_paths) == 1:
        try:
            # Simple copy if no processing needed, or re-encode to a standard format.
            # For now, let's assume re-encoding to ensure it matches expectations of a processed file.
            # This could be enhanced to use target_props like in add_b_roll if needed.
            ffmpeg.input(video_paths[0]).output(output_video_path, vcodec='libx264', acodec='aac').run(capture_stdout=True, capture_stderr=True)
            return f"Single video processed and saved to {output_video_path}"
        except ffmpeg.Error as e:
            return f"Error processing single video: {e.stderr.decode('utf8') if e.stderr else str(e)}"

    # Handle xfade transition for exactly two videos
    if transition_effect and len(video_paths) == 2:
        # Create a temporary directory for intermediate files
        temp_dir = tempfile.mkdtemp()
        try:
            video1_path = video_paths[0]
            video2_path = video_paths[1]
            
            props1 = _get_media_properties(video1_path)
            props2 = _get_media_properties(video2_path)

            if not props1['has_video'] or not props2['has_video']:
                return "Error: xfade transition requires both inputs to be videos."
            if transition_duration >= props1['duration']:
                 return f"Error: Transition duration ({transition_duration}s) cannot be equal or longer than the first video's duration ({props1['duration']})."

            # Check if both videos have audio
            has_audio = props1['has_audio'] and props2['has_audio']
            if not has_audio:
                print("Warning: At least one video lacks audio. Xfade will be video-only or silent audio.")

            # Determine common target properties for normalization before xfade
            # Preferring higher resolution/fps from inputs, or defaulting.
            target_w = max(props1['width'], props2['width'], 640) 
            target_h = max(props1['height'], props2['height'], 360)
            # Ensure a common FPS, e.g., highest of the two, or a default like 30
            target_fps = max(props1['avg_fps'], props2['avg_fps'], 30)
            if target_fps <= 0: 
                target_fps = 30 # safety net

            # Normalize input videos to have same dimensions and properties
            # First video
            norm_video1_path = os.path.join(temp_dir, "norm_video1.mp4")
            try:
                # Scale and set properties
                subprocess.run([
                    'ffmpeg',
                    '-i', video1_path,
                    '-vf', f'scale={target_w}:{target_h}',
                    '-r', str(target_fps),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-y',
                    norm_video1_path
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                return f"Error normalizing first video: {e.stderr.decode('utf8') if e.stderr else str(e)}"

            # Second video
            norm_video2_path = os.path.join(temp_dir, "norm_video2.mp4")
            try:
                # Scale and set properties
                subprocess.run([
                    'ffmpeg',
                    '-i', video2_path,
                    '-vf', f'scale={target_w}:{target_h}',
                    '-r', str(target_fps),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-y',
                    norm_video2_path
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                return f"Error normalizing second video: {e.stderr.decode('utf8') if e.stderr else str(e)}"

            # Get normalized video 1 duration
            norm_props1 = _get_media_properties(norm_video1_path)
            norm_video1_duration = norm_props1['duration']
            
            if transition_duration >= norm_video1_duration:
                return f"Error: Transition duration ({transition_duration}s) is too long for the normalized first video ({norm_video1_duration}s)."

            # Calculate offset (where second video starts relative to first)
            offset = norm_video1_duration - transition_duration
            
            # Create filter complex for xfade transition
            filter_complex = f"[0:v][1:v]xfade=transition={transition_effect}:duration={transition_duration}:offset={offset}"
            
            # Base command for video transition
            cmd = [
                'ffmpeg',
                '-i', norm_video1_path,
                '-i', norm_video2_path,
                '-filter_complex'
            ]
            
            # Add appropriate filters for video and audio
            if has_audio:
                # Audio transition (crossfade)
                filter_complex += f",[0:a][1:a]acrossfade=d={transition_duration}:c1=tri:c2=tri"
                cmd.extend([filter_complex, '-map', '[v]', '-map', '[a]'])
            else:
                # Video only
                filter_complex += "[v]"
                cmd.extend([filter_complex, '-map', '[v]'])
            
            # Add output file and encoding parameters
            cmd.extend([
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-y',
                output_video_path
            ])
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                return f"Videos concatenated successfully with '{transition_effect}' transition to {output_video_path}"
            except subprocess.CalledProcessError as e:
                return f"Error during xfade process: {e.stderr.decode('utf8') if e.stderr else str(e)}"
                
        except Exception as e:
            return f"An unexpected error occurred during xfade concatenation: {str(e)}"
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
    
    elif transition_effect and len(video_paths) > 2:
        return f"Error: xfade transition ('{transition_effect}') is currently only supported for exactly two videos. Found {len(video_paths)} videos."

    # Standard concatenation for 2+ videos without xfade
    # We'll use the concat demuxer approach
    temp_dir = tempfile.mkdtemp()
    try:
        # Normalize all videos to the same format/codec/resolution
        normalized_paths = []
        
        # Get target properties from first video
        first_props = _get_media_properties(video_paths[0])
        target_w = first_props['width'] if first_props['width'] > 0 else 1280
        target_h = first_props['height'] if first_props['height'] > 0 else 720
        target_fps = first_props['avg_fps'] if first_props['avg_fps'] > 0 else 30
        if target_fps <= 0:
            target_fps = 30
        
        # Process each video
        for i, video_path in enumerate(video_paths):
            norm_path = os.path.join(temp_dir, f"norm_{i}.mp4")
            try:
                subprocess.run([
                    'ffmpeg',
                    '-i', video_path,
                    '-vf', f'scale={target_w}:{target_h}',
                    '-r', str(target_fps),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-y',
                    norm_path
                ], check=True, capture_output=True)
                normalized_paths.append(norm_path)
            except subprocess.CalledProcessError as e:
                return f"Error normalizing video {i}: {e.stderr.decode('utf8') if e.stderr else str(e)}"
        
        # Create a concat file
        concat_list_path = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_list_path, 'w') as f:
            for path in normalized_paths:
                f.write(f"file '{path}'\n")
        
        # Run ffmpeg concat
        try:
            subprocess.run([
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list_path,
                '-c', 'copy',
                '-y',
                output_video_path
            ], check=True, capture_output=True)
            return f"Videos concatenated successfully to {output_video_path}"
        except subprocess.CalledProcessError as e:
            return f"Error during concatenation: {e.stderr.decode('utf8') if e.stderr else str(e)}"
            
    except Exception as e:
        return f"An unexpected error occurred during standard concatenation: {str(e)}"
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
