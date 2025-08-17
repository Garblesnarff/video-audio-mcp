

import ffmpeg
import os
import tempfile
import shutil
import subprocess
from ..utils import _get_media_properties

def create_video_from_images(image_paths: list[str], output_video_path: str, 
                           duration_per_image: float = 5.0, fps: int = 30,
                           transition_type: str = None, transition_duration: float = 1.0,
                           audio_path: str = None, sync_to_audio: bool = False,
                           ken_burns_effect: bool = False, resolution: str = None) -> str:
    """Creates a video from one or more images with various options.
    
    Args:
        image_paths: List of paths to image files (PNG, JPG, etc.)
        output_video_path: Path to save the output video
        duration_per_image: How long each image displays (seconds). Ignored if sync_to_audio=True
        fps: Frame rate of output video
        transition_type: Optional transition between images. Options:
            - 'fade': Crossfade between images
            - 'slide_left', 'slide_right', 'slide_up', 'slide_down': Slide transitions
            - 'wipe_left', 'wipe_right', 'wipe_up', 'wipe_down': Wipe transitions
            - 'dissolve': Dissolve transition
            - None: No transition (hard cut)
        transition_duration: Duration of transitions in seconds
        audio_path: Optional path to audio file to include
        sync_to_audio: If True, adjusts total duration to match audio length
        ken_burns_effect: If True, adds subtle zoom/pan movement to images
        resolution: Target resolution (e.g., '1920x1080', '1280x720'). If None, uses first image size
    
    Returns:
        A status message indicating success or failure.
    """
    if not image_paths:
        return "Error: No image paths provided"
    
    # Validate all images exist
    for img_path in image_paths:
        if not os.path.exists(img_path):
            return f"Error: Image file not found at {img_path}"
    
    # Validate audio if provided
    if audio_path and not os.path.exists(audio_path):
        return f"Error: Audio file not found at {audio_path}"
    
    try:
        # Get audio duration if syncing
        audio_duration = None
        if audio_path and sync_to_audio:
            audio_props = _get_media_properties(audio_path)
            audio_duration = audio_props['duration']
            if audio_duration <= 0:
                return "Error: Could not determine audio duration for sync"
        
        # Calculate timing
        num_images = len(image_paths)
        if sync_to_audio and audio_duration:
            # Account for transitions when calculating duration per image
            total_transition_time = (num_images - 1) * transition_duration if transition_type and num_images > 1 else 0
            available_time = audio_duration - total_transition_time
            if available_time <= 0:
                return f"Error: Audio duration ({audio_duration}s) too short for {num_images} images with transitions"
            duration_per_image = available_time / num_images
        
        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Process single image case
            if num_images == 1:
                # Simple case: one image
                filter_complex_parts = []
                
                # Set up base image input with loop
                input_cmd = [
                    'ffmpeg',
                    '-loop', '1',
                    '-i', image_paths[0],
                    '-t', str(duration_per_image)
                ]
                
                # Add audio if provided
                if audio_path:
                    input_cmd.extend(['-i', audio_path])
                
                # Build filter for single image
                if resolution:
                    res_filter = resolution.replace('x', ':') if 'x' in resolution else resolution
                    filter_complex_parts.append(f"[0:v]scale={res_filter}:force_original_aspect_ratio=decrease,pad={res_filter}:'(ow-iw)/2':'(oh-ih)/2':black")
                else:
                    filter_complex_parts.append("[0:v]format=yuv420p")
                
                # Add Ken Burns effect if requested
                if ken_burns_effect:
                    # Subtle zoom from 1.0 to 1.1 over the duration
                    zoom_expr = f"1+0.1*t/{duration_per_image}"
                    # zoompan needs size in WIDTHxHEIGHT format, not WIDTH:HEIGHT
                    zoom_res = resolution if resolution else '1920x1080'
                    # For subprocess list arguments, we don't need quotes around expressions
                    filter_complex_parts.append(f"zoompan=z={zoom_expr}:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={int(duration_per_image*fps)}:s={zoom_res}:fps={fps}")
                
                # Finalize filter
                filter_complex_parts.append("[v]")
                
                # Build output command
                output_cmd = []
                if filter_complex_parts:
                    filter_complex = ','.join(filter_complex_parts[:-1]) + filter_complex_parts[-1]
                    output_cmd.extend(['-filter_complex', filter_complex, '-map', '[v]'])
                
                # Add audio mapping if provided
                if audio_path:
                    output_cmd.extend(['-map', '1:a', '-c:a', 'aac'])
                    if sync_to_audio:
                        output_cmd.extend(['-shortest'])
                
                # Output settings
                output_cmd.extend([
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-r', str(fps),
                    '-y',
                    output_video_path
                ])
                
                # Execute
                cmd = input_cmd + output_cmd
                subprocess.run(cmd, check=True, capture_output=True)
                
                return f"Video created successfully from single image: {output_video_path}"
            
            # Multiple images case
            else:
                # First, create individual video segments from each image
                segment_paths = []
                
                for i, img_path in enumerate(image_paths):
                    segment_path = os.path.join(temp_dir, f"segment_{i:04d}.mp4")
                    
                    # Create video from single image
                    cmd = [
                        'ffmpeg',
                        '-loop', '1',
                        '-i', img_path,
                        '-t', str(duration_per_image),
                        '-vf', f"scale={(resolution.replace('x', ':') if resolution and 'x' in resolution else '1920:1080')}:force_original_aspect_ratio=decrease,pad={(resolution.replace('x', ':') if resolution and 'x' in resolution else '1920:1080')}:'(ow-iw)/2':'(oh-ih)/2':black"
                    ]
                    
                    # Add Ken Burns if requested
                    if ken_burns_effect:
                        # Alternate between zoom in and zoom out
                        if i % 2 == 0:
                            zoom_expr = f"1+0.1*t/{duration_per_image}"  # Zoom in
                        else:
                            zoom_expr = f"1.1-0.1*t/{duration_per_image}"  # Zoom out
                        
                        # For subprocess list arguments, we don't need quotes around expressions
                        zoompan_filter = f"zoompan=z={zoom_expr}:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={int(duration_per_image*fps)}:s={resolution if resolution else '1920x1080'}:fps={fps}"
                        cmd[-1] += f",{zoompan_filter}"
                    
                    cmd.extend([
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        '-r', str(fps),
                        '-y',
                        segment_path
                    ])
                    
                    subprocess.run(cmd, check=True, capture_output=True)
                    segment_paths.append(segment_path)
                
                # Now concatenate with transitions if requested
                if transition_type and num_images > 1:
                    # Use xfade for transitions between segments
                    filter_complex_parts = []
                    current_input = "[0:v]"
                    
                    for i in range(1, len(segment_paths)):
                        # Calculate offset for this transition
                        offset = (duration_per_image - transition_duration) + (i-1) * (duration_per_image - transition_duration)
                        
                        # Map transition types to xfade transitions
                        xfade_transition = transition_type
                        if transition_type == 'slide_left':
                            xfade_transition = 'slideleft'
                        elif transition_type == 'slide_right':
                            xfade_transition = 'slideright'
                        elif transition_type == 'slide_up':
                            xfade_transition = 'slideup'
                        elif transition_type == 'slide_down':
                            xfade_transition = 'slidedown'
                        elif transition_type == 'wipe_left':
                            xfade_transition = 'wipeleft'
                        elif transition_type == 'wipe_right':
                            xfade_transition = 'wiperight'
                        elif transition_type == 'wipe_up':
                            xfade_transition = 'wipeup'
                        elif transition_type == 'wipe_down':
                            xfade_transition = 'wipedown'
                        elif transition_type == 'fade':
                            xfade_transition = 'fade'
                        
                        if i < len(segment_paths) - 1:
                            filter_complex_parts.append(
                                f"{current_input}[{i}:v]xfade=transition={xfade_transition}:duration={transition_duration}:offset={offset}[v{i}]"
                            )
                            current_input = f"[v{i}]"
                        else:
                            filter_complex_parts.append(
                                f"{current_input}[{i}:v]xfade=transition={xfade_transition}:duration={transition_duration}:offset={offset}[v]"
                            )
                    
                    # Build command with transitions
                    cmd = ['ffmpeg']
                    for seg_path in segment_paths:
                        cmd.extend(['-i', seg_path])
                    
                    if audio_path:
                        cmd.extend(['-i', audio_path])
                    
                    filter_complex = ';'.join(filter_complex_parts)
                    cmd.extend([
                        '-filter_complex', filter_complex,
                        '-map', '[v]'
                    ])
                    
                    if audio_path:
                        cmd.extend(['-map', f'{len(segment_paths)}:a', '-c:a', 'aac'])
                        if sync_to_audio:
                            cmd.extend(['-shortest'])
                    
                    cmd.extend([
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        '-y',
                        output_video_path
                    ])
                    
                    subprocess.run(cmd, check=True, capture_output=True)
                
                else:
                    # No transitions - use concat
                    concat_list_path = os.path.join(temp_dir, "concat_list.txt")
                    with open(concat_list_path, 'w') as f:
                        for seg_path in segment_paths:
                            f.write(f"file '{seg_path}'\n")
                    
                    cmd = [
                        'ffmpeg',
                        '-f', 'concat',
                        '-safe', '0',
                        '-i', concat_list_path
                    ]
                    
                    if audio_path:
                        cmd.extend(['-i', audio_path])
                    
                    cmd.extend(['-c:v', 'copy'])
                    
                    if audio_path:
                        cmd.extend(['-map', '0:v', '-map', '1:a', '-c:a', 'aac'])
                        if sync_to_audio:
                            cmd.extend(['-shortest'])
                    
                    cmd.extend(['-y', output_video_path])
                    
                    subprocess.run(cmd, check=True, capture_output=True)
                
                return f"Video slideshow created successfully from {num_images} images: {output_video_path}"
                
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating video from images: {error_msg}"
    except Exception as e:
        return f"Unexpected error creating video from images: {str(e)}"

