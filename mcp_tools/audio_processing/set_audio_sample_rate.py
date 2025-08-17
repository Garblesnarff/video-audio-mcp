
import ffmpeg

def set_audio_sample_rate(input_audio_path: str, output_audio_path: str, sample_rate: int) -> str:
    """Sets the sample rate for an audio file.
    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the audio file with the new sample rate.
        sample_rate: Target audio sample rate in Hz (e.g., 44100, 48000).
    Returns:
        A status message indicating success or failure.
    """
    try:
        ffmpeg.input(input_audio_path).output(output_audio_path, ar=sample_rate).run(capture_stdout=True, capture_stderr=True)
        return f"Audio sample rate set to {sample_rate} Hz and saved to {output_audio_path}"
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error setting audio sample rate: {error_message}"
    except FileNotFoundError:
        return f"Error: Input audio file not found at {input_audio_path}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
