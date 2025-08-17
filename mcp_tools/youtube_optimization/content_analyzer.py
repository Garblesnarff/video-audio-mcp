import os
import json
import tempfile
from typing import List, Dict, Tuple, Optional
import ffmpeg

# Optional imports with graceful fallback
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None
    np = None

def detect_scene_changes(video_path: str, 
                        threshold: float = 0.3,
                        min_scene_length: float = 2.0,
                        output_json: str = None) -> str:
    """
    Detect scene changes in video for automatic chapter generation.
    
    Args:
        video_path: Path to input video
        threshold: Scene change detection threshold (0.0-1.0)
        min_scene_length: Minimum scene length in seconds
        output_json: Path to save scene data as JSON
    
    Returns:
        Scene detection results or error message
    """
    
    if not CV2_AVAILABLE:
        return "Error: OpenCV not installed. Install with: pip install opencv-python"
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file does not exist: {video_path}")
    
    try:
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return f"Error: Could not open video file: {video_path}"
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        # Scene detection
        scenes = []
        prev_frame = None
        current_scene_start = 0.0
        frame_count = 0
        
        # Calculate minimum frames for scene length
        min_frames = int(min_scene_length * fps)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            current_time = frame_count / fps
            
            if prev_frame is not None:
                # Convert frames to grayscale for comparison
                gray_current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                
                # Calculate histogram difference
                hist_current = cv2.calcHist([gray_current], [0], None, [256], [0, 256])
                hist_prev = cv2.calcHist([gray_prev], [0], None, [256], [0, 256])
                
                # Normalize histograms
                cv2.normalize(hist_current, hist_current, 0, 1, cv2.NORM_MINMAX)
                cv2.normalize(hist_prev, hist_prev, 0, 1, cv2.NORM_MINMAX)
                
                # Calculate correlation coefficient
                correlation = cv2.compareHist(hist_current, hist_prev, cv2.HISTCMP_CORREL)
                
                # Scene change detected if correlation is below threshold
                if correlation < (1 - threshold) and (frame_count - current_scene_start * fps) > min_frames:
                    # End current scene
                    scene_duration = current_time - current_scene_start
                    scenes.append({
                        "start_time": current_scene_start,
                        "end_time": current_time,
                        "duration": scene_duration,
                        "start_frame": int(current_scene_start * fps),
                        "end_frame": frame_count
                    })
                    
                    # Start new scene
                    current_scene_start = current_time
            
            prev_frame = frame.copy()
            frame_count += 1
            
            # Progress indicator
            if frame_count % 100 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"Scene detection progress: {progress:.1f}%")
        
        # Add final scene
        if current_scene_start < duration:
            scenes.append({
                "start_time": current_scene_start,
                "end_time": duration,
                "duration": duration - current_scene_start,
                "start_frame": int(current_scene_start * fps),
                "end_frame": total_frames
            })
        
        cap.release()
        
        # Save results to JSON if requested
        if output_json:
            scene_data = {
                "video_path": video_path,
                "total_duration": duration,
                "total_scenes": len(scenes),
                "scenes": scenes
            }
            with open(output_json, 'w') as f:
                json.dump(scene_data, f, indent=2)
        
        # Generate summary
        avg_scene_length = sum(scene["duration"] for scene in scenes) / len(scenes) if scenes else 0
        summary = f"Scene detection complete: {len(scenes)} scenes found"
        summary += f"\\nAverage scene length: {avg_scene_length:.1f} seconds"
        summary += f"\\nTotal video duration: {duration:.1f} seconds"
        
        return summary
        
    except Exception as e:
        return f"Error during scene detection: {str(e)}"


