import ffmpeg
import os
from typing import List, Dict, Optional

def create_split_screen(video_paths: List[str], output_video_path: str, 
                       layout: str = "horizontal", transition_duration: float = 0.5,
                       border_width: int = 2, border_color: str = "black",
                       audio_mix: str = "blend") -> str:
    """
    Create split-screen video with multiple input videos.
    
    Args:
        video_paths: List of input video file paths (2-4 videos)
        output_video_path: Path for the output video file
        layout: Layout type ("horizontal", "vertical", "quad", "triple_h", "triple_v")
        transition_duration: Duration of transition between splits (seconds)
        border_width: Width of borders between videos (pixels)
        border_color: Color of borders ("black", "white", "gray")
        audio_mix: How to handle audio ("first", "blend", "separate")
    
    Returns:
        Success message with output file path
    """
    
    if not all(os.path.exists(path) for path in video_paths):
        raise FileNotFoundError("One or more input video files do not exist")
    
    if len(video_paths) < 2 or len(video_paths) > 4:
        raise ValueError("Split screen requires 2-4 input videos")
    
    try:
        # Load input videos
        inputs = [ffmpeg.input(path) for path in video_paths]
        
        # Get dimensions of first video for reference
        probe = ffmpeg.probe(video_paths[0])
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        
        # Calculate split dimensions based on layout
        if layout == "horizontal":
            split_width = (width - border_width * (len(video_paths) - 1)) // len(video_paths)
            split_height = height
            
            # Scale and position videos
            scaled_videos = []
            for i, inp in enumerate(inputs):
                scaled = inp.video.filter('scale', split_width, split_height)
                scaled_videos.append(scaled)
            
            # Create horizontal layout with borders
            if len(video_paths) == 2:
                layout_filter = f"[0:v]pad={width}:{height}:0:0:{border_color}[bg];[bg][1:v]overlay={split_width + border_width}:0"
            elif len(video_paths) == 3:
                x2 = split_width + border_width
                x3 = split_width * 2 + border_width * 2
                layout_filter = f"[0:v]pad={width}:{height}:0:0:{border_color}[bg];[bg][1:v]overlay={x2}:0[bg2];[bg2][2:v]overlay={x3}:0"
            else:  # 4 videos
                x2 = split_width + border_width
                x3 = split_width * 2 + border_width * 2
                x4 = split_width * 3 + border_width * 3
                layout_filter = f"[0:v]pad={width}:{height}:0:0:{border_color}[bg];[bg][1:v]overlay={x2}:0[bg2];[bg2][2:v]overlay={x3}:0[bg3];[bg3][3:v]overlay={x4}:0"
                
        elif layout == "vertical":
            split_width = width
            split_height = (height - border_width * (len(video_paths) - 1)) // len(video_paths)
            
            # Scale videos
            scaled_videos = []
            for i, inp in enumerate(inputs):
                scaled = inp.video.filter('scale', split_width, split_height)
                scaled_videos.append(scaled)
            
            # Create vertical layout
            if len(video_paths) == 2:
                layout_filter = f"[0:v]pad={width}:{height}:0:0:{border_color}[bg];[bg][1:v]overlay=0:{split_height + border_width}"
            elif len(video_paths) == 3:
                y2 = split_height + border_width
                y3 = split_height * 2 + border_width * 2
                layout_filter = f"[0:v]pad={width}:{height}:0:0:{border_color}[bg];[bg][1:v]overlay=0:{y2}[bg2];[bg2][2:v]overlay=0:{y3}"
            else:  # 4 videos
                y2 = split_height + border_width
                y3 = split_height * 2 + border_width * 2
                y4 = split_height * 3 + border_width * 3
                layout_filter = f"[0:v]pad={width}:{height}:0:0:{border_color}[bg];[bg][1:v]overlay=0:{y2}[bg2];[bg2][2:v]overlay=0:{y3}[bg3];[bg3][3:v]overlay=0:{y4}"
                
        elif layout == "quad" and len(video_paths) == 4:
            split_width = (width - border_width) // 2
            split_height = (height - border_width) // 2
            
            # Scale videos
            scaled_videos = []
            for i, inp in enumerate(inputs):
                scaled = inp.video.filter('scale', split_width, split_height)
                scaled_videos.append(scaled)
            
            # Create 2x2 grid
            x2 = split_width + border_width
            y2 = split_height + border_width
            layout_filter = f"[0:v]pad={width}:{height}:0:0:{border_color}[bg];[bg][1:v]overlay={x2}:0[bg2];[bg2][2:v]overlay=0:{y2}[bg3];[bg3][3:v]overlay={x2}:{y2}"
            
        else:
            raise ValueError(f"Unsupported layout '{layout}' for {len(video_paths)} videos")
        
        # Scale input videos
        for i, inp in enumerate(inputs):
            if layout in ["horizontal"]:
                inputs[i] = inp.video.filter('scale', split_width, split_height)
            elif layout in ["vertical"]:
                inputs[i] = inp.video.filter('scale', split_width, split_height)
            elif layout == "quad":
                inputs[i] = inp.video.filter('scale', split_width, split_height)
        
        # Apply layout filter
        if len(video_paths) == 2:
            video_out = ffmpeg.filter([inputs[0], inputs[1]], 'hstack' if layout == "horizontal" else 'vstack', inputs=2)
            if border_width > 0:
                video_out = video_out.filter('pad', width + border_width, height + border_width, border_width//2, border_width//2, border_color)
        else:
            # Use complex filter for 3+ videos
            video_stream = ffmpeg.filter_complex([inp for inp in inputs], layout_filter)
            video_out = video_stream
        
        # Handle audio mixing
        audio_inputs = [ffmpeg.input(path).audio for path in video_paths]
        
        if audio_mix == "first":
            audio_out = audio_inputs[0]
        elif audio_mix == "blend":
            if len(audio_inputs) == 2:
                audio_out = ffmpeg.filter([audio_inputs[0], audio_inputs[1]], 'amix', inputs=2, weights="1 1")
            else:
                audio_out = ffmpeg.filter(audio_inputs, 'amix', inputs=len(audio_inputs))
        else:  # separate
            audio_out = audio_inputs[0]  # Default to first
        
        # Create output
        output = ffmpeg.output(video_out, audio_out, output_video_path, 
                             vcodec='libx264', acodec='aac', 
                             preset='medium', crf=18)
        
        # Run the process
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully created split screen video: {output_video_path}"
        
    except Exception as e:
        return f"Error creating split screen video: {str(e)}"


def create_video_grid(video_paths: List[str], output_video_path: str,
                     grid_size: str = "auto", cell_padding: int = 5,
                     background_color: str = "black", maintain_aspect: bool = True,
                     audio_source: str = "first") -> str:
    """
    Create a grid layout with multiple videos in a mosaic pattern.
    
    Args:
        video_paths: List of input video file paths
        output_video_path: Path for the output video file
        grid_size: Grid dimensions ("auto", "2x2", "3x3", "4x2", "2x3", etc.)
        cell_padding: Padding between grid cells (pixels)
        background_color: Background color for the grid
        maintain_aspect: Whether to maintain aspect ratio of individual videos
        audio_source: Audio handling ("first", "mix", "none")
    
    Returns:
        Success message with output file path
    """
    
    if not all(os.path.exists(path) for path in video_paths):
        raise FileNotFoundError("One or more input video files do not exist")
    
    num_videos = len(video_paths)
    if num_videos < 2:
        raise ValueError("Grid requires at least 2 videos")
    
    try:
        # Determine grid dimensions
        if grid_size == "auto":
            if num_videos <= 4:
                rows, cols = 2, 2
            elif num_videos <= 6:
                rows, cols = 2, 3
            elif num_videos <= 9:
                rows, cols = 3, 3
            elif num_videos <= 12:
                rows, cols = 3, 4
            else:
                rows, cols = 4, 4
        else:
            try:
                rows, cols = map(int, grid_size.split('x'))
            except:
                raise ValueError(f"Invalid grid_size format: {grid_size}")
        
        # Ensure we have enough cells
        if rows * cols < num_videos:
            raise ValueError(f"Grid size {rows}x{cols} too small for {num_videos} videos")
        
        # Get reference dimensions
        probe = ffmpeg.probe(video_paths[0])
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        ref_width = int(video_info['width'])
        ref_height = int(video_info['height'])
        
        # Calculate cell dimensions
        total_padding_x = cell_padding * (cols + 1)
        total_padding_y = cell_padding * (rows + 1)
        cell_width = (ref_width - total_padding_x) // cols
        cell_height = (ref_height - total_padding_y) // rows
        
        # Calculate output dimensions
        output_width = cell_width * cols + total_padding_x
        output_height = cell_height * rows + total_padding_y
        
        # Load and scale videos
        inputs = []
        for i, path in enumerate(video_paths):
            inp = ffmpeg.input(path)
            if maintain_aspect:
                # Scale to fit cell while maintaining aspect ratio
                scaled = inp.video.filter('scale', f'{cell_width}:{cell_height}:force_original_aspect_ratio=decrease')
                # Pad to exact cell size
                scaled = scaled.filter('pad', cell_width, cell_height, '(ow-iw)/2', '(oh-ih)/2', background_color)
            else:
                scaled = inp.video.filter('scale', cell_width, cell_height)
            inputs.append(scaled)
        
        # Create background
        background = ffmpeg.input('color={}:size={}x{}:duration=10'.format(
            background_color, output_width, output_height), f='lavfi')
        
        # Build overlay chain
        current = background
        for i, video_input in enumerate(inputs):
            if i >= rows * cols:
                break
                
            row = i // cols
            col = i % cols
            x = cell_padding + col * (cell_width + cell_padding)
            y = cell_padding + row * (cell_height + cell_padding)
            
            current = ffmpeg.overlay(current, video_input, x=x, y=y)
        
        # Handle audio
        if audio_source == "first":
            audio_out = ffmpeg.input(video_paths[0]).audio
        elif audio_source == "mix":
            audio_inputs = [ffmpeg.input(path).audio for path in video_paths[:4]]  # Mix up to 4 audio tracks
            audio_out = ffmpeg.filter(audio_inputs, 'amix', inputs=len(audio_inputs))
        else:  # none
            audio_out = None
        
        # Create output
        if audio_out:
            output = ffmpeg.output(current, audio_out, output_video_path,
                                 vcodec='libx264', acodec='aac', preset='medium', crf=18)
        else:
            output = ffmpeg.output(current, output_video_path,
                                 vcodec='libx264', preset='medium', crf=18)
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully created video grid: {output_video_path}"
        
    except Exception as e:
        return f"Error creating video grid: {str(e)}"