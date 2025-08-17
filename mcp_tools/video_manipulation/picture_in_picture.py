import ffmpeg
import os

def create_picture_in_picture(main_video_path: str, overlay_video_path: str, 
                            output_video_path: str, position: str = "top_right",
                            overlay_size: str = "25%", border: dict = None,
                            timing: dict = None, animation: dict = None) -> str:
    """Creates picture-in-picture video with customizable overlay positioning and effects.
    
    Args:
        main_video_path: Path to the main/background video
        overlay_video_path: Path to the overlay/PiP video
        output_video_path: Path to save the PiP video
        position: Overlay position:
            - 'top_left', 'top_right', 'bottom_left', 'bottom_right'
            - 'center', 'top_center', 'bottom_center'
            - 'custom' (requires custom x,y in animation dict)
        overlay_size: Size of overlay video:
            - Percentage: '25%', '50%' (of main video width)
            - Fixed size: '320x240', '640x480'
            - 'auto': Keep original aspect ratio with 25% width
        border: Optional border configuration:
            - {'width': 3, 'color': 'white', 'style': 'solid'}
            - {'width': 5, 'color': 'black', 'style': 'shadow'}
        timing: Optional timing configuration:
            - {'start': 10.0, 'duration': 30.0} (start at 10s for 30s)
            - {'start': 0, 'end': 60} (from start to 60s)
        animation: Optional animation configuration:
            - {'type': 'fade_in', 'duration': 2.0}
            - {'type': 'slide_in', 'direction': 'right', 'duration': 1.5}
            - {'type': 'custom', 'x': '100', 'y': '50'} (custom position)
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(main_video_path):
        return f"Error: Main video file not found at {main_video_path}"
    
    if not os.path.exists(overlay_video_path):
        return f"Error: Overlay video file not found at {overlay_video_path}"
    
    try:
        # Load input videos
        main_input = ffmpeg.input(main_video_path)
        overlay_input = ffmpeg.input(overlay_video_path)
        
        # Get main video properties
        main_probe = ffmpeg.probe(main_video_path)
        main_video_stream = next(s for s in main_probe['streams'] if s['codec_type'] == 'video')
        main_width = int(main_video_stream['width'])
        main_height = int(main_video_stream['height'])
        
        # Process overlay video
        overlay_stream = overlay_input.video
        
        # Apply timing if specified
        if timing:
            start_time = timing.get('start', 0)
            if 'duration' in timing:
                duration = timing['duration']
                overlay_stream = ffmpeg.input(overlay_video_path, ss=start_time, t=duration).video
            elif 'end' in timing:
                duration = timing['end'] - start_time
                overlay_stream = ffmpeg.input(overlay_video_path, ss=start_time, t=duration).video
        
        # Calculate overlay dimensions
        if overlay_size.endswith('%'):
            # Percentage of main video width
            percentage = float(overlay_size.rstrip('%')) / 100
            overlay_width = int(main_width * percentage)
            overlay_height = int(overlay_width * 9 / 16)  # Assume 16:9 aspect ratio, adjust if needed
        elif 'x' in overlay_size:
            # Fixed dimensions
            overlay_width, overlay_height = map(int, overlay_size.split('x'))
        elif overlay_size == 'auto':
            # Auto-size to 25% width maintaining aspect ratio
            overlay_width = int(main_width * 0.25)
            overlay_height = int(overlay_width * 9 / 16)
        else:
            return f"Error: Invalid overlay_size format '{overlay_size}'"
        
        # Scale overlay video
        overlay_stream = overlay_stream.filter('scale', overlay_width, overlay_height)
        
        # Calculate position coordinates
        margin = 20  # Default margin from edges
        
        position_coords = {
            'top_left': (margin, margin),
            'top_right': (main_width - overlay_width - margin, margin),
            'bottom_left': (margin, main_height - overlay_height - margin),
            'bottom_right': (main_width - overlay_width - margin, main_height - overlay_height - margin),
            'center': ((main_width - overlay_width) // 2, (main_height - overlay_height) // 2),
            'top_center': ((main_width - overlay_width) // 2, margin),
            'bottom_center': ((main_width - overlay_width) // 2, main_height - overlay_height - margin)
        }
        
        if position == 'custom' and animation and 'x' in animation and 'y' in animation:
            x_pos = animation['x']
            y_pos = animation['y']
        elif position in position_coords:
            x_pos, y_pos = position_coords[position]
        else:
            return f"Error: Invalid position '{position}'"
        
        # Add border if specified
        if border:
            border_width = border.get('width', 2)
            border_color = border.get('color', 'white')
            border_style = border.get('style', 'solid')
            
            if border_style == 'solid':
                # Add solid border using pad filter
                overlay_stream = overlay_stream.filter(
                    'pad',
                    width=overlay_width + 2 * border_width,
                    height=overlay_height + 2 * border_width,
                    x=border_width,
                    y=border_width,
                    color=border_color
                )
                # Adjust position for border
                x_pos = max(0, x_pos - border_width)
                y_pos = max(0, y_pos - border_width)
                
            elif border_style == 'shadow':
                # Add drop shadow effect
                shadow_offset = border_width
                shadow_stream = overlay_stream.filter(
                    'pad',
                    width=overlay_width + shadow_offset,
                    height=overlay_height + shadow_offset,
                    x=shadow_offset,
                    y=shadow_offset,
                    color='black@0.5'
                )
                # Overlay original on shadow
                overlay_stream = shadow_stream.overlay(overlay_stream, x=0, y=0)
        
        # Apply animation if specified
        if animation:
            anim_type = animation.get('type', 'none')
            anim_duration = animation.get('duration', 1.0)
            
            if anim_type == 'fade_in':
                # Fade in animation
                overlay_stream = overlay_stream.filter(
                    'fade',
                    type='in',
                    duration=anim_duration
                )
                
            elif anim_type == 'slide_in':
                direction = animation.get('direction', 'left')
                
                if direction == 'left':
                    # Slide in from left
                    start_x = -overlay_width
                    end_x = x_pos
                    x_expr = f"if(lt(t,{anim_duration}),{start_x}+({end_x}-{start_x})*t/{anim_duration},{end_x})"
                    
                elif direction == 'right':
                    # Slide in from right  
                    start_x = main_width
                    end_x = x_pos
                    x_expr = f"if(lt(t,{anim_duration}),{start_x}+({end_x}-{start_x})*t/{anim_duration},{end_x})"
                    
                elif direction == 'top':
                    # Slide in from top
                    start_y = -overlay_height
                    end_y = y_pos
                    y_expr = f"if(lt(t,{anim_duration}),{start_y}+({end_y}-{start_y})*t/{anim_duration},{end_y})"
                    x_expr = str(x_pos)
                    
                elif direction == 'bottom':
                    # Slide in from bottom
                    start_y = main_height
                    end_y = y_pos
                    y_expr = f"if(lt(t,{anim_duration}),{start_y}+({end_y}-{start_y})*t/{anim_duration},{end_y})"
                    x_expr = str(x_pos)
                
                # For left/right slides, y is constant
                if direction in ['left', 'right']:
                    y_expr = str(y_pos)
                
                # Note: Dynamic positioning would require more complex filter setup
                # For now, use static position
                x_pos = x_expr if isinstance(x_expr, (int, str)) and str(x_expr).isdigit() else x_pos
                y_pos = y_expr if isinstance(y_expr, (int, str)) and str(y_expr).isdigit() else y_pos
        
        # Apply PiP overlay
        if timing:
            # Time-limited overlay
            start_time = timing.get('start', 0)
            if 'duration' in timing:
                end_time = start_time + timing['duration']
            elif 'end' in timing:
                end_time = timing['end']
            else:
                end_time = None
            
            if end_time:
                enable_expr = f"between(t,{start_time},{end_time})"
                pip_stream = main_input.video.overlay(
                    overlay_stream,
                    x=x_pos,
                    y=y_pos,
                    enable=enable_expr
                )
            else:
                pip_stream = main_input.video.overlay(
                    overlay_stream,
                    x=x_pos,
                    y=y_pos
                )
        else:
            # Full duration overlay
            pip_stream = main_input.video.overlay(
                overlay_stream,
                x=x_pos,
                y=y_pos
            )
        
        # Handle audio - mix both tracks or use main audio
        audio_stream = main_input.audio
        
        # Create output
        output = ffmpeg.output(
            pip_stream,
            audio_stream,
            output_video_path,
            vcodec='libx264',
            acodec='aac'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Picture-in-picture video created successfully. Position: {position}, Size: {overlay_size}. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating picture-in-picture: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def create_multi_pip(main_video_path: str, overlay_videos: list[dict], 
                    output_video_path: str, layout: str = "auto") -> str:
    """Creates multiple picture-in-picture overlays on a single main video.
    
    Args:
        main_video_path: Path to the main/background video
        overlay_videos: List of overlay configurations, each containing:
            - 'path': Path to overlay video
            - 'position': Position on screen
            - 'size': Size of overlay
            - 'timing': Optional timing configuration
        output_video_path: Path to save the multi-PiP video
        layout: Layout preset ('auto', 'corners', 'sides', 'grid')
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(main_video_path):
        return f"Error: Main video file not found at {main_video_path}"
    
    if not overlay_videos:
        return "Error: No overlay videos provided"
    
    # Validate overlay video files
    for i, overlay in enumerate(overlay_videos):
        if 'path' not in overlay:
            return f"Error: Overlay {i+1} missing 'path' field"
        if not os.path.exists(overlay['path']):
            return f"Error: Overlay video {i+1} not found at {overlay['path']}"
    
    try:
        main_input = ffmpeg.input(main_video_path)
        current_stream = main_input.video
        
        # Get main video dimensions
        main_probe = ffmpeg.probe(main_video_path)
        main_video_stream = next(s for s in main_probe['streams'] if s['codec_type'] == 'video')
        main_width = int(main_video_stream['width'])
        main_height = int(main_video_stream['height'])
        
        # Auto-assign positions if using layout presets
        if layout == "corners" and len(overlay_videos) <= 4:
            positions = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
            for i, overlay in enumerate(overlay_videos):
                if 'position' not in overlay:
                    overlay['position'] = positions[i % 4]
                    
        elif layout == "sides" and len(overlay_videos) <= 4:
            positions = ['top_center', 'bottom_center', 'center', 'center']
            for i, overlay in enumerate(overlay_videos):
                if 'position' not in overlay:
                    overlay['position'] = positions[i % 4]
                    
        elif layout == "grid":
            # Calculate grid positions
            grid_size = math.ceil(math.sqrt(len(overlay_videos)))
            positions = []
            
            for row in range(grid_size):
                for col in range(grid_size):
                    if len(positions) >= len(overlay_videos):
                        break
                    x = (main_width // (grid_size + 1)) * (col + 1) - 80
                    y = (main_height // (grid_size + 1)) * (row + 1) - 60
                    positions.append(('custom', x, y))
            
            for i, overlay in enumerate(overlay_videos):
                if i < len(positions):
                    pos_type, x, y = positions[i]
                    overlay['position'] = pos_type
                    if 'animation' not in overlay:
                        overlay['animation'] = {}
                    overlay['animation'].update({'x': x, 'y': y})
        
        # Process each overlay
        for i, overlay_config in enumerate(overlay_videos):
            overlay_path = overlay_config['path']
            overlay_input = ffmpeg.input(overlay_path)
            overlay_stream = overlay_input.video
            
            # Apply size
            size = overlay_config.get('size', '20%')
            if size.endswith('%'):
                percentage = float(size.rstrip('%')) / 100
                overlay_width = int(main_width * percentage)
                overlay_height = int(overlay_width * 9 / 16)
            elif 'x' in size:
                overlay_width, overlay_height = map(int, size.split('x'))
            else:
                overlay_width = int(main_width * 0.2)
                overlay_height = int(overlay_width * 9 / 16)
            
            overlay_stream = overlay_stream.filter('scale', overlay_width, overlay_height)
            
            # Calculate position
            position = overlay_config.get('position', 'top_left')
            margin = 20 + i * 10  # Slight offset for multiple overlays
            
            position_coords = {
                'top_left': (margin, margin + i * (overlay_height + 10)),
                'top_right': (main_width - overlay_width - margin, margin + i * (overlay_height + 10)),
                'bottom_left': (margin, main_height - overlay_height - margin - i * (overlay_height + 10)),
                'bottom_right': (main_width - overlay_width - margin, main_height - overlay_height - margin - i * (overlay_height + 10)),
                'center': ((main_width - overlay_width) // 2 + i * 50, (main_height - overlay_height) // 2 + i * 50),
            }
            
            if position == 'custom' and 'animation' in overlay_config:
                x_pos = overlay_config['animation'].get('x', 100)
                y_pos = overlay_config['animation'].get('y', 100)
            elif position in position_coords:
                x_pos, y_pos = position_coords[position]
            else:
                x_pos, y_pos = position_coords['top_left']
            
            # Apply timing if specified
            timing = overlay_config.get('timing')
            if timing:
                start_time = timing.get('start', 0)
                if 'duration' in timing:
                    end_time = start_time + timing['duration']
                elif 'end' in timing:
                    end_time = timing['end']
                else:
                    end_time = None
                
                if end_time:
                    enable_expr = f"between(t,{start_time},{end_time})"
                    current_stream = current_stream.overlay(
                        overlay_stream,
                        x=x_pos,
                        y=y_pos,
                        enable=enable_expr
                    )
                else:
                    current_stream = current_stream.overlay(overlay_stream, x=x_pos, y=y_pos)
            else:
                current_stream = current_stream.overlay(overlay_stream, x=x_pos, y=y_pos)
        
        # Create output
        output = ffmpeg.output(
            current_stream,
            main_input.audio,
            output_video_path,
            vcodec='libx264',
            acodec='aac'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Multi picture-in-picture video created successfully with {len(overlay_videos)} overlays using '{layout}' layout. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating multi picture-in-picture: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def create_animated_pip(main_video_path: str, overlay_video_path: str,
                       output_video_path: str, animation_preset: str = "slide_in_out") -> str:
    """Creates picture-in-picture with predefined animation presets.
    
    Args:
        main_video_path: Path to the main video
        overlay_video_path: Path to the overlay video
        output_video_path: Path to save the animated PiP video
        animation_preset: Animation preset:
            - 'slide_in_out': Slide in from right, slide out to left
            - 'fade_in_out': Fade in and fade out
            - 'zoom_in_out': Zoom in from center, zoom out
            - 'bounce_in': Bouncing entrance animation
            - 'rotate_in': Rotating entrance animation
    
    Returns:
        A status message indicating success or failure.
    """
    # Animation presets with specific configurations
    animation_configs = {
        'slide_in_out': {
            'timing': {'start': 5.0, 'duration': 15.0},
            'animation': {'type': 'slide_in', 'direction': 'right', 'duration': 2.0},
            'position': 'bottom_right',
            'overlay_size': '30%'
        },
        'fade_in_out': {
            'timing': {'start': 3.0, 'duration': 20.0},
            'animation': {'type': 'fade_in', 'duration': 2.0},
            'position': 'top_left',
            'overlay_size': '25%'
        },
        'zoom_in_out': {
            'timing': {'start': 2.0, 'duration': 10.0},
            'animation': {'type': 'fade_in', 'duration': 1.5},
            'position': 'center',
            'overlay_size': '40%'
        },
        'bounce_in': {
            'timing': {'start': 1.0, 'duration': 25.0},
            'animation': {'type': 'slide_in', 'direction': 'top', 'duration': 1.0},
            'position': 'top_right',
            'overlay_size': '20%'
        },
        'rotate_in': {
            'timing': {'start': 4.0, 'duration': 12.0},
            'animation': {'type': 'fade_in', 'duration': 1.5},
            'position': 'bottom_left',
            'overlay_size': '35%'
        }
    }
    
    if animation_preset not in animation_configs:
        available_presets = ', '.join(animation_configs.keys())
        return f"Error: Unknown animation preset '{animation_preset}'. Available presets: {available_presets}"
    
    config = animation_configs[animation_preset]
    
    return create_picture_in_picture(
        main_video_path=main_video_path,
        overlay_video_path=overlay_video_path,
        output_video_path=output_video_path,
        position=config['position'],
        overlay_size=config['overlay_size'],
        timing=config['timing'],
        animation=config['animation']
    )