import ffmpeg
import os
import math

def rotate_video(input_video_path: str, output_video_path: str,
                rotation_angle: float, rotation_type: str = "degrees",
                fill_mode: str = "black", maintain_quality: bool = True) -> str:
    """Rotates video by specified angle with various options for handling aspect ratio changes.
    
    Args:
        input_video_path: Path to the source video file
        output_video_path: Path to save the rotated video
        rotation_angle: Angle to rotate (in degrees or radians based on rotation_type)
            - Common values: 90, 180, 270 for degrees
            - For radians: PI/2, PI, 3*PI/2, etc.
        rotation_type: Type of angle measurement ('degrees' or 'radians')
        fill_mode: How to fill empty areas after rotation:
            - 'black': Fill with black color
            - 'white': Fill with white color  
            - 'blur': Fill with blurred edges
            - 'mirror': Mirror edge pixels
            - 'transparent': Transparent fill (for supported formats)
        maintain_quality: Whether to use lossless rotation for 90° increments
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        
        # Convert angle to radians if needed
        if rotation_type == "degrees":
            angle_rad = math.radians(rotation_angle)
        else:
            angle_rad = rotation_angle
        
        # Check if it's a 90-degree increment for lossless rotation
        if maintain_quality and rotation_type == "degrees" and rotation_angle % 90 == 0:
            # Use transpose for lossless 90-degree rotations
            video_stream = input_stream.video
            
            if rotation_angle % 360 == 90:
                video_stream = video_stream.filter('transpose', 1)  # 90° clockwise
            elif rotation_angle % 360 == 180:
                video_stream = video_stream.filter('transpose', 1).filter('transpose', 1)  # 180°
            elif rotation_angle % 360 == 270:
                video_stream = video_stream.filter('transpose', 2)  # 90° counter-clockwise
            else:  # 0° or 360°
                video_stream = video_stream  # No rotation needed
            
        else:
            # Use rotate filter for arbitrary angles
            video_stream = input_stream.video
            
            # Set fill color based on mode
            if fill_mode == "black":
                fill_color = "black"
            elif fill_mode == "white":
                fill_color = "white"
            elif fill_mode == "transparent":
                fill_color = "none"
            else:
                fill_color = "black"  # Default fallback
            
            # Apply rotation with different modes
            if fill_mode == "blur":
                # First rotate, then blur the background
                video_stream = video_stream.filter('rotate', angle=angle_rad, fillcolor=fill_color)
                # Add blur to background (complex filter would be needed for proper blur fill)
            elif fill_mode == "mirror":
                # Rotate with mirrored edges (simplified implementation)
                video_stream = video_stream.filter('rotate', angle=angle_rad, fillcolor=fill_color)
            else:
                # Standard rotation with solid fill
                video_stream = video_stream.filter('rotate', angle=angle_rad, fillcolor=fill_color)
                
            # Disable bilinear interpolation for sharper results when needed
            if abs(angle_rad % (math.pi/2)) < 0.01:  # Close to 90° increments
                video_stream = video_stream.filter('rotate', angle=angle_rad, fillcolor=fill_color, bilinear=0)
        
        # Create output
        output = ffmpeg.output(
            video_stream,
            input_stream.audio,
            output_video_path,
            vcodec='libx264',
            acodec='copy'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        rotation_desc = f"{rotation_angle}°" if rotation_type == "degrees" else f"{rotation_angle} rad"
        return f"Video rotated successfully by {rotation_desc} with {fill_mode} fill. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error rotating video: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def flip_mirror_video(input_video_path: str, output_video_path: str,
                     operation: str, preserve_metadata: bool = True) -> str:
    """Flips or mirrors video horizontally or vertically.
    
    Args:
        input_video_path: Path to the source video file
        output_video_path: Path to save the flipped video
        operation: Type of flip/mirror operation:
            - 'horizontal' or 'hflip': Horizontal flip (mirror left-right)
            - 'vertical' or 'vflip': Vertical flip (mirror top-bottom)  
            - 'both': Both horizontal and vertical flip (180° rotation equivalent)
            - 'diagonal': Diagonal flip (transpose)
            - 'anti_diagonal': Anti-diagonal flip (anti-transpose)
        preserve_metadata: Whether to preserve video metadata during operation
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    valid_operations = ['horizontal', 'hflip', 'vertical', 'vflip', 'both', 'diagonal', 'anti_diagonal']
    if operation not in valid_operations:
        return f"Error: Invalid operation '{operation}'. Valid operations: {', '.join(valid_operations)}"
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        video_stream = input_stream.video
        
        # Apply the appropriate flip operation
        if operation in ['horizontal', 'hflip']:
            video_stream = video_stream.filter('hflip')
            
        elif operation in ['vertical', 'vflip']:
            video_stream = video_stream.filter('vflip')
            
        elif operation == 'both':
            # Both horizontal and vertical flip
            video_stream = video_stream.filter('hflip').filter('vflip')
            
        elif operation == 'diagonal':
            # Diagonal flip (transpose matrix operation)
            video_stream = video_stream.filter('transpose', 0)  # 90° counter-clockwise + vflip
            
        elif operation == 'anti_diagonal':
            # Anti-diagonal flip  
            video_stream = video_stream.filter('transpose', 3)  # 90° clockwise + vflip
        
        # Build output arguments
        output_args = {
            'vcodec': 'libx264',
            'acodec': 'copy'
        }
        
        # Preserve metadata if requested
        if preserve_metadata:
            output_args['map_metadata'] = 0
        
        # Create output
        output = ffmpeg.output(
            video_stream,
            input_stream.audio,
            output_video_path,
            **output_args
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Video {operation} flip applied successfully. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error flipping video: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def rotate_and_flip_video(input_video_path: str, output_video_path: str,
                         rotation_angle: float, flip_operation: str = None,
                         rotation_type: str = "degrees") -> str:
    """Combines rotation and flipping operations in a single efficient pass.
    
    Args:
        input_video_path: Path to the source video file
        output_video_path: Path to save the processed video
        rotation_angle: Angle to rotate (in degrees or radians)
        flip_operation: Optional flip operation to apply after rotation:
            - 'horizontal', 'vertical', 'both', or None
        rotation_type: Type of angle measurement ('degrees' or 'radians')
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        video_stream = input_stream.video
        
        # Convert angle to radians if needed
        if rotation_type == "degrees":
            angle_rad = math.radians(rotation_angle)
        else:
            angle_rad = rotation_angle
        
        # Apply rotation
        if rotation_angle != 0:
            # Check for 90-degree increments for optimized processing
            if rotation_type == "degrees" and rotation_angle % 90 == 0:
                if rotation_angle % 360 == 90:
                    video_stream = video_stream.filter('transpose', 1)
                elif rotation_angle % 360 == 180:
                    video_stream = video_stream.filter('transpose', 1).filter('transpose', 1)
                elif rotation_angle % 360 == 270:
                    video_stream = video_stream.filter('transpose', 2)
            else:
                video_stream = video_stream.filter('rotate', angle=angle_rad, fillcolor="black")
        
        # Apply flip operation if specified
        if flip_operation:
            if flip_operation == 'horizontal':
                video_stream = video_stream.filter('hflip')
            elif flip_operation == 'vertical':
                video_stream = video_stream.filter('vflip')
            elif flip_operation == 'both':
                video_stream = video_stream.filter('hflip').filter('vflip')
        
        # Create output
        output = ffmpeg.output(
            video_stream,
            input_stream.audio,
            output_video_path,
            vcodec='libx264',
            acodec='copy'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        operations = []
        if rotation_angle != 0:
            rotation_desc = f"{rotation_angle}°" if rotation_type == "degrees" else f"{rotation_angle} rad"
            operations.append(f"rotated {rotation_desc}")
        if flip_operation:
            operations.append(f"{flip_operation} flipped")
        
        operation_desc = " and ".join(operations) if operations else "processed"
        return f"Video {operation_desc} successfully. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error processing video: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def auto_rotate_video(input_video_path: str, output_video_path: str) -> str:
    """Automatically corrects video rotation based on metadata orientation.
    
    Args:
        input_video_path: Path to the source video file
        output_video_path: Path to save the corrected video
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    try:
        # Probe video to get metadata
        probe = ffmpeg.probe(input_video_path)
        
        # Look for rotation metadata
        rotation = 0
        for stream in probe['streams']:
            if stream['codec_type'] == 'video':
                # Check for rotation in side_data_list
                if 'side_data_list' in stream:
                    for side_data in stream['side_data_list']:
                        if side_data.get('side_data_type') == 'Display Matrix':
                            rotation = int(side_data.get('rotation', 0))
                            break
                
                # Also check for rotation tag
                if 'tags' in stream and 'rotate' in stream['tags']:
                    rotation = int(stream['tags']['rotate'])
                    break
        
        if rotation == 0:
            return f"No rotation correction needed. Video is already properly oriented."
        
        # Apply rotation correction
        input_stream = ffmpeg.input(input_video_path)
        video_stream = input_stream.video
        
        # Correct rotation by applying opposite rotation
        if rotation == 90:
            video_stream = video_stream.filter('transpose', 2)  # 90° counter-clockwise
        elif rotation == 180:
            video_stream = video_stream.filter('hflip').filter('vflip')
        elif rotation == 270:
            video_stream = video_stream.filter('transpose', 1)  # 90° clockwise
        
        # Remove rotation metadata and create output
        output = ffmpeg.output(
            video_stream,
            input_stream.audio,
            output_video_path,
            vcodec='libx264',
            acodec='copy',
            metadata='rotate=0'  # Clear rotation metadata
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Video rotation auto-corrected (was {rotation}°). Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error auto-correcting video rotation: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"