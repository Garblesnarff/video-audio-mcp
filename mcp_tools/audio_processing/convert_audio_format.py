
import ffmpeg

def convert_audio_format(input_audio_path: str, output_audio_path: str, target_format: str) -> str:
    """Converts an audio file to the specified target format.
    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the converted audio file.
        target_format: Desired output audio format (e.g., 'mp3', 'wav', 'aac').
    Returns:
        A status message indicating success or failure.
    """
    try:
        ffmpeg.input(input_audio_path).output(output_audio_path, format=target_format).run(capture_stdout=True, capture_stderr=True)
        return f"Audio format converted to {target_format} and saved to {output_audio_path}"
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error converting audio format: {error_message}"
    except FileNotFoundError:
        return f"Error: Input audio file not found at {input_audio_path}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
