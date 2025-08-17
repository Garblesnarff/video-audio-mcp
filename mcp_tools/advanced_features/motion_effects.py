import ffmpeg
import os
from typing import Dict, Optional, List

def add_motion_blur(input_video_path: str, output_video_path: str,
                   blur_amount: float = 2.0,
                   blur_angle: float = 0.0,
                   motion_detection: bool = True,
                   preserve_static: bool = True) -> str:
    """
    Add motion blur effect to video to simulate camera movement or fast motion.
    
    Args:
        input_video_path: Path to the input video file
        output_video_path: Path for the output video file
        blur_amount: Amount of motion blur (0.5-10.0)
        blur_angle: Angle of motion blur in degrees (0-360)
        motion_detection: Whether to apply blur only to moving objects
        preserve_static: Whether to preserve static elements without blur
    
    Returns:
        Success message with output file path
    """
    
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video file does not exist: {input_video_path}")
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        video_stream = input_stream.video
        
        if motion_detection:
            # Apply motion-based blur using temporal analysis
            # Create motion vector field
            motion_stream = video_stream.filter('mestimate',
                                              method='epzs',
                                              mb_size=16,
                                              search_param=7)
            
            # Apply blur based on motion vectors
            video_stream = ffmpeg.filter([video_stream, motion_stream], 'minterpolate',
                                       fps='source_fps',
                                       mi_mode='mci',
                                       mc_mode='aobmc',
                                       vsbmc=1)
            
            # Additional directional blur
            if blur_angle != 0:
                # Convert angle to radians and calculate blur direction
                import math
                angle_rad = math.radians(blur_angle)
                blur_x = blur_amount * math.cos(angle_rad)
                blur_y = blur_amount * math.sin(angle_rad)
                
                video_stream = video_stream.filter('boxblur',
                                                 luma_radius=f'{abs(blur_x)}:1',
                                                 luma_power=1)
        else:
            # Apply uniform motion blur
            if blur_angle == 0:
                # Horizontal motion blur
                video_stream = video_stream.filter('boxblur',
                                                 luma_radius=f'{blur_amount}:1',
                                                 luma_power=1)
            elif blur_angle == 90:
                # Vertical motion blur
                video_stream = video_stream.filter('boxblur',
                                                 luma_radius=f'1:{blur_amount}',
                                                 luma_power=1)
            else:
                # Diagonal motion blur - simulate with rotation and blur
                video_stream = video_stream.filter('rotate', angle=f'{blur_angle}*PI/180')
                video_stream = video_stream.filter('boxblur',
                                                 luma_radius=f'{blur_amount}:1',
                                                 luma_power=1)
                video_stream = video_stream.filter('rotate', angle=f'-{blur_angle}*PI/180')
        
        # Optional: Preserve static elements by blending original
        if preserve_static and motion_detection:
            original_stream = input_stream.video
            # Blend motion-blurred with original based on motion intensity
            video_stream = ffmpeg.filter([original_stream, video_stream], 'blend',
                                       mode='overlay',
                                       opacity=0.7)
        
        output = ffmpeg.output(video_stream, input_stream.audio, output_video_path,
                             vcodec='libx264', acodec='aac',
                             preset='medium', crf=18)
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully added motion blur (amount: {blur_amount}, angle: {blur_angle}°): {output_video_path}"
        
    except Exception as e:
        return f"Error adding motion blur: {str(e)}"


