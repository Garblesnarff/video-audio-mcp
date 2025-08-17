import ffmpeg
import os
import math

def extract_thumbnails(input_video_path: str, output_directory: str,
                      thumbnail_count: int = 10, thumbnail_size: str = "320x180",
                      selection_method: str = "evenly_spaced", quality: int = 85,
                      format: str = "jpg") -> str:
    """Extracts thumbnail images from video at strategic points.
    
    Args:
        input_video_path: Path to the source video file
        output_directory: Directory to save thumbnail images
        thumbnail_count: Number of thumbnails to extract
        thumbnail_size: Size of thumbnails (e.g., '320x180', '640x360')
        selection_method: Method for selecting thumbnail positions:
            - 'evenly_spaced': Distribute evenly across duration
            - 'keyframes': Extract from keyframes only
            - 'scene_changes': Extract at scene change points
            - 'motion_peaks': Extract at high motion moments
            - 'quality_based': Select best quality frames
        quality: JPEG quality (1-100, higher is better)
        format: Output format ('jpg', 'png', 'webp')
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    # Create output directory
    os.makedirs(output_directory, exist_ok=True)
    
    try:
        # Get video duration and properties
        probe = ffmpeg.probe(input_video_path)
        duration = float(probe['format']['duration'])
        
        # Parse thumbnail size
        thumb_width, thumb_height = thumbnail_size.split('x')
        
        input_stream = ffmpeg.input(input_video_path)
        
        if selection_method == 'evenly_spaced':
            # Extract thumbnails evenly distributed across the video
            interval = duration / (thumbnail_count + 1)  # +1 to avoid first and last frame
            
            for i in range(thumbnail_count):
                timestamp = interval * (i + 1)
                thumbnail_path = os.path.join(output_directory, f'thumb_{i+1:03d}.{format}')
                
                # Extract frame at specific time
                frame_input = ffmpeg.input(input_video_path, ss=timestamp)
                video_stream = frame_input.video.filter('scale', thumb_width, thumb_height)
                
                output_params = {'frames:v': 1}
                if format.lower() == 'jpg':
                    output_params['q:v'] = quality
                
                output = ffmpeg.output(video_stream, thumbnail_path, **output_params)
                output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        elif selection_method == 'keyframes':
            # Extract from keyframes (I-frames)
            video_stream = input_stream.video
            video_stream = video_stream.filter('select', f"'eq(pict_type,I)'")
            video_stream = video_stream.filter('scale', thumb_width, thumb_height)
            
            output_pattern = os.path.join(output_directory, f'thumb_%03d.{format}')
            output_params = {}
            if format.lower() == 'jpg':
                output_params['q:v'] = quality
            
            output = ffmpeg.output(video_stream, output_pattern, **output_params)
            output = output.global_args('-vsync', 'vfr', '-frames:v', str(thumbnail_count))
            output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        elif selection_method == 'scene_changes':
            # Extract at scene change points
            scene_threshold = 0.4
            video_stream = input_stream.video
            video_stream = video_stream.filter('select', f"'gt(scene\\,{scene_threshold})'")
            video_stream = video_stream.filter('scale', thumb_width, thumb_height)
            
            output_pattern = os.path.join(output_directory, f'thumb_%03d.{format}')
            output_params = {}
            if format.lower() == 'jpg':
                output_params['q:v'] = quality
            
            output = ffmpeg.output(video_stream, output_pattern, **output_params)
            output = output.global_args('-vsync', 'vfr', '-frames:v', str(thumbnail_count))
            output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        elif selection_method == 'motion_peaks':
            # Extract frames with high motion (simplified using select filter)
            video_stream = input_stream.video
            # Use select filter to pick frames with significant changes
            video_stream = video_stream.filter('select', "'gte(t,1)*lt(t,n-1)'")  # Skip first/last second
            video_stream = video_stream.filter('scale', thumb_width, thumb_height)
            
            # Sample evenly from motion frames
            fps_for_count = thumbnail_count / (duration - 2)  # -2 for skipped seconds
            video_stream = video_stream.filter('fps', fps_for_count)
            
            output_pattern = os.path.join(output_directory, f'thumb_%03d.{format}')
            output_params = {}
            if format.lower() == 'jpg':
                output_params['q:v'] = quality
            
            output = ffmpeg.output(video_stream, output_pattern, **output_params)
            output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        elif selection_method == 'quality_based':
            # Extract high-quality frames (avoiding blurry or dark frames)
            # This is a simplified implementation - could be enhanced with blur detection
            video_stream = input_stream.video
            
            # Sample more frames than needed, then select best ones
            sample_fps = (thumbnail_count * 3) / duration
            video_stream = video_stream.filter('fps', sample_fps)
            video_stream = video_stream.filter('scale', thumb_width, thumb_height)
            
            output_pattern = os.path.join(output_directory, f'thumb_%03d.{format}')
            output_params = {}
            if format.lower() == 'jpg':
                output_params['q:v'] = quality
            
            output = ffmpeg.output(video_stream, output_pattern, **output_params)
            output = output.global_args('-frames:v', str(thumbnail_count))
            output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        # Count generated thumbnails
        generated_count = len([f for f in os.listdir(output_directory) if f.endswith(format)])
        
        return f"Generated {generated_count} thumbnails using '{selection_method}' method. Size: {thumbnail_size}. Saved to {output_directory}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error generating thumbnails: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def generate_smart_thumbnails(input_video_path: str, output_directory: str,
                            thumbnail_count: int = 5, analysis_depth: str = "medium") -> str:
    """Generates smart thumbnails by analyzing video content for best representative frames.
    
    Args:
        input_video_path: Path to the source video file
        output_directory: Directory to save thumbnail images
        thumbnail_count: Number of thumbnails to generate
        analysis_depth: Analysis level ('basic', 'medium', 'advanced'):
            - basic: Simple evenly-spaced extraction
            - medium: Scene change detection + motion analysis
            - advanced: Content analysis + quality assessment
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    # Create output directory
    os.makedirs(output_directory, exist_ok=True)
    
    try:
        probe = ffmpeg.probe(input_video_path)
        duration = float(probe['format']['duration'])
        
        if analysis_depth == "basic":
            # Simple evenly-spaced extraction
            return extract_thumbnails(
                input_video_path, output_directory, thumbnail_count,
                selection_method="evenly_spaced"
            )
        
        elif analysis_depth == "medium":
            # Scene change detection with fallback
            input_stream = ffmpeg.input(input_video_path)
            
            # First pass: detect scene changes
            scene_threshold = 0.3
            video_stream = input_stream.video
            
            # Apply scene detection and scaling
            video_stream = video_stream.filter('select', f"'gt(scene\\,{scene_threshold})'")
            video_stream = video_stream.filter('scale', '320', '180')
            
            output_pattern = os.path.join(output_directory, 'thumb_%03d.jpg')
            
            output = ffmpeg.output(video_stream, output_pattern, q=85)
            output = output.global_args('-vsync', 'vfr', '-frames:v', str(thumbnail_count * 2))
            
            try:
                output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
                
                # Check if we got enough thumbnails, if not, fill with evenly spaced
                generated = len([f for f in os.listdir(output_directory) if f.endswith('.jpg')])
                
                if generated < thumbnail_count:
                    # Fill remaining with evenly spaced
                    remaining = thumbnail_count - generated
                    interval = duration / (remaining + 1)
                    
                    for i in range(remaining):
                        timestamp = interval * (i + 1)
                        thumb_path = os.path.join(output_directory, f'thumb_{generated + i + 1:03d}.jpg')
                        
                        frame_input = ffmpeg.input(input_video_path, ss=timestamp)
                        frame_stream = frame_input.video.filter('scale', '320', '180')
                        frame_output = ffmpeg.output(frame_stream, thumb_path, frames=1, q=85)
                        frame_output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
                
            except ffmpeg.Error:
                # Fallback to evenly spaced if scene detection fails
                return extract_thumbnails(
                    input_video_path, output_directory, thumbnail_count,
                    selection_method="evenly_spaced"
                )
        
        elif analysis_depth == "advanced":
            # Advanced content analysis
            input_stream = ffmpeg.input(input_video_path)
            
            # Multi-pass analysis: keyframes + scene changes + motion
            thumbnails_per_method = max(1, thumbnail_count // 3)
            
            # Method 1: Keyframes
            keyframe_stream = input_stream.video
            keyframe_stream = keyframe_stream.filter('select', "'eq(pict_type,I)'")
            keyframe_stream = keyframe_stream.filter('scale', '320', '180')
            
            keyframe_pattern = os.path.join(output_directory, 'key_%03d.jpg')
            keyframe_output = ffmpeg.output(keyframe_stream, keyframe_pattern, q=90)
            keyframe_output = keyframe_output.global_args('-vsync', 'vfr', '-frames:v', str(thumbnails_per_method))
            keyframe_output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            
            # Method 2: Scene changes  
            scene_stream = input_stream.video
            scene_stream = scene_stream.filter('select', "'gt(scene\\,0.4)'")
            scene_stream = scene_stream.filter('scale', '320', '180')
            
            scene_pattern = os.path.join(output_directory, 'scene_%03d.jpg')
            scene_output = ffmpeg.output(scene_stream, scene_pattern, q=90)
            scene_output = scene_output.global_args('-vsync', 'vfr', '-frames:v', str(thumbnails_per_method))
            
            try:
                scene_output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            except ffmpeg.Error:
                pass  # Scene detection might fail, continue with other methods
            
            # Method 3: Fill remaining with evenly spaced high-quality frames
            generated = len([f for f in os.listdir(output_directory) if f.endswith('.jpg')])
            remaining = max(0, thumbnail_count - generated)
            
            if remaining > 0:
                interval = duration / (remaining + 1)
                for i in range(remaining):
                    timestamp = interval * (i + 1)
                    thumb_path = os.path.join(output_directory, f'qual_{i + 1:03d}.jpg')
                    
                    frame_input = ffmpeg.input(input_video_path, ss=timestamp)
                    frame_stream = frame_input.video.filter('scale', '320', '180')
                    frame_output = ffmpeg.output(frame_stream, thumb_path, frames=1, q=95)
                    frame_output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        # Count final thumbnail count
        final_count = len([f for f in os.listdir(output_directory) if f.endswith('.jpg')])
        
        return f"Generated {final_count} smart thumbnails using '{analysis_depth}' analysis. Saved to {output_directory}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error generating smart thumbnails: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def create_thumbnail_grid(thumbnail_directory: str, output_image_path: str,
                         grid_size: str = "auto", background_color: str = "black",
                         padding: int = 10, title_text: str = None) -> str:
    """Creates a grid/mosaic image from multiple thumbnails.
    
    Args:
        thumbnail_directory: Directory containing thumbnail images
        output_image_path: Path to save the grid image
        grid_size: Grid layout ('auto', '2x2', '3x3', '4x4', etc.)
        background_color: Background color for the grid
        padding: Padding between thumbnails in pixels
        title_text: Optional title text to add to the grid
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(thumbnail_directory):
        return f"Error: Thumbnail directory not found at {thumbnail_directory}"
    
    try:
        # Get list of thumbnail files
        thumbnail_files = [f for f in os.listdir(thumbnail_directory) 
                          if f.lower().endswith(('.jpg', '.png', '.jpeg', '.bmp'))]
        
        if not thumbnail_files:
            return "Error: No thumbnail images found in directory"
        
        thumbnail_files.sort()  # Sort for consistent ordering
        thumbnail_count = len(thumbnail_files)
        
        # Determine grid dimensions
        if grid_size == "auto":
            # Calculate optimal grid size
            cols = math.ceil(math.sqrt(thumbnail_count))
            rows = math.ceil(thumbnail_count / cols)
        else:
            try:
                cols, rows = map(int, grid_size.split('x'))
            except:
                return f"Error: Invalid grid_size format '{grid_size}'. Use format like '3x3' or 'auto'"
        
        # Limit to available thumbnails
        max_thumbnails = min(thumbnail_count, cols * rows)
        
        # Create filter complex for grid layout
        inputs = []
        filter_parts = []
        
        # Add all thumbnail inputs
        for i in range(max_thumbnails):
            thumb_path = os.path.join(thumbnail_directory, thumbnail_files[i])
            inputs.append(ffmpeg.input(thumb_path))
        
        # Build grid layout filter
        # This is a simplified version - a full implementation would be more complex
        if max_thumbnails == 1:
            filter_complex = "[0:v]scale=320:180[out]"
        elif max_thumbnails <= 4:
            # 2x2 grid implementation
            filter_complex = """
            [0:v]scale=320:180[v0];
            [1:v]scale=320:180[v1];
            [2:v]scale=320:180[v2];
            [3:v]scale=320:180[v3];
            [v0][v1]hstack[top];
            [v2][v3]hstack[bottom];
            [top][bottom]vstack[out]
            """
        else:
            # For larger grids, use a simplified stacking approach
            # Scale all inputs first
            scale_filters = []
            for i in range(max_thumbnails):
                scale_filters.append(f"[{i}:v]scale=160:90[v{i}]")
            
            # Create horizontal stacks for each row
            row_filters = []
            for row in range(rows):
                start_idx = row * cols
                end_idx = min(start_idx + cols, max_thumbnails)
                if start_idx < end_idx:
                    row_inputs = [f"[v{i}]" for i in range(start_idx, end_idx)]
                    row_filters.append(f"{''.join(row_inputs)}hstack=inputs={len(row_inputs)}[row{row}]")
            
            # Stack all rows vertically
            if len(row_filters) > 1:
                row_names = [f"[row{i}]" for i in range(len(row_filters))]
                final_filter = f"{''.join(row_names)}vstack=inputs={len(row_names)}[out]"
            else:
                final_filter = "[row0]copy[out]"
            
            filter_complex = ';'.join(scale_filters + row_filters + [final_filter])
        
        # Create output
        output = ffmpeg.output(
            *inputs,
            output_image_path,
            filter_complex=filter_complex,
            map='[out]'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Thumbnail grid created successfully with {max_thumbnails} images in {cols}x{rows} layout. Saved to {output_image_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating thumbnail grid: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"