def generate_youtube_chapters(video_path: str, 
                            scene_data_path: str = None,
                            transcription_path: str = None,
                            output_path: str = None,
                            min_chapter_length: float = 30.0) -> str:
    """
    Generate YouTube chapters based on scene changes and/or transcription.
    
    Args:
        video_path: Path to input video
        scene_data_path: Path to scene detection JSON (optional)
        transcription_path: Path to transcription file (optional) 
        output_path: Path to save chapter file
        min_chapter_length: Minimum chapter length in seconds
    
    Returns:
        Generated chapters or error message
    """
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file does not exist: {video_path}")
    
    try:
        chapters = []
        
        # Load scene data if provided
        scenes = []
        if scene_data_path and os.path.exists(scene_data_path):
            with open(scene_data_path, 'r') as f:
                scene_data = json.load(f)
                scenes = scene_data.get("scenes", [])
        
        # Load transcription for topic detection if provided
        transcription_segments = []
        if transcription_path and os.path.exists(transcription_path):
            transcription_segments = parse_transcription_file(transcription_path)
        
        # Get video duration
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        cap.release()
        
        if scenes:
            # Use scene-based chapters
            current_chapter_start = 0.0
            chapter_number = 1
            
            for scene in scenes:
                scene_end = scene["end_time"]
                chapter_duration = scene_end - current_chapter_start
                
                # Create chapter if it meets minimum length
                if chapter_duration >= min_chapter_length:
                    # Try to find a good title from transcription
                    chapter_title = f"Chapter {chapter_number}"
                    if transcription_segments:
                        chapter_title = extract_chapter_title(transcription_segments, 
                                                            current_chapter_start, scene_end)
                    
                    chapters.append({
                        "start_time": current_chapter_start,
                        "title": chapter_title,
                        "timestamp": format_youtube_timestamp(current_chapter_start)
                    })
                    
                    current_chapter_start = scene_end
                    chapter_number += 1
        
        else:
            # Create chapters based on time intervals if no scene data
            chapter_interval = max(min_chapter_length, duration / 10)  # Max 10 chapters
            current_time = 0.0
            chapter_number = 1
            
            while current_time < duration:
                chapter_title = f"Chapter {chapter_number}"
                if transcription_segments:
                    end_time = min(current_time + chapter_interval, duration)
                    chapter_title = extract_chapter_title(transcription_segments, 
                                                        current_time, end_time)
                
                chapters.append({
                    "start_time": current_time,
                    "title": chapter_title,
                    "timestamp": format_youtube_timestamp(current_time)
                })
                
                current_time += chapter_interval
                chapter_number += 1
        
        # Format for YouTube description
        youtube_chapters = []
        for chapter in chapters:
            youtube_chapters.append(f"{chapter['timestamp']} {chapter['title']}")
        
        chapter_text = "\\n".join(youtube_chapters)
        
        # Save to file if requested
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(chapter_text)
        
        return f"Generated {len(chapters)} YouTube chapters:\\n\\n{chapter_text}"
        
    except Exception as e:
        return f"Error generating YouTube chapters: {str(e)}"


