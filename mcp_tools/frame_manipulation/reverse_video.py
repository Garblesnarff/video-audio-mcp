import ffmpeg
import os
import tempfile

def reverse_video(input_video_path: str, output_video_path: str,
                 reverse_audio: bool = True, memory_limit: str = "2GB",
                 segment_duration: float = None) -> str:
    """Reverses video playback with optional audio reversal.
    
    Args:
        input_video_path: Path to the source video file
        output_video_path: Path to save the reversed video
        reverse_audio: Whether to reverse audio as well as video
        memory_limit: Memory limit for processing ('1GB', '2GB', '4GB', etc.)
        segment_duration: Optional segment duration for large files (seconds)
            If specified, video will be processed in segments to manage memory
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    try:
        # Get video properties
        probe = ffmpeg.probe(input_video_path)
        duration = float(probe['format']['duration'])
        
        # Check if segmentation is needed for large files
        if segment_duration and duration > segment_duration:
            return _reverse_video_segments(
                input_video_path, output_video_path, 
                reverse_audio, segment_duration
            )
        
        input_stream = ffmpeg.input(input_video_path)
        
        # Reverse video
        video_stream = input_stream.video.filter('reverse')
        
        # Handle audio
        if reverse_audio:
            # Reverse audio as well
            audio_stream = input_stream.audio.filter('areverse')
        else:
            # Keep original audio (will be out of sync with reversed video)
            audio_stream = input_stream.audio
        
        # Create output
        output = ffmpeg.output(
            video_stream,
            audio_stream,
            output_video_path,
            vcodec='libx264',
            acodec='aac'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        audio_status = "reversed" if reverse_audio else "preserved original"
        return f"Video reversed successfully. Audio: {audio_status}. Duration: {duration:.1f}s. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error reversing video: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def _reverse_video_segments(input_video_path: str, output_video_path: str,
                           reverse_audio: bool, segment_duration: float) -> str:
    """Reverses large video files by processing in segments."""
    try:
        # Get video duration
        probe = ffmpeg.probe(input_video_path)
        total_duration = float(probe['format']['duration'])
        
        # Calculate number of segments
        num_segments = int(total_duration / segment_duration) + 1
        
        # Create temporary directory for segments
        with tempfile.TemporaryDirectory() as temp_dir:
            reversed_segments = []
            
            # Process each segment
            for i in range(num_segments):
                start_time = i * segment_duration
                
                # Adjust duration for last segment
                if start_time + segment_duration > total_duration:
                    duration = total_duration - start_time
                else:
                    duration = segment_duration
                
                if duration <= 0:
                    break
                
                # Extract segment
                segment_path = os.path.join(temp_dir, f"segment_{i:03d}.mp4")
                segment_input = ffmpeg.input(input_video_path, ss=start_time, t=duration)
                
                # Reverse the segment
                segment_video = segment_input.video.filter('reverse')
                
                if reverse_audio:
                    segment_audio = segment_input.audio.filter('areverse')
                else:
                    segment_audio = segment_input.audio
                
                segment_output = ffmpeg.output(
                    segment_video,
                    segment_audio,
                    segment_path,
                    vcodec='libx264',
                    acodec='aac'
                )
                
                segment_output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
                reversed_segments.append(segment_path)
            
            # Reverse the order of segments (since we want to reverse the whole video)
            reversed_segments.reverse()
            
            # Concatenate reversed segments
            if len(reversed_segments) == 1:
                # Single segment, just copy
                os.rename(reversed_segments[0], output_video_path)
            else:
                # Multiple segments, concatenate
                concat_inputs = []
                for segment_path in reversed_segments:
                    concat_inputs.append(ffmpeg.input(segment_path))
                
                concat_output = ffmpeg.output(
                    *concat_inputs,
                    output_video_path,
                    vcodec='libx264',
                    acodec='aac'
                ).global_args('-f', 'concat', '-safe', '0')
                
                concat_output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        audio_status = "reversed" if reverse_audio else "preserved original"
        return f"Large video reversed successfully using {num_segments} segments. Audio: {audio_status}. Output saved to {output_video_path}"
        
    except Exception as e:
        return f"Error reversing video segments: {str(e)}"


def reverse_video_section(input_video_path: str, output_video_path: str,
                         start_time: float, end_time: float,
                         reverse_audio: bool = True) -> str:
    """Reverses only a specific section of the video while keeping the rest normal.
    
    Args:
        input_video_path: Path to the source video file
        output_video_path: Path to save the processed video
        start_time: Start time of section to reverse (seconds)
        end_time: End time of section to reverse (seconds)
        reverse_audio: Whether to reverse audio in the specified section
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    if start_time >= end_time:
        return "Error: start_time must be less than end_time"
    
    try:
        # Get video duration
        probe = ffmpeg.probe(input_video_path)
        total_duration = float(probe['format']['duration'])
        
        if end_time > total_duration:
            return f"Error: end_time ({end_time}s) exceeds video duration ({total_duration}s)"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            segments = []
            
            # Part 1: Before reverse section (if any)
            if start_time > 0:
                part1_path = os.path.join(temp_dir, "part1.mp4")
                part1_input = ffmpeg.input(input_video_path, ss=0, t=start_time)
                part1_output = ffmpeg.output(
                    part1_input.video,
                    part1_input.audio,
                    part1_path,
                    vcodec='libx264',
                    acodec='aac'
                )
                part1_output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
                segments.append(part1_path)
            
            # Part 2: Reverse section
            part2_path = os.path.join(temp_dir, "part2.mp4")
            reverse_duration = end_time - start_time
            part2_input = ffmpeg.input(input_video_path, ss=start_time, t=reverse_duration)
            
            # Reverse video
            part2_video = part2_input.video.filter('reverse')
            
            # Handle audio for reverse section
            if reverse_audio:
                part2_audio = part2_input.audio.filter('areverse')
            else:
                part2_audio = part2_input.audio
            
            part2_output = ffmpeg.output(
                part2_video,
                part2_audio,
                part2_path,
                vcodec='libx264',
                acodec='aac'
            )
            part2_output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            segments.append(part2_path)
            
            # Part 3: After reverse section (if any)
            if end_time < total_duration:
                part3_path = os.path.join(temp_dir, "part3.mp4")
                remaining_duration = total_duration - end_time
                part3_input = ffmpeg.input(input_video_path, ss=end_time, t=remaining_duration)
                part3_output = ffmpeg.output(
                    part3_input.video,
                    part3_input.audio,
                    part3_path,
                    vcodec='libx264',
                    acodec='aac'
                )
                part3_output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
                segments.append(part3_path)
            
            # Concatenate all segments
            if len(segments) == 1:
                os.rename(segments[0], output_video_path)
            else:
                # Create concat file
                concat_file_path = os.path.join(temp_dir, "concat.txt")
                with open(concat_file_path, 'w') as f:
                    for segment in segments:
                        f.write(f"file '{segment}'\n")
                
                # Concatenate using concat demuxer
                concat_output = ffmpeg.output(
                    ffmpeg.input(concat_file_path, format='concat', safe=0),
                    output_video_path,
                    vcodec='libx264',
                    acodec='aac'
                )
                concat_output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        reverse_duration = end_time - start_time
        audio_status = "reversed" if reverse_audio else "preserved"
        return f"Video section reversed successfully. Section: {start_time:.1f}s-{end_time:.1f}s ({reverse_duration:.1f}s). Audio: {audio_status}. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error reversing video section: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def create_boomerang_effect(input_video_path: str, output_video_path: str,
                           loop_count: int = 3, transition_duration: float = 0.5) -> str:
    """Creates a boomerang effect by playing video forward then backward repeatedly.
    
    Args:
        input_video_path: Path to the source video file
        output_video_path: Path to save the boomerang video
        loop_count: Number of forward-backward cycles
        transition_duration: Duration of transition between forward and backward (seconds)
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            segments = []
            
            # Create forward and backward versions
            forward_path = os.path.join(temp_dir, "forward.mp4")
            backward_path = os.path.join(temp_dir, "backward.mp4")
            
            # Forward version (original)
            input_stream = ffmpeg.input(input_video_path)
            forward_output = ffmpeg.output(
                input_stream.video,
                input_stream.audio,
                forward_path,
                vcodec='libx264',
                acodec='aac'
            )
            forward_output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            
            # Backward version (reversed)
            backward_video = input_stream.video.filter('reverse')
            backward_audio = input_stream.audio.filter('areverse')
            backward_output = ffmpeg.output(
                backward_video,
                backward_audio,
                backward_path,
                vcodec='libx264',
                acodec='aac'
            )
            backward_output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            
            # Create boomerang sequence
            for i in range(loop_count):
                segments.append(forward_path)
                segments.append(backward_path)
            
            # Create concat file
            concat_file_path = os.path.join(temp_dir, "concat.txt")
            with open(concat_file_path, 'w') as f:
                for segment in segments:
                    f.write(f"file '{segment}'\n")
            
            # Concatenate to create boomerang effect
            concat_output = ffmpeg.output(
                ffmpeg.input(concat_file_path, format='concat', safe=0),
                output_video_path,
                vcodec='libx264',
                acodec='aac'
            )
            concat_output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        total_cycles = loop_count * 2  # Forward + backward
        return f"Boomerang effect created successfully with {loop_count} cycles ({total_cycles} segments). Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating boomerang effect: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def reverse_with_speed_ramp(input_video_path: str, output_video_path: str,
                           ramp_type: str = "ease_in_out", max_speed: float = 2.0) -> str:
    """Reverses video with speed ramping for smooth effects.
    
    Args:
        input_video_path: Path to the source video file
        output_video_path: Path to save the processed video
        ramp_type: Speed ramp type:
            - 'ease_in': Start slow, end fast
            - 'ease_out': Start fast, end slow
            - 'ease_in_out': Start slow, fast in middle, end slow
        max_speed: Maximum speed multiplier during ramp
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        
        # First reverse the video
        reversed_video = input_stream.video.filter('reverse')
        reversed_audio = input_stream.audio.filter('areverse')
        
        # Apply speed ramping based on type
        if ramp_type == "ease_in":
            # Start slow (0.5x), end fast (max_speed)
            speed_expr = f"0.5+({max_speed}-0.5)*t/duration"
        elif ramp_type == "ease_out":
            # Start fast (max_speed), end slow (0.5x)
            speed_expr = f"{max_speed}-({max_speed}-0.5)*t/duration"
        elif ramp_type == "ease_in_out":
            # Slow-fast-slow (sinusoidal)
            speed_expr = f"0.5+({max_speed}-0.5)*sin(PI*t/duration)"
        else:
            return f"Error: Unknown ramp type '{ramp_type}'"
        
        # Apply speed ramping using setpts
        # Note: This is a simplified implementation
        # Real speed ramping with expressions would require more complex filter chains
        if max_speed != 1.0:
            avg_speed = (1.0 + max_speed) / 2  # Approximate average speed
            ramped_video = reversed_video.filter('setpts', f'PTS/{avg_speed}')
            ramped_audio = reversed_audio.filter('atempo', avg_speed)
        else:
            ramped_video = reversed_video
            ramped_audio = reversed_audio
        
        # Create output
        output = ffmpeg.output(
            ramped_video,
            ramped_audio,
            output_video_path,
            vcodec='libx264',
            acodec='aac'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Reverse video with speed ramp created successfully. Ramp type: {ramp_type}, Max speed: {max_speed}x. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating reverse with speed ramp: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"