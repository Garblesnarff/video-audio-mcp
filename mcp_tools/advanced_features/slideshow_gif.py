import ffmpeg
import os
from typing import List, Dict, Optional

def create_slideshow(image_paths: List[str], output_video_path: str,
                    duration_per_image: float = 3.0,
                    transition_type: str = "fade",
                    transition_duration: float = 0.5,
                    background_music: str = None,
                    output_resolution: str = "1920x1080",
                    fps: int = 30) -> str:
    """
    Create a slideshow video from a series of images.
    
    Args:
        image_paths: List of paths to image files
        output_video_path: Path for the output video file
        duration_per_image: How long each image is displayed (seconds)
        transition_type: Type of transition ("fade", "slide", "zoom", "none")
        transition_duration: Duration of transition effect (seconds)
        background_music: Path to background music file
        output_resolution: Output video resolution
        fps: Output frame rate
    
    Returns:
        Success message with output file path
    """
    
    if not all(os.path.exists(path) for path in image_paths):
        raise FileNotFoundError("One or more image files do not exist")
    
    if len(image_paths) < 2:
        raise ValueError("Slideshow requires at least 2 images")
    
    try:
        width, height = map(int, output_resolution.split('x'))
        
        # Create video from images
        if transition_type == "none":
            # Simple concatenation without transitions
            image_streams = []
            for img_path in image_paths:
                # Create video segment from image
                img_stream = ffmpeg.input(img_path, loop=1, t=duration_per_image, framerate=fps)
                img_stream = img_stream.filter('scale', width, height, force_original_aspect_ratio='decrease')
                img_stream = img_stream.filter('pad', width, height, '(ow-iw)/2', '(oh-ih)/2', 'black')
                image_streams.append(img_stream)
            
            # Concatenate all image streams
            video_stream = ffmpeg.concat(*image_streams, v=1, a=0)
            
        else:
            # Create transitions between images
            effective_duration = duration_per_image - (transition_duration / 2)
            image_streams = []
            
            for i, img_path in enumerate(image_paths):
                # Base duration (longer for first and last image)
                if i == 0 or i == len(image_paths) - 1:
                    img_duration = duration_per_image
                else:
                    img_duration = duration_per_image + transition_duration
                
                img_stream = ffmpeg.input(img_path, loop=1, t=img_duration, framerate=fps)
                img_stream = img_stream.filter('scale', width, height, force_original_aspect_ratio='decrease')
                img_stream = img_stream.filter('pad', width, height, '(ow-iw)/2', '(oh-ih)/2', 'black')
                
                # Add transitions
                if transition_type == "fade" and i > 0:
                    # Fade in
                    img_stream = img_stream.filter('fade', type='in', start_time=0, duration=transition_duration)
                elif transition_type == "zoom":
                    # Zoom effect
                    zoom_filter = f"scale=iw*1.2:ih*1.2,crop=iw:ih"
                    img_stream = img_stream.filter('zoompan', 
                                                 z='min(zoom+0.0015,1.5)',
                                                 d=int(fps * img_duration),
                                                 x='iw/2-(iw/zoom/2)',
                                                 y='ih/2-(ih/zoom/2)')
                
                image_streams.append(img_stream)
            
            # Handle slide transitions differently
            if transition_type == "slide":
                # Create sliding effect between images
                filter_complex = []
                inputs = []
                
                for i, img_path in enumerate(image_paths):
                    img_input = ffmpeg.input(img_path, loop=1, t=duration_per_image, framerate=fps)
                    img_input = img_input.filter('scale', width, height, force_original_aspect_ratio='decrease')
                    img_input = img_input.filter('pad', width, height, '(ow-iw)/2', '(oh-ih)/2', 'black')
                    inputs.append(img_input)
                
                # Build slide transition chain
                current = inputs[0]
                for i in range(1, len(inputs)):
                    # Create slide transition
                    transition_frames = int(fps * transition_duration)
                    current = ffmpeg.filter([current, inputs[i]], 'xfade',
                                          transition='slide',
                                          duration=transition_duration,
                                          offset=effective_duration)
                
                video_stream = current
            else:
                # For fade transitions, use xfade filter
                if transition_type == "fade" and len(image_streams) > 1:
                    current = image_streams[0]
                    for i in range(1, len(image_streams)):
                        current = ffmpeg.filter([current, image_streams[i]], 'xfade',
                                              transition='fade',
                                              duration=transition_duration,
                                              offset=effective_duration)
                    video_stream = current
                else:
                    video_stream = ffmpeg.concat(*image_streams, v=1, a=0)
        
        # Add background music if provided
        if background_music and os.path.exists(background_music):
            audio_input = ffmpeg.input(background_music)
            
            # Get video duration to loop audio if needed
            total_duration = len(image_paths) * duration_per_image
            
            # Loop audio to match video duration
            audio_stream = audio_input.filter('aloop', loop=-1, size=int(48000 * total_duration))
            audio_stream = audio_stream.filter('atrim', duration=total_duration)
            
            # Fade in/out audio
            audio_stream = audio_stream.filter('afade', type='in', duration=1.0)
            audio_stream = audio_stream.filter('afade', type='out', start_time=total_duration-1.0, duration=1.0)
            
            output = ffmpeg.output(video_stream, audio_stream, output_video_path,
                                 vcodec='libx264', acodec='aac',
                                 preset='medium', crf=18,
                                 pix_fmt='yuv420p')
        else:
            output = ffmpeg.output(video_stream, output_video_path,
                                 vcodec='libx264',
                                 preset='medium', crf=18,
                                 pix_fmt='yuv420p')
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully created slideshow with {len(image_paths)} images: {output_video_path}"
        
    except Exception as e:
        return f"Error creating slideshow: {str(e)}"