def analyze_content_density(video_path: str, 
                          window_size: float = 10.0,
                          output_json: str = None) -> str:
    """
    Analyze content density to identify action vs. static segments.
    
    Args:
        video_path: Path to input video
        window_size: Analysis window size in seconds
        output_json: Path to save analysis results
    
    Returns:
        Content density analysis results
    """
    
    if not CV2_AVAILABLE:
        return "Error: OpenCV not installed. Install with: pip install opencv-python"
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file does not exist: {video_path}")
    
    try:
        # Open video
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        # Analysis parameters
        window_frames = int(window_size * fps)
        motion_scores = []
        visual_complexity_scores = []
        
        frame_count = 0
        prev_gray = None
        window_motion = []
        window_complexity = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate motion (optical flow magnitude)
            motion_score = 0
            if prev_gray is not None:
                flow = cv2.calcOpticalFlowPyrLK(prev_gray, gray, 
                                               corners=cv2.goodFeaturesToTrack(prev_gray, 100, 0.3, 7),
                                               nextPts=None,
                                               winSize=(15, 15), maxLevel=2)[0]
                if flow is not None:
                    motion_score = np.mean(np.linalg.norm(flow, axis=2))
            
            # Calculate visual complexity (edge density)
            edges = cv2.Canny(gray, 50, 150)
            complexity_score = np.sum(edges > 0) / (gray.shape[0] * gray.shape[1])
            
            window_motion.append(motion_score)
            window_complexity.append(complexity_score)
            
            # Process window when full
            if len(window_motion) >= window_frames:
                avg_motion = np.mean(window_motion)
                avg_complexity = np.mean(window_complexity)
                
                timestamp = frame_count / fps
                motion_scores.append({
                    "timestamp": timestamp,
                    "motion_score": avg_motion,
                    "complexity_score": avg_complexity,
                    "combined_score": (avg_motion + avg_complexity) / 2
                })
                
                # Slide window
                window_motion = window_motion[window_frames//2:]
                window_complexity = window_complexity[window_frames//2:]
            
            prev_gray = gray
            frame_count += 1
            
            # Progress indicator
            if frame_count % 100 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"Content analysis progress: {progress:.1f}%")
        
        cap.release()
        
        # Analyze results
        if motion_scores:
            avg_motion = np.mean([s["motion_score"] for s in motion_scores])
            avg_complexity = np.mean([s["complexity_score"] for s in motion_scores])
            
            # Identify high-action segments
            high_action_threshold = avg_motion + np.std([s["motion_score"] for s in motion_scores])
            high_action_segments = [s for s in motion_scores if s["motion_score"] > high_action_threshold]
            
            # Identify visually complex segments
            high_complexity_threshold = avg_complexity + np.std([s["complexity_score"] for s in motion_scores])
            complex_segments = [s for s in motion_scores if s["complexity_score"] > high_complexity_threshold]
            
            analysis_results = {
                "video_path": video_path,
                "total_duration": duration,
                "window_size": window_size,
                "average_motion": avg_motion,
                "average_complexity": avg_complexity,
                "high_action_segments": len(high_action_segments),
                "complex_segments": len(complex_segments),
                "detailed_scores": motion_scores
            }
            
            # Save results
            if output_json:
                with open(output_json, 'w') as f:
                    json.dump(analysis_results, f, indent=2)
            
            summary = f"Content density analysis complete"
            summary += f"\\nAverage motion score: {avg_motion:.3f}"
            summary += f"\\nAverage complexity score: {avg_complexity:.3f}"
            summary += f"\\nHigh-action segments: {len(high_action_segments)}"
            summary += f"\\nComplex segments: {len(complex_segments)}"
            
            return summary
        
        return "No analysis data generated"
        
    except Exception as e:
        return f"Error during content analysis: {str(e)}"


def extract_youtube_shorts(video_path: str, 
                          output_directory: str,
                          max_duration: float = 60.0,
                          target_aspect: str = "9:16",
                          use_content_analysis: bool = True) -> str:
    """
    Extract YouTube Shorts from longer video based on content analysis.
    
    Args:
        video_path: Path to input video
        output_directory: Directory for Shorts outputs
        max_duration: Maximum duration for each Short
        target_aspect: Target aspect ratio for Shorts
        use_content_analysis: Whether to use AI to find best segments
    
    Returns:
        Summary of Shorts extraction
    """
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file does not exist: {video_path}")
    
    # Note: CV2 is optional for this function - it can work without content analysis
    try:
        os.makedirs(output_directory, exist_ok=True)
        
        # Get video properties
        probe = ffmpeg.probe(video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        duration = float(video_info['duration'])
        width = int(video_info['width'])
        height = int(video_info['height'])
        
        if duration <= max_duration:
            return f"Video is already short enough ({duration:.1f}s <= {max_duration}s)"
        
        segments = []
        
        if use_content_analysis and CV2_AVAILABLE:
            # Analyze content to find interesting segments
            try:
                from ultralytics import YOLO
                model = YOLO("yolov8n.pt")
                
                # Sample frames and find high-activity periods
                cap = cv2.VideoCapture(video_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                activity_scores = []
                frame_count = 0
                
                # Sample every second
                sample_interval = int(fps)
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    if frame_count % sample_interval == 0:
                        timestamp = frame_count / fps
                        
                        # Object detection for activity score
                        results = model(frame, conf=0.3)
                        num_objects = len(results[0].boxes) if results[0].boxes else 0
                        
                        # Motion estimation (simple approach)
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        motion_score = cv2.Laplacian(gray, cv2.CV_64F).var()
                        
                        activity_score = num_objects * 10 + motion_score / 1000
                        activity_scores.append({
                            "timestamp": timestamp,
                            "score": activity_score
                        })
                    
                    frame_count += 1
                
                cap.release()
                
                # Find peak activity periods
                if activity_scores:
                    # Sort by activity score
                    activity_scores.sort(key=lambda x: x["score"], reverse=True)
                    
                    # Select top segments, ensuring they don't overlap
                    selected_times = []
                    for score_data in activity_scores:
                        timestamp = score_data["timestamp"]
                        
                        # Check if this segment overlaps with existing selections
                        overlap = False
                        for selected_start in selected_times:
                            if abs(timestamp - selected_start) < max_duration:
                                overlap = True
                                break
                        
                        if not overlap:
                            # Ensure segment fits within video duration
                            start_time = max(0, timestamp - max_duration / 2)
                            end_time = min(duration, start_time + max_duration)
                            start_time = end_time - max_duration  # Adjust start if needed
                            
                            if start_time >= 0:
                                segments.append({
                                    "start": start_time,
                                    "duration": max_duration,
                                    "score": score_data["score"]
                                })
                                selected_times.append(start_time)
                            
                            # Limit number of shorts
                            if len(segments) >= 3:
                                break
                
            except ImportError:
                # Fallback to simple time-based extraction
                use_content_analysis = False
        
        if not use_content_analysis or not segments:
            # Simple time-based extraction
            num_segments = min(3, int(duration / max_duration))
            segment_interval = duration / (num_segments + 1)
            
            segments = []
            for i in range(num_segments):
                start_time = segment_interval * (i + 1) - max_duration / 2
                start_time = max(0, start_time)
                
                if start_time + max_duration <= duration:
                    segments.append({
                        "start": start_time,
                        "duration": max_duration,
                        "score": 0
                    })
        
        # Create Shorts from segments
        created_shorts = []
        for i, segment in enumerate(segments):
            short_path = os.path.join(output_directory, f"short_{i+1:02d}.mp4")
            
            # Extract segment
            input_stream = ffmpeg.input(video_path, ss=segment["start"], t=segment["duration"])
            
            # Convert to target aspect ratio
            if target_aspect == "9:16":
                # Portrait mode for Shorts
                if width > height:
                    # Landscape to portrait - crop to center square then letterbox
                    crop_size = min(width, height)
                    video_stream = input_stream.video.filter('crop', crop_size, crop_size, 
                                                           (width - crop_size) // 2, 0)
                    # Scale to 1080x1920 for 9:16
                    video_stream = video_stream.filter('scale', 1080, 1920, force_original_aspect_ratio='increase')
                    video_stream = video_stream.filter('crop', 1080, 1920)
                else:
                    # Already portrait or square
                    video_stream = input_stream.video.filter('scale', 1080, 1920, force_original_aspect_ratio='decrease')
                    video_stream = video_stream.filter('pad', 1080, 1920, '(ow-iw)/2', '(oh-ih)/2', 'black')
            else:
                video_stream = input_stream.video
            
            # Output
            output = ffmpeg.output(video_stream, input_stream.audio, short_path,
                                 vcodec='libx264', acodec='aac',
                                 preset='medium', crf=18)
            
            ffmpeg.run(output, overwrite_output=True, quiet=True)
            created_shorts.append(short_path)
        
        return f"Successfully created {len(created_shorts)} YouTube Shorts in {output_directory}"
        
    except Exception as e:
        return f"Error extracting YouTube Shorts: {str(e)}"


def parse_transcription_file(file_path: str) -> List[Dict]:
    """Parse transcription file (SRT, VTT, or JSON) into segments."""
    segments = []
    
    try:
        if file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'segments' in data:
                    segments = data['segments']
        
        elif file_path.endswith('.srt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple SRT parsing
                blocks = content.strip().split('\\n\\n')
                for block in blocks:
                    lines = block.strip().split('\\n')
                    if len(lines) >= 3:
                        time_line = lines[1]
                        text = ' '.join(lines[2:])
                        
                        # Parse timestamp
                        if ' --> ' in time_line:
                            start_str, end_str = time_line.split(' --> ')
                            start_time = parse_srt_timestamp(start_str)
                            end_time = parse_srt_timestamp(end_str)
                            
                            segments.append({
                                'start': start_time,
                                'end': end_time,
                                'text': text
                            })
        
    except Exception as e:
        print(f"Error parsing transcription file: {e}")
    
    return segments


def parse_srt_timestamp(timestamp_str: str) -> float:
    """Parse SRT timestamp to seconds."""
    # Format: HH:MM:SS,mmm
    time_part, ms_part = timestamp_str.strip().split(',')
    h, m, s = map(int, time_part.split(':'))
    ms = int(ms_part)
    
    return h * 3600 + m * 60 + s + ms / 1000


def extract_chapter_title(transcription_segments: List[Dict], 
                         start_time: float, end_time: float) -> str:
    """Extract a meaningful chapter title from transcription."""
    # Find transcription segments in this time range
    relevant_text = []
    
    for segment in transcription_segments:
        seg_start = segment.get('start', 0)
        seg_end = segment.get('end', seg_start)
        
        # Check if segment overlaps with chapter timeframe
        if (seg_start <= end_time and seg_end >= start_time):
            text = segment.get('text', '').strip()
            if text:
                relevant_text.append(text)
    
    if relevant_text:
        # Simple approach: use first few words from the beginning
        full_text = ' '.join(relevant_text)
        words = full_text.split()
        
        # Extract key phrases (simple approach)
        if len(words) >= 3:
            return ' '.join(words[:6])  # First 6 words
        else:
            return full_text
    
    # Fallback
    minutes = int(start_time // 60)
    seconds = int(start_time % 60)
    return f"Chapter at {minutes:02d}:{seconds:02d}"


def format_youtube_timestamp(seconds: float) -> str:
    """Format seconds as YouTube timestamp (MM:SS or H:MM:SS)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"