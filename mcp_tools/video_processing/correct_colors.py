
import ffmpeg

def correct_colors(input_video_path: str, output_video_path: str, 
                   brightness: float = 0.0, contrast: float = 1.0, 
                   saturation: float = 1.0, gamma: float = 1.0) -> str:
    """Adjusts the color properties of a video.

    Args:
        input_video_path: Path to the source video file.
        output_video_path: Path to save the color-corrected video.
        brightness: Brightness adjustment. Range: -1.0 to 1.0. Default: 0.0.
        contrast: Contrast adjustment. Range: -2.0 to 2.0. Default: 1.0.
        saturation: Saturation adjustment. Range: 0.0 to 3.0. Default: 1.0.
        gamma: Gamma adjustment. Range: 0.1 to 10.0. Default: 1.0.

    Returns:
        A status message indicating success or failure.
    """
    try:
        stream = ffmpeg.input(input_video_path)
        
        # Apply the 'eq' filter for color correction
        video_stream = stream.video.filter('eq', 
                                           brightness=brightness, 
                                           contrast=contrast, 
                                           saturation=saturation, 
                                           gamma=gamma)
        
        # Get the audio stream to pass it through
        audio_stream = stream.audio

        # Output the processed video and original audio
        ffmpeg.output(video_stream, audio_stream, output_video_path, acodec='copy').run(capture_stdout=True, capture_stderr=True)
        return f"Color correction applied successfully and saved to {output_video_path}"
    except ffmpeg.Error as e:
        # Fallback if audio copy fails
        try:
            stream = ffmpeg.input(input_video_path)
            video_stream = stream.video.filter('eq', 
                                               brightness=brightness, 
                                               contrast=contrast, 
                                               saturation=saturation, 
                                               gamma=gamma)
            ffmpeg.output(video_stream, stream.audio, output_video_path).run(capture_stdout=True, capture_stderr=True)
            return f"Color correction applied successfully (audio re-encoded) and saved to {output_video_path}"
        except ffmpeg.Error as e_recode:
            error_message = e_recode.stderr.decode('utf8') if e_recode.stderr else str(e_recode)
            return f"Error applying color correction: {error_message}"
    except FileNotFoundError:
        return f"Error: Input video file not found at {input_video_path}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
