
import ffmpeg
import os

def change_video_speed(video_path: str, output_video_path: str, speed_factor: float) -> str:
    """Changes the playback speed of a video (and its audio).

    Args:
        video_path: Path to the input video file.
        output_video_path: Path to save the speed-adjusted video file.
        speed_factor: The factor by which to change the speed (e.g., 2.0 for 2x speed, 0.5 for half speed).
                      Must be positive.
    
    Returns:
        A status message indicating success or failure.
    """
    if speed_factor <= 0:
        return "Error: Speed factor must be positive."
    if not os.path.exists(video_path):
        return f"Error: Input video file not found at {video_path}"

    try:
        # Process atempo values (audio speed) - requires special handling for values outside 0.5-2.0 range
        atempo_value = speed_factor
        atempo_filters = []
        
        # Handle audio speed outside atempo's range (0.5-2.0)
        if speed_factor < 0.5:
            # For speed < 0.5, use multiple atempo=0.5 filters
            while atempo_value < 0.5:
                atempo_filters.append("atempo=0.5")
                atempo_value *= 2  # After applying atempo=0.5, the remaining factor doubles
            # Add the remaining factor if needed
            if atempo_value < 0.99:  # A bit of buffer for floating point comparison
                atempo_filters.append(f"atempo={atempo_value}")
        elif speed_factor > 2.0:
            # For speed > 2.0, use multiple atempo=2.0 filters
            while atempo_value > 2.0:
                atempo_filters.append("atempo=2.0")
                atempo_value /= 2  # After applying atempo=2.0, the remaining factor halves
            # Add the remaining factor if needed
            if atempo_value > 1.01:  # A bit of buffer for floating point comparison
                atempo_filters.append(f"atempo={atempo_value}")
        else:
            # For speed factors within range, just use one atempo filter
            atempo_filters.append(f"atempo={speed_factor}")
        
        # Apply separate filters to video and audio streams
        input_stream = ffmpeg.input(video_path)
        video = input_stream.video.setpts(f"{1.0/speed_factor}*PTS")
        
        # Chain multiple audio filters if needed
        audio = input_stream.audio
        for filter_str in atempo_filters:
            audio = audio.filter("atempo", speed_factor if filter_str == f"atempo={speed_factor}" else 
                               0.5 if filter_str == "atempo=0.5" else 
                               2.0 if filter_str == "atempo=2.0" else 
                               float(filter_str.replace("atempo=", "")))
        
        # Combine processed streams and output
        output = ffmpeg.output(video, audio, output_video_path)
        output.run(capture_stdout=True, capture_stderr=True)
        
        return f"Video speed changed by factor {speed_factor} and saved to {output_video_path}"
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error changing video speed: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred while changing video speed: {str(e)}"
