
import ffmpeg

def set_audio_channels(input_audio_path: str, output_audio_path: str, channels: int) -> str:
    """Sets the number of channels for an audio file (1 for mono, 2 for stereo).
    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the audio file with the new channel layout.
        channels: Number of audio channels (1 for mono, 2 for stereo).
    Returns:
        A status message indicating success or failure.
    """
    try:
        ffmpeg.input(input_audio_path).output(output_audio_path, ac=channels).run(capture_stdout=True, capture_stderr=True)
        return f"Audio channels set to {channels} and saved to {output_audio_path}"
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error setting audio channels: {error_message}"
    except FileNotFoundError:
        return f"Error: Input audio file not found at {input_audio_path}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