def create_gif_from_video(input_video_path: str, output_gif_path: str,
                         start_time: float = 0.0,
                         duration: float = 5.0,
                         fps: int = 15,
                         width: int = 480,
                         optimize_colors: bool = True,
                         loop_count: int = 0) -> str:
    """
    Convert video segment to optimized GIF.
    
    Args:
        input_video_path: Path to the input video file
        output_gif_path: Path for the output GIF file
        start_time: Start time in seconds
        duration: Duration of GIF in seconds
        fps: Frame rate for GIF
        width: Width of GIF (height will be calculated)
        optimize_colors: Whether to optimize color palette
        loop_count: Number of loops (0 = infinite)
    
    Returns:
        Success message with output file path
    """
    
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video file does not exist: {input_video_path}")
    
    try:
        # Load video segment
        input_stream = ffmpeg.input(input_video_path, ss=start_time, t=duration)
        
        # Scale video
        video_stream = input_stream.filter('scale', width, -1)  # Keep aspect ratio
        
        # Set frame rate
        video_stream = video_stream.filter('fps', fps)
        
        if optimize_colors:
            # Generate optimized palette
            palette_path = output_gif_path.replace('.gif', '_palette.png')
            
            # Generate palette
            palette_stream = video_stream.filter('palettegen', 
                                                max_colors=256,
                                                stats_mode='diff')
            palette_output = ffmpeg.output(palette_stream, palette_path)
            ffmpeg.run(palette_output, overwrite_output=True, quiet=True)
            
            # Apply palette to create optimized GIF
            palette_input = ffmpeg.input(palette_path)
            gif_stream = ffmpeg.filter([video_stream, palette_input], 'paletteuse',
                                     dither='bayer:bayer_scale=5:diff_mode=rectangle')
            
            # Set loop count
            if loop_count > 0:
                gif_output = ffmpeg.output(gif_stream, output_gif_path, loop=loop_count)
            else:
                gif_output = ffmpeg.output(gif_stream, output_gif_path)
            
            ffmpeg.run(gif_output, overwrite_output=True, quiet=True)
            
            # Clean up palette file
            if os.path.exists(palette_path):
                os.remove(palette_path)
                
        else:
            # Direct conversion without palette optimization
            if loop_count > 0:
                gif_output = ffmpeg.output(video_stream, output_gif_path, loop=loop_count)
            else:
                gif_output = ffmpeg.output(video_stream, output_gif_path)
            
            ffmpeg.run(gif_output, overwrite_output=True, quiet=True)
        
        return f"Successfully created GIF ({fps}fps, {width}px wide): {output_gif_path}"
        
    except Exception as e:
        return f"Error creating GIF: {str(e)}"


