
import ffmpeg

def change_aspect_ratio(video_path: str, output_video_path: str, target_aspect_ratio: str, 
                          resize_mode: str = 'pad', padding_color: str = 'black') -> str:
    """Changes the aspect ratio of a video, using padding or cropping.
    Args listed in PRD.
    Returns:
        A status message indicating success or failure.
    """
    try:
        probe = ffmpeg.probe(video_path)
        video_stream_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if not video_stream_info:
            return "Error: No video stream found in the input file."

        original_width = int(video_stream_info['width'])
        original_height = int(video_stream_info['height'])

        num, den = map(int, target_aspect_ratio.split(':'))
        target_ar_val = num / den
        original_ar_val = original_width / original_height

        vf_filter = ""
        # Attempt to copy codecs if the operation doesn't strictly require re-encoding video stream
        # This is mostly for padding. Cropping implies re-encoding the video stream.
        codec_to_use = None 

        if resize_mode == 'pad':
            if abs(original_ar_val - target_ar_val) < 1e-4:
                try:
                    ffmpeg.input(video_path).output(output_video_path, c='copy').run(capture_stdout=True, capture_stderr=True)
                    return f"Video aspect ratio already matches. Copied to {output_video_path}."
                except ffmpeg.Error:
                     # If copy fails, just re-encode
                    ffmpeg.input(video_path).output(output_video_path).run(capture_stdout=True, capture_stderr=True)
                    return f"Video aspect ratio already matches. Re-encoded to {output_video_path}."
            
            if original_ar_val > target_ar_val: 
                final_w = int(original_height * target_ar_val)
                final_h = original_height
                vf_filter = f"scale={final_w}:{final_h}:force_original_aspect_ratio=decrease,pad={final_w}:{final_h}:(ow-iw)/2:(oh-ih)/2:{padding_color}"
            else: 
                final_w = original_width
                final_h = int(original_width / target_ar_val)
                vf_filter = f"scale={final_w}:{final_h}:force_original_aspect_ratio=decrease,pad={final_w}:{final_h}:(ow-iw)/2:(oh-ih)/2:{padding_color}"
            codec_to_use = 'copy' # Try to copy for padding, audio will be copied too

        elif resize_mode == 'crop':
            if abs(original_ar_val - target_ar_val) < 1e-4:
                try:
                    ffmpeg.input(video_path).output(output_video_path, c='copy').run(capture_stdout=True, capture_stderr=True)
                    return f"Video aspect ratio already matches. Copied to {output_video_path}."
                except ffmpeg.Error:
                    ffmpeg.input(video_path).output(output_video_path).run(capture_stdout=True, capture_stderr=True)
                    return f"Video aspect ratio already matches. Re-encoded to {output_video_path}."
            
            if original_ar_val > target_ar_val: 
                new_width = int(original_height * target_ar_val)
                vf_filter = f"crop={new_width}:{original_height}:(iw-{new_width})/2:0"
            else: 
                new_height = int(original_width / target_ar_val)
                vf_filter = f"crop={original_width}:{new_height}:0:(ih-{new_height})/2"
        else:
            return f"Error: Invalid resize_mode '{resize_mode}'. Must be 'pad' or 'crop'."
        
        try:
            # Try with specified video filter and copying audio codec
            ffmpeg.input(video_path).output(output_video_path, vf=vf_filter, acodec='copy').run(capture_stdout=True, capture_stderr=True)
            return f"Video aspect ratio changed (audio copy) to {target_aspect_ratio} using {resize_mode}. Saved to {output_video_path}"
        except ffmpeg.Error as e_acopy:
            # Fallback to re-encoding audio if audio copy failed
            try:
                ffmpeg.input(video_path).output(output_video_path, vf=vf_filter).run(capture_stdout=True, capture_stderr=True)
                return f"Video aspect ratio changed (audio re-encoded) to {target_aspect_ratio} using {resize_mode}. Saved to {output_video_path}"
            except ffmpeg.Error as e_recode_all:
                err_acopy_msg = e_acopy.stderr.decode('utf8') if e_acopy.stderr else str(e_acopy)
                err_recode_msg = e_recode_all.stderr.decode('utf8') if e_recode_all.stderr else str(e_recode_all)
                return f"Error changing aspect ratio. Audio copy attempt failed: {err_acopy_msg}. Full re-encode attempt also failed: {err_recode_msg}."

    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error changing aspect ratio: {error_message}"
    except FileNotFoundError:
        return f"Error: Input video file not found at {video_path}"
    except ValueError:
        return f"Error: Invalid target_aspect_ratio format. Expected 'num:den' (e.g., '16:9')."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
