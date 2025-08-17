import ffmpeg
import os
from typing import Optional, Tuple, Dict

def crop_video(input_video_path: str, output_video_path: str,
               crop_params: Dict[str, int] = None,
               crop_preset: str = None,
               maintain_quality: bool = True,
               target_aspect: str = None) -> str:
    """
    Crop video to specific dimensions or aspect ratios.
    
    Args:
        input_video_path: Path to the input video file
        output_video_path: Path for the output video file
        crop_params: Dictionary with 'x', 'y', 'width', 'height' keys
        crop_preset: Preset crop ("center_square", "top_half", "bottom_half", "left_half", "right_half")
        maintain_quality: Whether to maintain original quality settings
        target_aspect: Target aspect ratio ("16:9", "9:16", "1:1", "4:3")
    
    Returns:
        Success message with output file path
    """
    
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video file does not exist: {input_video_path}")
    
    try:
        # Get video information
        probe = ffmpeg.probe(input_video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        
        # Determine crop parameters
        if crop_params:
            x = crop_params.get('x', 0)
            y = crop_params.get('y', 0)
            crop_width = crop_params.get('width', width)
            crop_height = crop_params.get('height', height)
        elif crop_preset:
            if crop_preset == "center_square":
                size = min(width, height)
                x = (width - size) // 2
                y = (height - size) // 2
                crop_width = crop_height = size
            elif crop_preset == "top_half":
                x, y = 0, 0
                crop_width, crop_height = width, height // 2
            elif crop_preset == "bottom_half":
                x, y = 0, height // 2
                crop_width, crop_height = width, height // 2
            elif crop_preset == "left_half":
                x, y = 0, 0
                crop_width, crop_height = width // 2, height
            elif crop_preset == "right_half":
                x, y = width // 2, 0
                crop_width, crop_height = width // 2, height
            else:
                raise ValueError(f"Unknown crop preset: {crop_preset}")
        elif target_aspect:
            # Calculate crop based on target aspect ratio
            aspect_parts = target_aspect.split(':')
            target_ratio = float(aspect_parts[0]) / float(aspect_parts[1])
            current_ratio = width / height
            
            if current_ratio > target_ratio:
                # Video is wider, crop from sides
                crop_height = height
                crop_width = int(height * target_ratio)
                x = (width - crop_width) // 2
                y = 0
            else:
                # Video is taller, crop from top/bottom
                crop_width = width
                crop_height = int(width / target_ratio)
                x = 0
                y = (height - crop_height) // 2
        else:
            raise ValueError("Must specify either crop_params, crop_preset, or target_aspect")
        
        # Validate crop parameters
        if x < 0 or y < 0 or x + crop_width > width or y + crop_height > height:
            raise ValueError("Crop parameters exceed video dimensions")
        
        # Load input
        input_stream = ffmpeg.input(input_video_path)
        
        # Apply crop filter
        video_stream = input_stream.video.filter('crop', crop_width, crop_height, x, y)
        
        # Set output parameters
        output_params = {
            'vcodec': 'libx264',
            'acodec': 'aac'
        }
        
        if maintain_quality:
            output_params.update({
                'crf': 18,
                'preset': 'medium'
            })
        
        # Create output
        output = ffmpeg.output(video_stream, input_stream.audio, output_video_path, **output_params)
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully cropped video to {crop_width}x{crop_height}: {output_video_path}"
        
    except Exception as e:
        return f"Error cropping video: {str(e)}"


def create_timelapse(input_video_path: str, output_video_path: str,
                    speed_factor: float = 10.0,
                    fps_output: int = 30,
                    smooth_motion: bool = True,
                    maintain_audio: bool = False) -> str:
    """
    Create timelapse video by speeding up footage.
    
    Args:
        input_video_path: Path to the input video file
        output_video_path: Path for the output video file
        speed_factor: How much to speed up (2.0 = 2x speed, 10.0 = 10x speed)
        fps_output: Output frame rate
        smooth_motion: Whether to apply motion blur for smooth timelapse
        maintain_audio: Whether to keep and speed up audio
    
    Returns:
        Success message with output file path
    """
    
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video file does not exist: {input_video_path}")
    
    if speed_factor <= 1.0:
        raise ValueError("Speed factor must be greater than 1.0 for timelapse")
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        
        # Calculate PTS (Presentation Time Stamp) multiplier
        pts_multiplier = 1.0 / speed_factor
        
        # Apply video speed change
        video_stream = input_stream.video.filter('setpts', f'{pts_multiplier}*PTS')
        
        # Apply frame rate filter
        video_stream = video_stream.filter('fps', fps_output)
        
        # Add motion blur for smooth timelapse
        if smooth_motion and speed_factor > 5.0:
            blur_amount = min(speed_factor / 10.0, 2.0)
            video_stream = video_stream.filter('minterpolate', 
                                             fps=fps_output, 
                                             mi_mode='mci',
                                             mc_mode='aobmc')
        
        output_params = {
            'vcodec': 'libx264',
            'preset': 'medium',
            'crf': 18
        }
        
        # Handle audio
        if maintain_audio:
            # Speed up audio to match video
            audio_stream = input_stream.audio.filter('atempo', min(speed_factor, 2.0))
            # If speed factor > 2, chain multiple atempo filters
            current_speed = speed_factor
            while current_speed > 2.0:
                audio_stream = audio_stream.filter('atempo', 2.0)
                current_speed /= 2.0
            if current_speed > 1.0:
                audio_stream = audio_stream.filter('atempo', current_speed)
            
            output_params['acodec'] = 'aac'
            output = ffmpeg.output(video_stream, audio_stream, output_video_path, **output_params)
        else:
            output = ffmpeg.output(video_stream, output_video_path, **output_params)
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully created timelapse at {speed_factor}x speed: {output_video_path}"
        
    except Exception as e:
        return f"Error creating timelapse: {str(e)}"


def create_slow_motion(input_video_path: str, output_video_path: str,
                      slow_factor: float = 2.0,
                      interpolation_method: str = "blend",
                      fps_output: int = 60,
                      maintain_audio: bool = True,
                      audio_pitch_correction: bool = True) -> str:
    """
    Create slow motion video with frame interpolation.
    
    Args:
        input_video_path: Path to the input video file
        output_video_path: Path for the output video file
        slow_factor: How much to slow down (2.0 = half speed, 4.0 = quarter speed)
        interpolation_method: Method for creating new frames ("blend", "mci", "optical_flow")
        fps_output: Output frame rate (higher for smoother slow motion)
        maintain_audio: Whether to keep and slow down audio
        audio_pitch_correction: Whether to maintain audio pitch when slowing
    
    Returns:
        Success message with output file path
    """
    
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video file does not exist: {input_video_path}")
    
    if slow_factor <= 1.0:
        raise ValueError("Slow factor must be greater than 1.0 for slow motion")
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        
        # Get original fps
        probe = ffmpeg.probe(input_video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        original_fps = eval(video_info['r_frame_rate'])
        
        # Calculate new timing
        pts_multiplier = slow_factor
        
        # Apply slow motion
        video_stream = input_stream.video.filter('setpts', f'{pts_multiplier}*PTS')
        
        # Apply interpolation for smoother slow motion
        if interpolation_method == "mci":
            # Motion Compensated Interpolation
            video_stream = video_stream.filter('minterpolate',
                                             fps=fps_output,
                                             mi_mode='mci',
                                             mc_mode='aobmc',
                                             vsbmc=1)
        elif interpolation_method == "optical_flow":
            # Optical flow interpolation
            video_stream = video_stream.filter('minterpolate',
                                             fps=fps_output,
                                             mi_mode='mci',
                                             mc_mode='obmc')
        elif interpolation_method == "blend":
            # Simple frame blending
            video_stream = video_stream.filter('fps', fps_output)
            video_stream = video_stream.filter('minterpolate', fps=fps_output, mi_mode='blend')
        else:
            # Just change frame rate
            video_stream = video_stream.filter('fps', fps_output)
        
        output_params = {
            'vcodec': 'libx264',
            'preset': 'slow',  # Better quality for slow motion
            'crf': 15  # Higher quality
        }
        
        # Handle audio
        if maintain_audio:
            # Slow down audio
            audio_stream = input_stream.audio
            
            if audio_pitch_correction:
                # Use rubberband filter for pitch correction (if available)
                try:
                    audio_stream = audio_stream.filter('rubberband', tempo=1.0/slow_factor)
                except:
                    # Fallback to simple tempo change
                    slow_amount = 1.0 / slow_factor
                    while slow_amount < 0.5:
                        audio_stream = audio_stream.filter('atempo', 0.5)
                        slow_amount *= 2
                    if slow_amount < 1.0:
                        audio_stream = audio_stream.filter('atempo', slow_amount)
            else:
                # Simple tempo change without pitch correction
                slow_amount = 1.0 / slow_factor
                while slow_amount < 0.5:
                    audio_stream = audio_stream.filter('atempo', 0.5)
                    slow_amount *= 2
                if slow_amount < 1.0:
                    audio_stream = audio_stream.filter('atempo', slow_amount)
            
            output_params['acodec'] = 'aac'
            output = ffmpeg.output(video_stream, audio_stream, output_video_path, **output_params)
        else:
            output = ffmpeg.output(video_stream, output_video_path, **output_params)
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully created slow motion at {slow_factor}x slower: {output_video_path}"
        
    except Exception as e:
        return f"Error creating slow motion: {str(e)}"