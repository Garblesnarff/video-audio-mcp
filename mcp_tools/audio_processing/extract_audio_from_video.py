
import ffmpeg

def extract_audio_from_video(video_path: str, output_audio_path: str, audio_codec: str = 'mp3') -> str:
    """Extracts audio from a video file and saves it.
    
    Args:
        video_path: The path to the input video file.
        output_audio_path: The path to save the extracted audio file.
        audio_codec: The audio codec to use for the output (e.g., 'mp3', 'aac', 'wav'). Defaults to 'mp3'.
    Returns:
        A status message indicating success or failure.
    """
    try:
        input_stream = ffmpeg.input(video_path)
        output_stream = input_stream.output(output_audio_path, acodec=audio_codec)
        output_stream.run(capture_stdout=True, capture_stderr=True)
        return f"Audio extracted successfully to {output_audio_path}"
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error extracting audio: {error_message}"
    except FileNotFoundError:
        return f"Error: Input video file not found at {video_path}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
