
import ffmpeg

def convert_video_properties(input_video_path: str, output_video_path: str, target_format: str,
                               resolution: str = None, video_codec: str = None, video_bitrate: str = None,
                               frame_rate: int = None, audio_codec: str = None, audio_bitrate: str = None,
                               audio_sample_rate: int = None, audio_channels: int = None) -> str:
    """Converts video file format and ALL specified properties like resolution, codecs, bitrates, and frame rate.
    Args listed in PRD.
    Returns:
        A status message indicating success or failure.
    """
    try:
        stream = ffmpeg.input(input_video_path)
        kwargs = {}
        vf_filters = []

        if resolution and resolution.lower() != 'preserve':
            if 'x' in resolution: 
                vf_filters.append(f"scale={resolution}")
            else: 
                vf_filters.append(f"scale=-2:{resolution}")
        
        if vf_filters:
            kwargs['vf'] = ",".join(vf_filters)

        if video_codec: kwargs['vcodec'] = video_codec
        if video_bitrate: kwargs['video_bitrate'] = video_bitrate
        if frame_rate: kwargs['r'] = frame_rate
        if audio_codec: kwargs['acodec'] = audio_codec
        if audio_bitrate: kwargs['audio_bitrate'] = audio_bitrate
        if audio_sample_rate: kwargs['ar'] = audio_sample_rate
        if audio_channels: kwargs['ac'] = audio_channels
        kwargs['format'] = target_format

        output_stream = stream.output(output_video_path, **kwargs)
        output_stream.run(capture_stdout=True, capture_stderr=True)
        return f"Video converted successfully to {output_video_path} with format {target_format} and specified properties."
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error converting video properties: {error_message}"
    except FileNotFoundError:
        return f"Error: Input video file not found at {input_video_path}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
