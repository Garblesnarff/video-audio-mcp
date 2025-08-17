import ffmpeg
import os

def add_text_overlay(video_path: str, output_video_path: str, text_elements: list[dict]) -> str:
    """Adds one or more text overlays to a video at specified times and positions.

    Args:
        video_path: Path to the input main video file.
        output_video_path: Path to save the video with text overlays.
        text_elements: A list of dictionaries, where each dictionary defines a text overlay.
            Required keys for each text_element dict:
            - 'text': str - The text to display.
            - 'start_time': str or float - Start time (HH:MM:SS, or seconds).
            - 'end_time': str or float - End time (HH:MM:SS, or seconds).
            Optional keys for each text_element dict:
            - 'font_size': int (default: 24)
            - 'font_color': str (default: 'white')
            - 'x_pos': str or int (default: 'center')
            - 'y_pos': str or int (default: 'h-th-10')
            - 'box': bool (default: False)
            - 'box_color': str (default: 'black@0.5')
            - 'box_border_width': int (default: 0)
    Returns:
        A status message indicating success or failure.
    """
    try:
        if not os.path.exists(video_path):
            return f"Error: Input video file not found at {video_path}"
        if not text_elements:
            return "Error: No text elements provided for overlay."

        input_stream = ffmpeg.input(video_path)
        drawtext_filters = []

        for element in text_elements:
            text = element.get('text')
            start_time = element.get('start_time')
            end_time = element.get('end_time')

            if text is None or start_time is None or end_time is None:
                return f"Error: Text element is missing required keys (text, start_time, end_time)."
            
            # Thoroughly escape special characters in text
            # Escape single quotes, colons, commas, backslashes, and any other special chars
            safe_text = text.replace('\\', '\\\\').replace("'", "\\'").replace(':', '\\:').replace(',', '\\,')
            
            # Build filter parameters
            filter_params = [
                f"text='{safe_text}'",
                f"fontsize={element.get('font_size', 24)}",
                f"fontcolor={element.get('font_color', 'white')}",
                f"x={element.get('x_pos', '(w-text_w)/2')}",
                f"y={element.get('y_pos', 'h-text_h-10')}",
                f"enable=between(t\\,{start_time}\\,{end_time})"
            ]

            # Add box parameters if box is enabled
            if element.get('box', False):
                filter_params.append("box=1")
                filter_params.append(f"boxcolor={element.get('box_color', 'black@0.5')}")
                if 'box_border_width' in element:
                    filter_params.append(f"boxborderw={element['box_border_width']}")

            # Add font file if specified
            if 'font_file' in element:
                font_path = element['font_file'].replace('\\', '\\\\').replace("'", "\\'").replace(':', '\\:')
                filter_params.append(f"fontfile='{font_path}'")

            # Join all parameters with colons
            drawtext_filter = f"drawtext={':'.join(filter_params)}"
            drawtext_filters.append(drawtext_filter)

        # Join all drawtext filters with commas
        final_vf_filter = ','.join(drawtext_filters)

        try:
            # First attempt: try to copy audio codec
            stream = input_stream.output(output_video_path, vf=final_vf_filter, acodec='copy')
            stream.run(capture_stdout=True, capture_stderr=True)
            return f"Text overlays added successfully (audio copied) to {output_video_path}"
        except ffmpeg.Error as e_acopy:
            try:
                # Second attempt: re-encode audio if copying fails
                stream_recode = input_stream.output(output_video_path, vf=final_vf_filter)
                stream_recode.run(capture_stdout=True, capture_stderr=True)
                return f"Text overlays added successfully (audio re-encoded) to {output_video_path}"
            except ffmpeg.Error as e_recode_all:
                err_acopy_msg = e_acopy.stderr.decode('utf8') if e_acopy.stderr else str(e_acopy)
                err_recode_msg = e_recode_all.stderr.decode('utf8') if e_recode_all.stderr else str(e_recode_all)
                return f"Error adding text overlays. Audio copy attempt: {err_acopy_msg}. Full re-encode attempt: {err_recode_msg}"

    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error processing text overlays: {error_message}"
    except FileNotFoundError:
        return f"Error: Input video file not found."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