def create_360_video(input_video_path: str, output_video_path: str,
                    projection_type: str = "equirectangular",
                    input_format: str = "fisheye",
                    fov: float = 360.0,
                    stabilization: bool = True,
                    output_resolution: str = "3840x1920") -> str:
    """
    Convert or create 360-degree video with proper projection.
    
    Args:
        input_video_path: Path to the input video file
        output_video_path: Path for the output video file
        projection_type: Output projection ("equirectangular", "cubemap", "fisheye")
        input_format: Input video format ("fisheye", "dual_fisheye", "equirectangular")
        fov: Field of view in degrees
        stabilization: Whether to apply 360 stabilization
        output_resolution: Output resolution for 360 video
    
    Returns:
        Success message with output file path
    """
    
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video file does not exist: {input_video_path}")
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        video_stream = input_stream.video
        
        # Get input dimensions
        probe = ffmpeg.probe(input_video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        input_width = int(video_info['width'])
        input_height = int(video_info['height'])
        
        output_width, output_height = map(int, output_resolution.split('x'))
        
        # Apply input format conversion
        if input_format == "fisheye":
            # Convert fisheye to equirectangular
            video_stream = video_stream.filter('v360',
                                             input='fisheye',
                                             output='equirectangular',
                                             h_fov=fov,
                                             v_fov=fov)
                                             
        elif input_format == "dual_fisheye":
            # Handle dual fisheye (side-by-side)
            # Split into two fisheye streams
            left_stream = video_stream.filter('crop', input_width//2, input_height, 0, 0)
            right_stream = video_stream.filter('crop', input_width//2, input_height, input_width//2, 0)
            
            # Convert each fisheye to equirectangular hemisphere
            left_stream = left_stream.filter('v360',
                                           input='fisheye',
                                           output='equirectangular',
                                           h_fov=180,
                                           v_fov=180)
            right_stream = right_stream.filter('v360',
                                            input='fisheye', 
                                            output='equirectangular',
                                            h_fov=180,
                                            v_fov=180)
            
            # Combine hemispheres
            video_stream = ffmpeg.filter([left_stream, right_stream], 'hstack')
            
        elif input_format == "equirectangular":
            # Already in correct format, just process
            pass
        
        # Apply output projection if different from equirectangular
        if projection_type == "cubemap":
            video_stream = video_stream.filter('v360',
                                             input='equirectangular',
                                             output='cubemap_3_2',
                                             h_fov=360,
                                             v_fov=180)
        elif projection_type == "fisheye":
            video_stream = video_stream.filter('v360',
                                             input='equirectangular',
                                             output='fisheye',
                                             h_fov=fov,
                                             v_fov=fov)
        
        # Scale to output resolution
        video_stream = video_stream.filter('scale', output_width, output_height)
        
        # Apply 360 stabilization
        if stabilization:
            # Use gyroscope-based stabilization if available
            video_stream = video_stream.filter('deshake',
                                             x=-1, y=-1, w=-1, h=-1,
                                             rx=64, ry=64,
                                             edge='blank')
        
        # Add 360 metadata for proper playback
        output = ffmpeg.output(video_stream, input_stream.audio, output_video_path,
                             vcodec='libx264', acodec='aac',
                             preset='medium', crf=18,
                             **{
                                 'movflags': '+faststart',
                                 'metadata:s:v:0': 'spherical-video=1',
                                 'metadata:s:v:0': 'stereo_mode=mono'
                             })
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully created 360° video ({projection_type}): {output_video_path}"
        
    except Exception as e:
        return f"Error creating 360 video: {str(e)}"


def create_cinemagraph(input_video_path: str, output_video_path: str,
                      static_mask_path: str = None,
                      motion_area: Dict = None,
                      loop_duration: float = 3.0,
                      smooth_loop: bool = True,
                      mask_feather: float = 10.0) -> str:
    """
    Create a cinemagraph where only part of the video moves while the rest is static.
    
    Args:
        input_video_path: Path to the input video file
        output_video_path: Path for the output video file
        static_mask_path: Path to mask image (white = static, black = moving)
        motion_area: Dictionary with motion area coordinates {'x', 'y', 'width', 'height'}
        loop_duration: Duration of the loop in seconds
        smooth_loop: Whether to create seamless loop
        mask_feather: Feathering amount for mask edges
    
    Returns:
        Success message with output file path
    """
    
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video file does not exist: {input_video_path}")
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        
        # Create static frame from first frame
        static_frame = input_stream.video.filter('select', 'eq(n,0)')
        static_frame = static_frame.filter('loop', loop=-1, size=1)
        
        # Create moving video loop
        moving_video = input_stream.video.filter('trim', duration=loop_duration)
        
        # Create seamless loop if requested
        if smooth_loop:
            # Crossfade the end with the beginning for smooth loop
            loop_frames = int(30 * loop_duration)  # Assume 30fps
            crossfade_frames = min(10, loop_frames // 4)
            
            # Extract end frames
            end_stream = moving_video.filter('select', f'gte(n,{loop_frames - crossfade_frames})')
            # Extract beginning frames
            start_stream = moving_video.filter('select', f'lt(n,{crossfade_frames})')
            
            # Crossfade end to beginning
            crossfaded = ffmpeg.filter([end_stream, start_stream], 'blend',
                                     mode='normal',
                                     opacity='(t/({}/30))'.format(crossfade_frames))
            
            # Replace end frames with crossfaded frames
            moving_video = moving_video.filter('select', f'lt(n,{loop_frames - crossfade_frames})')
            moving_video = ffmpeg.concat(moving_video, crossfaded, v=1, a=0)
        
        # Loop the moving video
        moving_video = moving_video.filter('loop', loop=-1, size=int(30 * loop_duration))
        
        # Create or apply mask
        if static_mask_path and os.path.exists(static_mask_path):
            # Load mask image
            mask_stream = ffmpeg.input(static_mask_path, loop=1)
            
            # Get video dimensions to scale mask
            probe = ffmpeg.probe(input_video_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            width = int(video_info['width'])
            height = int(video_info['height'])
            
            mask_stream = mask_stream.filter('scale', width, height)
            
            # Apply feathering to mask
            if mask_feather > 0:
                mask_stream = mask_stream.filter('boxblur', mask_feather)
            
            # Use mask to blend static and moving parts
            video_stream = ffmpeg.filter([static_frame, moving_video, mask_stream], 'maskedmerge')
            
        elif motion_area:
            # Create rectangular motion area
            x = motion_area.get('x', 0)
            y = motion_area.get('y', 0)
            w = motion_area.get('width', 100)
            h = motion_area.get('height', 100)
            
            # Crop moving area
            moving_crop = moving_video.filter('crop', w, h, x, y)
            
            # Overlay moving area on static frame
            video_stream = ffmpeg.overlay(static_frame, moving_crop, x=x, y=y)
            
            # Apply feathering to edges
            if mask_feather > 0:
                # Create soft edge mask
                probe = ffmpeg.probe(input_video_path)
                video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
                width = int(video_info['width'])
                height = int(video_info['height'])
                
                # Generate gradient mask for feathering
                mask_color = f'color=white:size={w}x{h}'
                soft_mask = ffmpeg.input(mask_color, f='lavfi')
                soft_mask = soft_mask.filter('pad', width, height, x, y, 'black')
                soft_mask = soft_mask.filter('boxblur', mask_feather)
                
                # Apply soft blending
                video_stream = ffmpeg.filter([static_frame, video_stream, soft_mask], 'maskedmerge')
        else:
            # Default: use entire frame as moving (simple loop)
            video_stream = moving_video
        
        # Output without audio for cinemagraph
        output = ffmpeg.output(video_stream, output_video_path,
                             vcodec='libx264',
                             preset='medium', crf=18,
                             pix_fmt='yuv420p',
                             **{'movflags': '+faststart'})
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully created cinemagraph (loop: {loop_duration}s): {output_video_path}"
        
    except Exception as e:
        return f"Error creating cinemagraph: {str(e)}"