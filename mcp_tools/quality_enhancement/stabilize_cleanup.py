import ffmpeg
import os
from typing import Optional, Dict, List

def stabilize_shaky_video(input_video_path: str, output_video_path: str,
                         stabilization_method: str = "vidstab",
                         smoothing: float = 10.0,
                         crop_black_borders: bool = True,
                         zoom_factor: float = 1.1) -> str:
    """
    Stabilize shaky video footage using advanced algorithms.
    
    Args:
        input_video_path: Path to the input video file
        output_video_path: Path for the output video file
        stabilization_method: Method to use ("vidstab", "deshake", "robust")
        smoothing: Smoothing factor (higher = more stable but may lose detail)
        crop_black_borders: Whether to crop black borders from stabilization
        zoom_factor: Slight zoom to eliminate edge artifacts
    
    Returns:
        Success message with output file path
    """
    
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video file does not exist: {input_video_path}")
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        video_stream = input_stream.video
        
        if stabilization_method == "vidstab":
            # Two-pass vidstab stabilization (most effective)
            # Pass 1: Generate transforms
            transforms_file = output_video_path.replace('.mp4', '_transforms.trf')
            
            # Detection pass
            detect_stream = video_stream.filter('vidstabdetect',
                                              shakiness=8,
                                              accuracy=9,
                                              result=transforms_file)
            
            detect_output = ffmpeg.output(detect_stream, 'null', f='null')
            ffmpeg.run(detect_output, overwrite_output=True, quiet=True)
            
            # Transform pass
            video_stream = video_stream.filter('vidstabtransform',
                                             input=transforms_file,
                                             smoothing=int(smoothing),
                                             crop='black' if crop_black_borders else 'keep',
                                             zoom=zoom_factor,
                                             interpol='bilinear')
            
        elif stabilization_method == "deshake":
            # Single-pass deshake
            video_stream = video_stream.filter('deshake',
                                             x=-1, y=-1, w=-1, h=-1,
                                             rx=16, ry=16,
                                             edge='blank')
            
        elif stabilization_method == "robust":
            # Robust stabilization with motion estimation
            video_stream = video_stream.filter('deshake',
                                             x=-1, y=-1, w=-1, h=-1,
                                             rx=32, ry=32,
                                             edge='mirror',
                                             blocksize=8,
                                             contrast=125)
        
        # Apply slight zoom to eliminate edge artifacts
        if zoom_factor > 1.0:
            video_stream = video_stream.filter('scale',
                                             iw=f'iw*{zoom_factor}',
                                             ih=f'ih*{zoom_factor}')
            video_stream = video_stream.filter('crop',
                                             iw='iw/1.1', ih='ih/1.1',
                                             x='(iw-ow)/2', y='(ih-oh)/2')
        
        # Output with good quality
        output = ffmpeg.output(video_stream, input_stream.audio, output_video_path,
                             vcodec='libx264', acodec='aac',
                             preset='medium', crf=18)
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        # Clean up temporary files
        if stabilization_method == "vidstab":
            transforms_file = output_video_path.replace('.mp4', '_transforms.trf')
            if os.path.exists(transforms_file):
                os.remove(transforms_file)
        
        return f"Successfully stabilized video using {stabilization_method}: {output_video_path}"
        
    except Exception as e:
        return f"Error stabilizing video: {str(e)}"


def remove_background(input_video_path: str, output_video_path: str,
                     method: str = "chroma",
                     background_color: str = "green",
                     threshold: float = 0.1,
                     replacement_background: str = None,
                     edge_softening: float = 0.02) -> str:
    """
    Remove background from video using various methods.
    
    Args:
        input_video_path: Path to the input video file
        output_video_path: Path for the output video file
        method: Removal method ("chroma", "color_range", "ai_mask")
        background_color: Color to remove ("green", "blue", "white", "black")
        threshold: Sensitivity threshold for color removal
        replacement_background: Path to replacement background video/image
        edge_softening: Amount of edge softening (0.0-1.0)
    
    Returns:
        Success message with output file path
    """
    
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video file does not exist: {input_video_path}")
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        video_stream = input_stream.video
        
        if method == "chroma":
            # Chroma key removal
            if background_color.lower() == "green":
                color_key = "0x00FF00"
                similarity = threshold
            elif background_color.lower() == "blue":
                color_key = "0x0000FF" 
                similarity = threshold
            elif background_color.lower() == "white":
                color_key = "0xFFFFFF"
                similarity = threshold * 2  # White needs higher threshold
            else:  # black
                color_key = "0x000000"
                similarity = threshold * 1.5
            
            video_stream = video_stream.filter('chromakey',
                                             color=color_key,
                                             similarity=similarity,
                                             blend=edge_softening)
                                             
        elif method == "color_range":
            # Color range removal (more flexible)
            if background_color.lower() == "green":
                video_stream = video_stream.filter('colorkey',
                                                 color='green',
                                                 similarity=threshold,
                                                 blend=edge_softening)
            elif background_color.lower() == "blue":
                video_stream = video_stream.filter('colorkey',
                                                 color='blue',
                                                 similarity=threshold,
                                                 blend=edge_softening)
            else:
                video_stream = video_stream.filter('colorkey',
                                                 color=background_color,
                                                 similarity=threshold,
                                                 blend=edge_softening)
        
        # Add replacement background if provided
        if replacement_background and os.path.exists(replacement_background):
            # Check if it's an image or video
            try:
                probe = ffmpeg.probe(replacement_background)
                video_info = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
                
                if video_info:
                    # It's a video
                    bg_stream = ffmpeg.input(replacement_background)
                    # Scale background to match foreground
                    fg_probe = ffmpeg.probe(input_video_path)
                    fg_info = next(s for s in fg_probe['streams'] if s['codec_type'] == 'video')
                    bg_width = int(fg_info['width'])
                    bg_height = int(fg_info['height'])
                    
                    bg_stream = bg_stream.video.filter('scale', bg_width, bg_height)
                    video_stream = ffmpeg.overlay(bg_stream, video_stream)
                else:
                    # It's an image - loop it
                    bg_stream = ffmpeg.input(replacement_background, loop=1, t=10)
                    # Get duration from original video
                    fg_probe = ffmpeg.probe(input_video_path)
                    duration = float(fg_probe['format']['duration'])
                    
                    bg_stream = ffmpeg.input(replacement_background, loop=1, t=duration)
                    fg_probe = ffmpeg.probe(input_video_path)
                    fg_info = next(s for s in fg_probe['streams'] if s['codec_type'] == 'video')
                    bg_width = int(fg_info['width'])
                    bg_height = int(fg_info['height'])
                    
                    bg_stream = bg_stream.video.filter('scale', bg_width, bg_height)
                    video_stream = ffmpeg.overlay(bg_stream, video_stream)
                    
            except:
                # If probe fails, treat as image
                bg_stream = ffmpeg.input(replacement_background, loop=1, t=10)
                video_stream = ffmpeg.overlay(bg_stream, video_stream)
        
        # Output
        output = ffmpeg.output(video_stream, input_stream.audio, output_video_path,
                             vcodec='libx264', acodec='aac',
                             preset='medium', crf=18,
                             pix_fmt='yuv420p')  # Ensure compatibility
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully removed {background_color} background: {output_video_path}"
        
    except Exception as e:
        return f"Error removing background: {str(e)}"


