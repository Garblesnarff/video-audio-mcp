
import ffmpeg

def convert_audio_properties(input_audio_path: str, output_audio_path: str, target_format: str, 
                               bitrate: str = None, sample_rate: int = None, channels: int = None) -> str:
    """Converts audio file format and ALL specified properties like bitrate, sample rate, and channels.

    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the converted audio file.
        target_format: Desired output audio format (e.g., 'mp3', 'wav', 'aac').
        bitrate: Target audio bitrate (e.g., '128k', '192k'). Optional.
        sample_rate: Target audio sample rate in Hz (e.g., 44100, 48000). Optional.
        channels: Number of audio channels (1 for mono, 2 for stereo). Optional.
    Returns:
        A status message indicating success or failure.
    """
    try:
        stream = ffmpeg.input(input_audio_path)
        kwargs = {}
        if bitrate: 
            kwargs['audio_bitrate'] = bitrate
        if sample_rate: 
            kwargs['ar'] = sample_rate
        if channels: 
            kwargs['ac'] = channels
        kwargs['format'] = target_format

        output_stream = stream.output(output_audio_path, **kwargs)
        output_stream.run(capture_stdout=True, capture_stderr=True)
        return f"Audio converted successfully to {output_audio_path} with format {target_format} and specified properties."
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error converting audio properties: {error_message}"
    except FileNotFoundError:
        return f"Error: Input audio file not found at {input_audio_path}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
