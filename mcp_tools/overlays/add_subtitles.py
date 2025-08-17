
import ffmpeg
import os

def add_subtitles(video_path: str, srt_file_path: str, output_video_path: str, font_style: dict = None) -> str:
    """Burns subtitles from an SRT file onto a video, with optional styling.

    Args:
        video_path: Path to the input video file.
        srt_file_path: Path to the SRT subtitle file.
        output_video_path: Path to save the video with subtitles.
        font_style (dict, optional): A dictionary for subtitle styling. 
            Supported keys and example values:
            - 'font_name': 'Arial' (str)
            - 'font_size': 24 (int)
            - 'font_color': 'white' or '&H00FFFFFF' (str, FFmpeg color syntax)
            - 'outline_color': 'black' or '&H00000000' (str)
            - 'outline_width': 2 (int)
            - 'shadow_color': 'black' (str)
            - 'shadow_offset_x': 1 (int)
            - 'shadow_offset_y': 1 (int)
            - 'alignment': 7 (int, ASS alignment - Numpad layout: 1=bottom-left, 7=top-left etc. Default often 2=bottom-center)
            - 'margin_v': 10 (int, vertical margin from edge, depends on alignment)
            - 'margin_l': 10 (int, left margin)
            - 'margin_r': 10 (int, right margin)
            Default is None, which uses FFmpeg's default subtitle styling.

    Returns:
        A status message indicating success or failure.
    """
    try:
        # Basic validation for file existence
        if not os.path.exists(video_path):
            return f"Error: Input video file not found at {video_path}"
        if not os.path.exists(srt_file_path):
            return f"Error: SRT subtitle file not found at {srt_file_path}"

        input_stream = ffmpeg.input(video_path)
        
        style_args = []
        if font_style:
            if 'font_name' in font_style: style_args.append(f"FontName={font_style['font_name']}")
            if 'font_size' in font_style: style_args.append(f"FontSize={font_style['font_size']}")
            if 'font_color' in font_style: style_args.append(f"PrimaryColour={font_style['font_color']}")
            if 'outline_color' in font_style: style_args.append(f"OutlineColour={font_style['outline_color']}")
            if 'outline_width' in font_style: style_args.append(f"Outline={font_style['outline_width']}") # Outline thickness
            if 'shadow_color' in font_style: style_args.append(f"ShadowColour={font_style['shadow_color']}")
            if 'shadow_offset_x' in font_style or 'shadow_offset_y' in font_style:
                # FFmpeg 'Shadow' is more like a distance. Outline might be better for simple shadow.
                # For more control, ASS uses ShadowX, ShadowY. Let's use 'Shadow' for simplicity if only one is given.
                shadow_val = font_style.get('shadow_offset_x', font_style.get('shadow_offset_y', 1))
                style_args.append(f"Shadow={shadow_val}")
            if 'alignment' in font_style: style_args.append(f"Alignment={font_style['alignment']}")
            if 'margin_v' in font_style: style_args.append(f"MarginV={font_style['margin_v']}")
            if 'margin_l' in font_style: style_args.append(f"MarginL={font_style['margin_l']}")
            if 'margin_r' in font_style: style_args.append(f"MarginR={font_style['margin_r']}")
            # Add more style mappings as needed based on FFmpeg/ASS capabilities

        vf_filter_value = f"subtitles='{srt_file_path}'"
        if style_args:
            vf_filter_value += f":force_style='{','.join(style_args)}'"

        # Attempt to copy audio codec to speed up processing if possible
        output_stream = input_stream.output(output_video_path, vf=vf_filter_value, acodec='copy')
        try:
            output_stream.run(capture_stdout=True, capture_stderr=True)
            return f"Subtitles added successfully (audio copied) to {output_video_path}"
        except ffmpeg.Error as e_acopy:
            # Fallback to re-encoding audio if audio copy failed
            output_stream_recode_audio = input_stream.output(output_video_path, vf=vf_filter_value)
            try:
                output_stream_recode_audio.run(capture_stdout=True, capture_stderr=True)
                return f"Subtitles added successfully (audio re-encoded) to {output_video_path}"
            except ffmpeg.Error as e_recode_all:
                err_acopy_msg = e_acopy.stderr.decode('utf8') if e_acopy.stderr else str(e_acopy)
                err_recode_msg = e_recode_all.stderr.decode('utf8') if e_recode_all.stderr else str(e_recode_all)
                return f"Error adding subtitles. Audio copy attempt: {err_acopy_msg}. Full re-encode attempt: {err_recode_msg}"

    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error adding subtitles: {error_message}"
    except FileNotFoundError: # This might be redundant if checked above, but good for safety.
        return f"Error: A specified file was not found."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
