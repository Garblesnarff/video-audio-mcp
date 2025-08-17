
import ffmpeg

def set_audio_bitrate(input_audio_path: str, output_audio_path: str, bitrate: str) -> str:
    """Sets the bitrate for an audio file.
    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the audio file with the new bitrate.
        bitrate: Target audio bitrate (e.g., '128k', '192k', '320k').
    Returns:
        A status message indicating success or failure.
    """
    try:
        ffmpeg.input(input_audio_path).output(output_audio_path, audio_bitrate=bitrate).run(capture_stdout=True, capture_stderr=True)
        return f"Audio bitrate set to {bitrate} and saved to {output_audio_path}"
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error setting audio bitrate: {error_message}"
    except FileNotFoundError:
        return f"Error: Input audio file not found at {input_audio_path}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
