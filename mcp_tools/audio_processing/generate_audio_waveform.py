
import ffmpeg
import os

def generate_audio_waveform(input_audio_path: str, output_image_path: str, 
                            width: int = 1920, height: int = 1080, 
                            colors: str = 'white', background_color: str = 'black') -> str:
    """Generates a waveform image from an audio file.

    Args:
        input_audio_path: Path to the source audio file.
        output_image_path: Path to save the generated waveform image (e.g., .png, .jpg).
        width: Width of the output image in pixels. Default: 1920.
        height: Height of the output image in pixels. Default: 1080.
        colors: Color of the waveform. Can be a single color name (e.g., 'white') or a comma-separated list for gradient.
        background_color: Background color of the image. Default: 'black'.

    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_audio_path):
        return f"Error: Input audio file not found at {input_audio_path}"

    try:
        # Construct the showwavespic filter string
        # Note: ffmpeg-python might not directly support all showwavespic options as kwargs.
        # We'll build the filter string manually.
        filter_str = f"showwavespic=s={width}x{height}:colors={colors}:bg_color={background_color}"

        ffmpeg.input(input_audio_path).output(output_image_path, 
                                              vf=filter_str, 
                                              vframes=1).run(capture_stdout=True, capture_stderr=True)
        
        return f"Audio waveform image generated successfully and saved to {output_image_path}"
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error generating audio waveform: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
