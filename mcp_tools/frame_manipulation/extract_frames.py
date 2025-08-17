import ffmpeg
import os
import math

def extract_frames(input_video_path: str, output_directory: str,
                  extraction_mode: str = "interval", interval: float = 1.0,
                  start_time: float = 0.0, end_time: float = None,
                  frame_format: str = "png", quality: int = 95,
                  resolution: str = None, frame_count: int = None) -> str:
    """Extracts frames from video with various options for timing and quality.
    
    Args:
        input_video_path: Path to the source video file
        output_directory: Directory to save extracted frames
        extraction_mode: How to extract frames:
            - 'interval': Extract at regular time intervals
            - 'count': Extract specific number of frames evenly distributed
            - 'fps': Extract at specific frame rate
            - 'keyframes': Extract only keyframes/I-frames
            - 'scene_changes': Extract at scene change points
        interval: Time interval in seconds between frames (for 'interval' mode)
        start_time: Start time in seconds for extraction
        end_time: End time in seconds for extraction (None for full duration)
        frame_format: Output format ('png', 'jpg', 'bmp', 'tiff')
        quality: Output quality for JPEG (1-100, higher is better)
        resolution: Output resolution (e.g., '1920x1080', '640x360', None for original)
        frame_count: Number of frames to extract (for 'count' mode)
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    # Create output directory
    os.makedirs(output_directory, exist_ok=True)
    
    try:
        # Get video duration if end_time not specified
        if end_time is None:
            probe = ffmpeg.probe(input_video_path)
            end_time = float(probe['format']['duration'])
        
        duration = end_time - start_time
        
        # Setup input with time range
        input_stream = ffmpeg.input(input_video_path, ss=start_time, t=duration)
        
        # Build filter chain
        filters = []
        
        # Resolution scaling
        if resolution:
            width, height = resolution.split('x')
            filters.append(f'scale={width}:{height}')
        
        # Frame extraction based on mode
        if extraction_mode == 'interval':
            # Extract every N seconds
            fps_filter = f'fps=1/{interval}'
            filters.append(fps_filter)
            
        elif extraction_mode == 'count':
            if frame_count is None:
                return "Error: frame_count must be specified for 'count' mode"
            # Calculate fps to get desired number of frames
            fps_for_count = frame_count / duration
            filters.append(f'fps={fps_for_count}')
            
        elif extraction_mode == 'fps':
            # Extract at specific frame rate
            target_fps = 1.0 / interval if interval > 0 else 1.0
            filters.append(f'fps={target_fps}')
            
        elif extraction_mode == 'keyframes':
            # Extract only keyframes
            filters.append("select='eq(pict_type,I)'")
            
        elif extraction_mode == 'scene_changes':
            # Extract frames at scene changes
            scene_threshold = 0.4  # Can be made configurable
            filters.append(f"select='gt(scene\\,{scene_threshold})'")
        
        # Apply filters if any
        video_stream = input_stream.video
        if filters:
            filter_string = ','.join(filters)
            video_stream = video_stream.filter('fps', 1/interval if extraction_mode == 'interval' else '1')
            if resolution:
                video_stream = video_stream.filter('scale', width, height)
        
        # Set output filename pattern
        frame_extension = frame_format.lower()
        output_pattern = os.path.join(output_directory, f'frame_%04d.{frame_extension}')
        
        # Configure output parameters
        output_params = {}
        
        if frame_format.lower() == 'jpg' or frame_format.lower() == 'jpeg':
            output_params['q:v'] = quality
        elif frame_format.lower() == 'png':
            output_params['compression_level'] = 6  # PNG compression
        
        # Create output
        output = ffmpeg.output(video_stream, output_pattern, **output_params)
        
        # Handle special cases for select filters
        if extraction_mode in ['keyframes', 'scene_changes']:
            output = output.global_args('-vsync', 'vfr')
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        # Count extracted frames
        extracted_count = len([f for f in os.listdir(output_directory) if f.endswith(frame_extension)])
        
        return f"Extracted {extracted_count} frames using '{extraction_mode}' mode. Frames saved to {output_directory}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error extracting frames: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def extract_frame_at_time(input_video_path: str, output_image_path: str,
                         timestamp: float, resolution: str = None,
                         frame_format: str = "png", quality: int = 95) -> str:
    """Extracts a single frame at a specific timestamp.
    
    Args:
        input_video_path: Path to the source video file
        output_image_path: Path to save the extracted frame
        timestamp: Time in seconds to extract frame from
        resolution: Output resolution (e.g., '1920x1080', None for original)
        frame_format: Output format ('png', 'jpg', 'bmp', 'tiff')
        quality: Output quality for JPEG (1-100)
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_image_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Setup input at specific timestamp
        input_stream = ffmpeg.input(input_video_path, ss=timestamp)
        video_stream = input_stream.video
        
        # Apply resolution scaling if specified
        if resolution:
            width, height = resolution.split('x')
            video_stream = video_stream.filter('scale', width, height)
        
        # Configure output parameters
        output_params = {'frames:v': 1}  # Extract only one frame
        
        if frame_format.lower() in ['jpg', 'jpeg']:
            output_params['q:v'] = quality
        elif frame_format.lower() == 'png':
            output_params['compression_level'] = 6
        
        # Create output
        output = ffmpeg.output(video_stream, output_image_path, **output_params)
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Frame extracted successfully at {timestamp}s. Saved to {output_image_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error extracting frame: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def extract_frames_batch(video_list: list[str], output_base_directory: str,
                        extraction_settings: dict) -> str:
    """Batch extract frames from multiple videos with same settings.
    
    Args:
        video_list: List of paths to video files
        output_base_directory: Base directory for all outputs
        extraction_settings: Dictionary with extraction parameters:
            - extraction_mode, interval, frame_format, quality, etc.
    
    Returns:
        A status message indicating success or failure.
    """
    if not video_list:
        return "Error: No video files provided"
    
    results = []
    successful = 0
    failed = 0
    
    for video_path in video_list:
        if not os.path.exists(video_path):
            results.append(f"FAILED: {video_path} - file not found")
            failed += 1
            continue
        
        try:
            # Create subdirectory for each video
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            video_output_dir = os.path.join(output_base_directory, video_name)
            
            # Extract frames using provided settings
            result = extract_frames(
                input_video_path=video_path,
                output_directory=video_output_dir,
                **extraction_settings
            )
            
            if "Error" not in result:
                results.append(f"SUCCESS: {video_name}")
                successful += 1
            else:
                results.append(f"FAILED: {video_name} - {result}")
                failed += 1
                
        except Exception as e:
            results.append(f"FAILED: {video_name} - {str(e)}")
            failed += 1
    
    summary = f"Batch frame extraction completed. Successful: {successful}, Failed: {failed}"
    if failed > 0:
        summary += f"\n\nDetails:\n" + "\n".join(results)
    
    return summary


def extract_frame_sequence(input_video_path: str, output_directory: str,
                          start_frame: int, end_frame: int,
                          frame_format: str = "png", resolution: str = None) -> str:
    """Extracts a specific sequence of frames by frame number.
    
    Args:
        input_video_path: Path to the source video file
        output_directory: Directory to save extracted frames
        start_frame: Starting frame number (0-based)
        end_frame: Ending frame number (inclusive)
        frame_format: Output format ('png', 'jpg', 'bmp', 'tiff')
        resolution: Output resolution (e.g., '1920x1080', None for original)
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    if start_frame >= end_frame:
        return "Error: start_frame must be less than end_frame"
    
    try:
        # Get video properties
        probe = ffmpeg.probe(input_video_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        
        if not video_stream:
            return "Error: No video stream found in input file"
        
        # Calculate frame rate
        frame_rate_str = video_stream.get('avg_frame_rate', '30/1')
        num, den = map(float, frame_rate_str.split('/'))
        fps = num / den if den != 0 else 30
        
        # Convert frame numbers to timestamps
        start_time = start_frame / fps
        end_time = end_frame / fps
        duration = end_time - start_time
        
        # Create output directory
        os.makedirs(output_directory, exist_ok=True)
        
        # Setup input with time range
        input_stream = ffmpeg.input(input_video_path, ss=start_time, t=duration)
        video_stream = input_stream.video
        
        # Apply resolution scaling if specified
        if resolution:
            width, height = resolution.split('x')
            video_stream = video_stream.filter('scale', width, height)
        
        # Extract all frames in the range
        frame_extension = frame_format.lower()
        output_pattern = os.path.join(output_directory, f'frame_%04d.{frame_extension}')
        
        output_params = {}
        if frame_format.lower() in ['jpg', 'jpeg']:
            output_params['q:v'] = 95
        
        output = ffmpeg.output(video_stream, output_pattern, **output_params)
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        # Count extracted frames
        frame_count = end_frame - start_frame + 1
        extracted_count = len([f for f in os.listdir(output_directory) if f.endswith(frame_extension)])
        
        return f"Extracted {extracted_count} frames (frames {start_frame}-{end_frame}). Saved to {output_directory}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error extracting frame sequence: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"