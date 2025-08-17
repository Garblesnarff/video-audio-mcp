
import ffmpeg
import os

def add_image_overlay(video_path: str, output_video_path: str, image_path: str, 
                        position: str = 'top_right', opacity: float = None, 
                        start_time: str = None, end_time: str = None, 
                        width: str = None, height: str = None) -> str:
    """Adds an image overlay (watermark/logo) to a video.

    Args:
        video_path: Path to the input video file.
        output_video_path: Path to save the video with the image overlay.
        image_path: Path to the image file for the overlay.
        position: Position of the overlay. 
            Options: 'top_left', 'top_right', 'bottom_left', 'bottom_right', 'center'. 
            Or specify custom coordinates like 'x=10:y=10'.
        opacity: Opacity of the overlay (0.0 to 1.0). If None, image's own alpha is used.
        start_time: Start time for the overlay (HH:MM:SS or seconds). If None, starts from beginning.
        end_time: End time for the overlay (HH:MM:SS or seconds). If None, lasts till end.
        width: Width for the overlay image (e.g., '100', 'iw*0.1'). Original if None.
        height: Height for the overlay image (e.g., '50', 'ih*0.1'). Original if None.

    Returns:
        A status message indicating success or failure.
    """
    try:
        if not os.path.exists(video_path):
            return f"Error: Input video file not found at {video_path}"
        if not os.path.exists(image_path):
            return f"Error: Overlay image file not found at {image_path}"

        main_input = ffmpeg.input(video_path)
        overlay_input = ffmpeg.input(image_path)
        
        # Process the overlay image (scale, opacity)
        processed_overlay = overlay_input
        
        # Apply scaling if requested
        if width or height:
            scale_params = {}
            if width: scale_params['width'] = width
            if height: scale_params['height'] = height
            if width and not height: scale_params['height'] = '-1'  # Auto-height maintaining aspect
            if height and not width: scale_params['width'] = '-1'  # Auto-width maintaining aspect
            processed_overlay = processed_overlay.filter('scale', **scale_params)

        # Apply opacity if requested
        if opacity is not None and 0.0 <= opacity <= 1.0:
            # Ensure image has alpha channel, then apply opacity
            processed_overlay = processed_overlay.filter('format', 'rgba')  # Ensure alpha channel exists
            processed_overlay = processed_overlay.filter('colorchannelmixer', aa=str(opacity))

        # Determine overlay position coordinates
        overlay_x_pos = '0'
        overlay_y_pos = '0'
        if position == 'top_left':
            overlay_x_pos, overlay_y_pos = '10', '10'
        elif position == 'top_right':
            overlay_x_pos, overlay_y_pos = 'main_w-overlay_w-10', '10'
        elif position == 'bottom_left':
            overlay_x_pos, overlay_y_pos = '10', 'main_h-overlay_h-10'
        elif position == 'bottom_right':
            overlay_x_pos, overlay_y_pos = 'main_w-overlay_w-10', 'main_h-overlay_h-10'
        elif position == 'center':
            overlay_x_pos, overlay_y_pos = '(main_w-overlay_w)/2', '(main_h-overlay_h)/2'
        elif ':' in position:
            pos_parts = position.split(':')
            for part in pos_parts:
                if part.startswith('x='): overlay_x_pos = part.split('=')[1]
                if part.startswith('y='): overlay_y_pos = part.split('=')[1]

        # Prepare overlay filter parameters
        overlay_filter_kwargs = {'x': overlay_x_pos, 'y': overlay_y_pos}
        
        # Add time-based enabling condition if specified
        if start_time is not None or end_time is not None:
            actual_start_time = start_time if start_time is not None else '0'
            if end_time is not None:
                enable_expr = f"between(t,{actual_start_time},{end_time})"
            else:  # Only start_time is provided
                enable_expr = f"gte(t,{actual_start_time})"
            overlay_filter_kwargs['enable'] = enable_expr

        try:
            # Attempt 1: Create overlay with audio copying
            video_with_overlay = ffmpeg.filter([main_input, processed_overlay], 'overlay', **overlay_filter_kwargs)
            output_node = ffmpeg.output(video_with_overlay, main_input.audio, output_video_path, acodec='copy')
            output_node.run(capture_stdout=True, capture_stderr=True)
            return f"Image overlay added successfully (audio copied) to {output_video_path}"
        except ffmpeg.Error as e_acopy:
            try:
                # Attempt 2: Re-encode audio if copying fails
                # We need to reconstruct the filter chain
                video_with_overlay_fallback = ffmpeg.filter([main_input, processed_overlay], 'overlay', **overlay_filter_kwargs)
                output_node_fallback = ffmpeg.output(video_with_overlay_fallback, main_input.audio, output_video_path)
                output_node_fallback.run(capture_stdout=True, capture_stderr=True)
                return f"Image overlay added successfully (audio re-encoded) to {output_video_path}"
            except ffmpeg.Error as e_recode:
                err_acopy_msg = e_acopy.stderr.decode('utf8') if e_acopy.stderr else str(e_acopy)
                err_recode_msg = e_recode.stderr.decode('utf8') if e_recode.stderr else str(e_recode)
                return f"Error adding image overlay. Audio copy attempt: {err_acopy_msg}. Full re-encode attempt: {err_recode_msg}"

    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error processing image overlay: {error_message}"
    except FileNotFoundError:
        return f"Error: An input file was not found (video: '{video_path}', image: '{image_path}'). Please check paths."
    except Exception as e:
        return f"An unexpected error occurred in add_image_overlay: {str(e)}"
