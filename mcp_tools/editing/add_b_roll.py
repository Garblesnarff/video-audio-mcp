
import ffmpeg
import os
import tempfile
import shutil
import subprocess
from ..utils import _get_media_properties, _parse_time_to_seconds

def add_b_roll(main_video_path: str, broll_clips: list[dict], output_video_path: str) -> str:
    """Inserts B-roll clips into a main video as overlays.
    Args listed in previous messages (docstring unchanged for brevity here)
    """
    if not os.path.exists(main_video_path):
        return f"Error: Main video file not found at {main_video_path}"
    if not broll_clips:
        try:
            ffmpeg.input(main_video_path).output(output_video_path, c='copy').run(capture_stdout=True, capture_stderr=True)
            return f"No B-roll clips provided. Main video copied to {output_video_path}"
        except ffmpeg.Error as e:
            return f"No B-roll clips, but error copying main video: {e.stderr.decode('utf8') if e.stderr else str(e)}"

    valid_positions = {'fullscreen', 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'}
    valid_transitions = {'fade', 'slide_left', 'slide_right', 'slide_up', 'slide_down'}
    
    try:
        # Create a temporary directory for intermediate files
        temp_dir = tempfile.mkdtemp()
        
        try:
            main_props = _get_media_properties(main_video_path)
            if not main_props['has_video']:
                return f"Error: Main video {main_video_path} has no video stream."
                
            # Get main video dimensions 
            main_width = main_props['width']
            main_height = main_props['height']
            
            # First pass: Process each B-roll clip individually
            processed_clips = []
            
            for i, broll_item in enumerate(sorted(broll_clips, key=lambda x: _parse_time_to_seconds(x['insert_at_timestamp']))):
                clip_path = broll_item['clip_path']
                if not os.path.exists(clip_path):
                    return f"Error: B-roll clip not found at {clip_path}"
                
                broll_props = _get_media_properties(clip_path)
                if not broll_props['has_video']:
                    continue
                
                # Process timestamps
                start_time = _parse_time_to_seconds(broll_item['insert_at_timestamp'])
                duration = _parse_time_to_seconds(broll_item.get('duration', str(broll_props['duration'])))
                position = broll_item.get('position', 'fullscreen')
                
                if position not in valid_positions:
                    return f"Error: Invalid position '{position}' for B-roll {clip_path}"
                
                # Create a processed version of this clip
                temp_clip = os.path.join(temp_dir, f"processed_broll_{i}.mp4")
                scale_factor = broll_item.get('scale', 1.0 if position == 'fullscreen' else 0.5)
                
                # Apply scaling based on position
                scale_filter_parts = []
                
                if position == 'fullscreen':
                    scale_filter_parts.append(f"scale={main_width}:{main_height}")
                else:
                    scale_filter_parts.append(f"scale=iw*{scale_factor}:ih*{scale_factor}")
                
                # Add fade transitions if specified
                transition_in = broll_item.get('transition_in')
                transition_out = broll_item.get('transition_out')
                transition_duration = float(broll_item.get('transition_duration', 0.5))
                
                if transition_in == 'fade':
                    scale_filter_parts.append(f"fade=t=in:st=0:d={transition_duration}")
                
                if transition_out == 'fade':
                    # Calculate fade out start time 
                    fade_out_start = max(0, float(broll_props['duration']) - transition_duration)
                    scale_filter_parts.append(f"fade=t=out:st={fade_out_start}:d={transition_duration}")
                
                # Convert filters list to string
                filter_string = ",".join(scale_filter_parts)
                
                # Process the b-roll clip
                try:
                    subprocess.run([
                        'ffmpeg', 
                        '-i', clip_path,
                        '-vf', filter_string,
                        '-c:v', 'libx264', 
                        '-c:a', 'aac',
                        '-y',  # Overwrite output if exists
                        temp_clip
                    ], check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    return f"Error processing B-roll {i}: {e.stderr.decode('utf8') if e.stderr else str(e)}"
                
                # Calculate overlay coordinates based on position
                overlay_x = "0"
                overlay_y = "0"
                
                if position == 'top-left':
                    overlay_x, overlay_y = "10", "10" 
                elif position == 'top-right':
                    overlay_x, overlay_y = f"W-w-10", "10"  # W=main width, w=overlay width
                elif position == 'bottom-left':
                    overlay_x, overlay_y = "10", "H-h-10"  # H=main height, h=overlay height
                elif position == 'bottom-right':
                    overlay_x, overlay_y = "W-w-10", "H-h-10"
                elif position == 'center':
                    overlay_x, overlay_y = "(W-w)/2", "(H-h)/2"
                
                # Store clip info with processed path
                processed_clips.append({
                    'path': temp_clip,
                    'start_time': start_time,
                    'duration': duration,
                    'position': position,
                    'overlay_x': overlay_x,
                    'overlay_y': overlay_y,
                    'transition_in': transition_in,
                    'transition_out': transition_out,
                    'transition_duration': transition_duration,
                    'audio_mix': float(broll_item.get('audio_mix', 0.0))
                })
            
            # Second pass: Create a filter complex for all clips
            if not processed_clips:
                # No valid clips to process
                try:
                    shutil.copy(main_video_path, output_video_path)
                    return f"No valid B-roll clips to overlay. Main video copied to {output_video_path}"
                except Exception as e:
                    return f"No valid B-roll clips, but error copying main video: {str(e)}"
            
            # Build filter string for second pass
            filter_parts = []
            
            # Reference the main video
            main_overlay = "[0:v]"
            
            # Add each overlay
            for i, clip in enumerate(processed_clips):
                # Create unique labels
                current_label = f"[v{i}]"
                overlay_index = i + 1  # Start from 1 as 0 is main video
                
                # Basic overlay without slide transitions
                if not (('slide' in clip['transition_in']) or ('slide' in clip['transition_out'])):
                    # Simple overlay with enable expression
                    overlay_filter = (
                        f"{main_overlay}[{overlay_index}:v]overlay="
                        f"x={clip['overlay_x']}:y={clip['overlay_y']}:"
                        f"enable='between(t,{clip['start_time']},{clip['start_time'] + clip['duration']})'")
                    
                    if i < len(processed_clips) - 1:
                        overlay_filter += current_label
                        main_overlay = current_label
                    else:
                        # Last overlay, output directly
                        overlay_filter += "[v]"
                    
                    filter_parts.append(overlay_filter)
                else:
                    # For slide transitions, we'll use a simplified approach
                    # with basic enable condition only
                    overlay_filter = (
                        f"{main_overlay}[{overlay_index}:v]overlay="
                        f"x={clip['overlay_x']}:y={clip['overlay_y']}:"
                        f"enable='between(t,{clip['start_time']},{clip['start_time'] + clip['duration']})'")
                    
                    if i < len(processed_clips) - 1:
                        overlay_filter += current_label
                        main_overlay = current_label
                    else:
                        overlay_filter += "[v]"
                    
                    filter_parts.append(overlay_filter)
            
            # Combine filter parts
            filter_complex = ";".join(filter_parts)
            
            # Audio handling
            audio_output = []
            
            # If any clip has audio_mix > 0, we would add audio mixing here
            # For simplicity, we'll just use the main audio track
            if main_props['has_audio']:
                audio_output = ['-map', '0:a']
            
            # Prepare input files
            input_files = ['-i', main_video_path]
            for clip in processed_clips:
                input_files.extend(['-i', clip['path']])
            
            # Build the final command
            cmd = [
                'ffmpeg',
                *input_files,
                '-filter_complex', filter_complex,
                '-map', '[v]',
                *audio_output,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-y',
                output_video_path
            ]
            
            # Run final command
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                return f"B-roll clips added successfully as overlays. Output at {output_video_path}"
            except subprocess.CalledProcessError as e:
                error_message = e.stderr.decode('utf8') if e.stderr else str(e)
                return f"Error in final B-roll composition: {error_message}"
        
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
    
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error adding B-roll overlays: {error_message}"
    except ValueError as e:
        return f"Error with input values (e.g., time format): {str(e)}"
    except RuntimeError as e:
        return f"Runtime error during B-roll processing: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred in add_b_roll: {str(e)}"