def batch_process_videos(input_directory: str, output_directory: str,
                        operation: str,
                        operation_params: Dict = None,
                        file_pattern: str = "*.mp4",
                        preserve_structure: bool = True,
                        max_concurrent: int = 3) -> str:
    """
    Batch process multiple videos with specified operation.
    
    Args:
        input_directory: Directory containing input videos
        output_directory: Directory for output videos
        operation: Operation to perform ("convert", "resize", "enhance", "extract_audio")
        operation_params: Parameters for the operation
        file_pattern: Pattern to match files
        preserve_structure: Whether to preserve subdirectory structure
        max_concurrent: Maximum number of concurrent processes
    
    Returns:
        Summary of batch processing results
    """
    
    if not os.path.exists(input_directory):
        raise FileNotFoundError(f"Input directory does not exist: {input_directory}")
    
    try:
        import glob
        import concurrent.futures
        import threading
        
        # Create output directory
        os.makedirs(output_directory, exist_ok=True)
        
        # Find all matching video files
        search_pattern = os.path.join(input_directory, "**", file_pattern)
        video_files = glob.glob(search_pattern, recursive=True)
        
        if not video_files:
            return f"No video files found matching pattern: {file_pattern}"
        
        # Default operation parameters
        if not operation_params:
            operation_params = {}
        
        def process_single_video(video_file):
            try:
                # Calculate output path
                rel_path = os.path.relpath(video_file, input_directory)
                if preserve_structure:
                    output_path = os.path.join(output_directory, rel_path)
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                else:
                    filename = os.path.basename(video_file)
                    output_path = os.path.join(output_directory, filename)
                
                # Ensure different name if same directory
                if output_path == video_file:
                    base, ext = os.path.splitext(output_path)
                    output_path = f"{base}_processed{ext}"
                
                # Perform operation
                input_stream = ffmpeg.input(video_file)
                
                if operation == "convert":
                    format_type = operation_params.get('format', 'mp4')
                    if format_type == 'webm':
                        output = ffmpeg.output(input_stream, output_path,
                                             vcodec='libvpx-vp9', acodec='libopus')
                    else:
                        output = ffmpeg.output(input_stream, output_path,
                                             vcodec='libx264', acodec='aac')
                
                elif operation == "resize":
                    width = operation_params.get('width', 1280)
                    height = operation_params.get('height', 720)
                    video_stream = input_stream.filter('scale', width, height)
                    output = ffmpeg.output(video_stream, input_stream.audio, output_path,
                                         vcodec='libx264', acodec='aac')
                
                elif operation == "enhance":
                    video_stream = input_stream.video
                    # Basic enhancement
                    video_stream = video_stream.filter('eq', contrast=1.1, saturation=1.05)
                    video_stream = video_stream.filter('unsharp', luma_msize_x=5, luma_msize_y=5, luma_amount=1.0)
                    output = ffmpeg.output(video_stream, input_stream.audio, output_path,
                                         vcodec='libx264', acodec='aac')
                
                elif operation == "extract_audio":
                    audio_format = operation_params.get('format', 'mp3')
                    audio_path = output_path.replace('.mp4', f'.{audio_format}')
                    output = ffmpeg.output(input_stream.audio, audio_path)
                    output_path = audio_path
                
                else:
                    return f"Unknown operation: {operation}"
                
                ffmpeg.run(output, overwrite_output=True, quiet=True)
                return f"Success: {os.path.basename(video_file)}"
                
            except Exception as e:
                return f"Error processing {os.path.basename(video_file)}: {str(e)}"
        
        # Process files concurrently
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_file = {executor.submit(process_single_video, vf): vf for vf in video_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                result = future.result()
                results.append(result)
        
        # Count successes and failures
        successes = [r for r in results if r.startswith("Success")]
        failures = [r for r in results if r.startswith("Error")]
        
        summary = f"Batch {operation} complete: {len(successes)} succeeded, {len(failures)} failed"
        if failures:
            summary += f"\nFirst few errors: {'; '.join(failures[:3])}"
        
        return summary
        
    except Exception as e:
        return f"Error in batch processing: {str(e)}"