def batch_enhance_videos(input_directory: str, output_directory: str,
                        enhancement_settings: Dict = None,
                        file_pattern: str = "*.mp4",
                        preserve_structure: bool = True) -> str:
    """
    Batch enhance multiple videos in a directory.
    
    Args:
        input_directory: Directory containing input videos
        output_directory: Directory for output videos
        enhancement_settings: Dictionary of enhancement parameters
        file_pattern: Pattern to match files ("*.mp4", "*.mov", etc.)
        preserve_structure: Whether to preserve subdirectory structure
    
    Returns:
        Summary of batch processing results
    """
    
    if not os.path.exists(input_directory):
        raise FileNotFoundError(f"Input directory does not exist: {input_directory}")
    
    # Default enhancement settings
    if not enhancement_settings:
        enhancement_settings = {
            'enhancement_level': 'medium',
            'denoise': True,
            'color_correction': 'auto',
            'stabilize': False
        }
    
    try:
        import glob
        
        # Create output directory
        os.makedirs(output_directory, exist_ok=True)
        
        # Find all matching video files
        search_pattern = os.path.join(input_directory, "**", file_pattern)
        video_files = glob.glob(search_pattern, recursive=True)
        
        if not video_files:
            return f"No video files found matching pattern: {file_pattern}"
        
        processed_count = 0
        failed_count = 0
        error_messages = []
        
        for video_file in video_files:
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
                    output_path = f"{base}_enhanced{ext}"
                
                # Apply enhancements based on settings
                input_stream = ffmpeg.input(video_file)
                video_stream = input_stream.video
                audio_stream = input_stream.audio
                
                # Noise reduction
                if enhancement_settings.get('denoise', True):
                    video_stream = video_stream.filter('hqdn3d', 2, 1, 2, 1)
                
                # Color correction
                color_type = enhancement_settings.get('color_correction', 'auto')
                if color_type == 'auto':
                    video_stream = video_stream.filter('eq', 
                                                     contrast=1.1, brightness=0.02, 
                                                     saturation=1.05, gamma=0.95)
                
                # Enhancement level
                level = enhancement_settings.get('enhancement_level', 'medium')
                if level == 'light':
                    video_stream = video_stream.filter('unsharp', 
                                                     luma_msize_x=3, luma_msize_y=3,
                                                     luma_amount=0.5)
                elif level == 'medium':
                    video_stream = video_stream.filter('unsharp',
                                                     luma_msize_x=5, luma_msize_y=5,
                                                     luma_amount=1.0)
                elif level == 'aggressive':
                    video_stream = video_stream.filter('unsharp',
                                                     luma_msize_x=5, luma_msize_y=5,
                                                     luma_amount=1.5)
                
                # Stabilization (optional, can be slow)
                if enhancement_settings.get('stabilize', False):
                    video_stream = video_stream.filter('deshake')
                
                # Audio enhancement
                if enhancement_settings.get('enhance_audio', True):
                    audio_stream = audio_stream.filter('loudnorm')
                
                # Output
                output = ffmpeg.output(video_stream, audio_stream, output_path,
                                     vcodec='libx264', acodec='aac',
                                     preset='medium', crf=18)
                
                ffmpeg.run(output, overwrite_output=True, quiet=True)
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                error_messages.append(f"{os.path.basename(video_file)}: {str(e)}")
        
        result = f"Batch processing complete: {processed_count} videos enhanced"
        if failed_count > 0:
            result += f", {failed_count} failed"
            result += f"\nErrors: {'; '.join(error_messages[:5])}"  # Show first 5 errors
        
        return result
        
    except Exception as e:
        return f"Error in batch enhancement: {str(e)}"