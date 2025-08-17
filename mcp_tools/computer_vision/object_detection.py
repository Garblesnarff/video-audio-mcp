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

def detect_objects_yolo(video_path: str, 
                       output_video_path: str = None,
                       model_type: str = "yolov8n",
                       confidence_threshold: float = 0.5,
                       draw_boxes: bool = True,
                       target_classes: List[str] = None,
                       output_json: str = None) -> str:
    """
    Detect objects in video using YOLO and optionally draw bounding boxes.
    
    Args:
        video_path: Path to input video
        output_video_path: Path for output video with drawn boxes (optional)
        model_type: YOLO model type ("yolov8n", "yolov8s", "yolov8m", "yolov8l", "yolov8x")
        confidence_threshold: Minimum confidence for detections
        draw_boxes: Whether to draw bounding boxes on video
        target_classes: List of specific classes to detect (None for all)
        output_json: Path to save detection results as JSON
    
    Returns:
        Detection results summary or error message
    """
    
    if not CV2_AVAILABLE:
        return "Error: OpenCV not installed. Install with: pip install opencv-python"
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file does not exist: {video_path}")
    
    try:
        # Try to import YOLOv8 (ultralytics)
        try:
            from ultralytics import YOLO
            use_ultralytics = True
        except ImportError:
            try:
                import yolov5
                use_ultralytics = False
            except ImportError:
                return "Error: YOLO not installed. Install with: pip install ultralytics"
        
        # Load YOLO model
        if use_ultralytics:
            model = YOLO(f"{model_type}.pt")
        else:
            model = yolov5.load(model_type)
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return f"Error: Could not open video file: {video_path}"
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Setup video writer if output path provided
        out = None
        if output_video_path and draw_boxes:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        # Detection results storage
        all_detections = []
        frame_number = 0
        
        # Process video frame by frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run YOLO detection
            if use_ultralytics:
                results = model(frame, conf=confidence_threshold)
                detections = process_ultralytics_results(results[0], target_classes)
            else:
                results = model(frame)
                detections = process_yolov5_results(results, confidence_threshold, target_classes)
            
            # Store detections with frame info
            frame_detections = {
                "frame": frame_number,
                "timestamp": frame_number / fps,
                "detections": detections
            }
            all_detections.append(frame_detections)
            
            # Draw bounding boxes if requested
            if draw_boxes and detections:
                frame = draw_detection_boxes(frame, detections)
            
            # Write frame to output video
            if out is not None:
                out.write(frame)
            
            frame_number += 1
            
            # Progress indicator (every 30 frames)
            if frame_number % 30 == 0:
                progress = (frame_number / total_frames) * 100
                print(f"Processing: {progress:.1f}%")
        
        # Cleanup
        cap.release()
        if out is not None:
            out.release()
        
        # Save detection results to JSON if requested
        if output_json:
            with open(output_json, 'w') as f:
                json.dump(all_detections, f, indent=2)
        
        # Generate summary
        total_detections = sum(len(frame["detections"]) for frame in all_detections)
        unique_classes = set()
        for frame in all_detections:
            for det in frame["detections"]:
                unique_classes.add(det["class"])
        
        summary = f"Detection complete: {total_detections} objects detected across {frame_number} frames"
        summary += f"\\nUnique classes found: {', '.join(sorted(unique_classes))}"
        if output_video_path:
            summary += f"\\nOutput video saved: {output_video_path}"
        if output_json:
            summary += f"\\nDetection data saved: {output_json}"
        
        return summary
        
    except Exception as e:
        return f"Error during object detection: {str(e)}"


def generate_smart_thumbnails_ai(video_path: str, 
                                output_directory: str,
                                num_thumbnails: int = 5,
                                focus_on_objects: bool = True,
                                preferred_classes: List[str] = None) -> str:
    """
    Generate smart thumbnails using AI object detection to find interesting frames.
    
    Args:
        video_path: Path to input video
        output_directory: Directory to save thumbnails
        num_thumbnails: Number of thumbnails to generate
        focus_on_objects: Whether to prioritize frames with detected objects
        preferred_classes: List of object classes to prioritize (e.g., ["person", "face"])
    
    Returns:
        Summary of thumbnail generation
    """
    
    if not CV2_AVAILABLE:
        return "Error: OpenCV not installed. Install with: pip install opencv-python"
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file does not exist: {video_path}")
    
    try:
        from ultralytics import YOLO
        
        # Load YOLO model
        model = YOLO("yolov8n.pt")
        
        # Default preferred classes for thumbnails
        if not preferred_classes:
            preferred_classes = ["person", "face", "cat", "dog", "car", "bicycle"]
        
        os.makedirs(output_directory, exist_ok=True)
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Sample frames throughout the video
        sample_frames = np.linspace(0, total_frames - 1, num_thumbnails * 10, dtype=int)
        frame_scores = []
        
        for frame_idx in sample_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Calculate frame score based on content
            score = 0
            
            if focus_on_objects:
                # Run object detection
                results = model(frame, conf=0.3)
                detections = process_ultralytics_results(results[0])
                
                # Score based on object presence and types
                for det in detections:
                    if det["class"] in preferred_classes:
                        score += det["confidence"] * 2  # Bonus for preferred classes
                    else:
                        score += det["confidence"]
                
                # Bonus for multiple objects (more interesting)
                if len(detections) > 1:
                    score *= 1.2
            
            # Visual quality score (contrast, sharpness)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Sharpness (Laplacian variance)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            score += sharpness / 1000  # Normalize
            
            # Contrast (standard deviation)
            contrast = gray.std()
            score += contrast / 100  # Normalize
            
            frame_scores.append({
                "frame_idx": frame_idx,
                "timestamp": frame_idx / fps,
                "score": score,
                "frame": frame.copy()
            })
        
        # Sort by score and select top frames
        frame_scores.sort(key=lambda x: x["score"], reverse=True)
        selected_frames = frame_scores[:num_thumbnails]
        
        # Save thumbnails
        saved_count = 0
        for i, frame_data in enumerate(selected_frames):
            timestamp = frame_data["timestamp"]
            frame = frame_data["frame"]
            
            # Generate filename with timestamp
            thumbnail_path = os.path.join(output_directory, 
                                        f"thumbnail_{i+1:02d}_{timestamp:.1f}s.jpg")
            
            # Save thumbnail
            cv2.imwrite(thumbnail_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            saved_count += 1
        
        cap.release()
        
        return f"Successfully generated {saved_count} AI-powered thumbnails in {output_directory}"
        
    except Exception as e:
        return f"Error generating smart thumbnails: {str(e)}"


def auto_crop_to_subject(video_path: str, output_video_path: str,
                        target_class: str = "person",
                        padding_ratio: float = 0.2,
                        smooth_tracking: bool = True) -> str:
    """
    Automatically crop video to focus on detected subject (person, face, etc.).
    
    Args:
        video_path: Path to input video
        output_video_path: Path for cropped output video
        target_class: Object class to focus on ("person", "face", "car", etc.)
        padding_ratio: Extra padding around detected object (0.0-1.0)
        smooth_tracking: Whether to apply smoothing to reduce jitter
    
    Returns:
        Success message or error
    """
    
    if not CV2_AVAILABLE:
        return "Error: OpenCV not installed. Install with: pip install opencv-python"
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file does not exist: {video_path}")
    
    try:
        from ultralytics import YOLO
        
        # Load YOLO model
        model = YOLO("yolov8n.pt")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Determine crop size (square crop for social media)
        crop_size = min(width, height)
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (crop_size, crop_size))
        
        # Tracking variables
        prev_center = None
        smoothing_factor = 0.8 if smooth_tracking else 0
        
        frame_count = 0
        successful_crops = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run object detection
            results = model(frame, conf=0.5)
            detections = process_ultralytics_results(results[0], [target_class])
            
            if detections:
                # Find the largest/most confident detection
                best_detection = max(detections, 
                                   key=lambda x: x["confidence"] * x["area"])
                
                # Calculate crop center
                bbox = best_detection["bbox"]
                center_x = bbox[0] + bbox[2] // 2
                center_y = bbox[1] + bbox[3] // 2
                
                # Apply smoothing
                if prev_center and smooth_tracking:
                    center_x = int(smoothing_factor * prev_center[0] + (1 - smoothing_factor) * center_x)
                    center_y = int(smoothing_factor * prev_center[1] + (1 - smoothing_factor) * center_y)
                
                prev_center = (center_x, center_y)
                
            else:
                # No detection - use previous center or video center
                if prev_center:
                    center_x, center_y = prev_center
                else:
                    center_x, center_y = width // 2, height // 2
            
            # Calculate crop boundaries
            half_crop = crop_size // 2
            x1 = max(0, center_x - half_crop)
            y1 = max(0, center_y - half_crop)
            x2 = min(width, x1 + crop_size)
            y2 = min(height, y1 + crop_size)
            
            # Adjust if crop goes out of bounds
            if x2 - x1 < crop_size:
                x1 = max(0, x2 - crop_size)
            if y2 - y1 < crop_size:
                y1 = max(0, y2 - crop_size)
            
            # Crop frame
            cropped_frame = frame[y1:y2, x1:x2]
            
            # Ensure exact crop size
            if cropped_frame.shape[:2] != (crop_size, crop_size):
                cropped_frame = cv2.resize(cropped_frame, (crop_size, crop_size))
            
            out.write(cropped_frame)
            successful_crops += 1
            frame_count += 1
        
        # Cleanup
        cap.release()
        out.release()
        
        return f"Successfully auto-cropped video focusing on {target_class}: {output_video_path} ({successful_crops} frames processed)"
        
    except Exception as e:
        return f"Error during auto-cropping: {str(e)}"


def process_ultralytics_results(results, target_classes=None):
    """Process YOLOv8 detection results."""
    detections = []
    
    if hasattr(results, 'boxes') and results.boxes is not None:
        boxes = results.boxes
        for i in range(len(boxes)):
            # Get class name
            class_id = int(boxes.cls[i])
            class_name = results.names[class_id]
            
            # Filter by target classes if specified
            if target_classes and class_name not in target_classes:
                continue
            
            # Get bounding box coordinates
            bbox = boxes.xyxy[i].cpu().numpy().astype(int)
            confidence = float(boxes.conf[i])
            
            detection = {
                "class": class_name,
                "confidence": confidence,
                "bbox": [int(bbox[0]), int(bbox[1]), int(bbox[2] - bbox[0]), int(bbox[3] - bbox[1])],
                "area": (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            }
            detections.append(detection)
    
    return detections


def process_yolov5_results(results, confidence_threshold, target_classes=None):
    """Process YOLOv5 detection results."""
    detections = []
    
    # Convert results to pandas DataFrame
    df = results.pandas().xyxy[0]
    
    for _, row in df.iterrows():
        if row['confidence'] < confidence_threshold:
            continue
        
        class_name = row['name']
        if target_classes and class_name not in target_classes:
            continue
        
        detection = {
            "class": class_name,
            "confidence": row['confidence'],
            "bbox": [int(row['xmin']), int(row['ymin']), 
                    int(row['xmax'] - row['xmin']), int(row['ymax'] - row['ymin'])],
            "area": (row['xmax'] - row['xmin']) * (row['ymax'] - row['ymin'])
        }
        detections.append(detection)
    
    return detections


def draw_detection_boxes(frame, detections):
    """Draw bounding boxes and labels on frame."""
    for det in detections:
        bbox = det["bbox"]
        class_name = det["class"]
        confidence = det["confidence"]
        
        # Draw bounding box
        cv2.rectangle(frame, 
                     (bbox[0], bbox[1]), 
                     (bbox[0] + bbox[2], bbox[1] + bbox[3]), 
                     (0, 255, 0), 2)
        
        # Draw label
        label = f"{class_name}: {confidence:.2f}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        
        # Draw label background
        cv2.rectangle(frame,
                     (bbox[0], bbox[1] - label_size[1] - 10),
                     (bbox[0] + label_size[0], bbox[1]),
                     (0, 255, 0), -1)
        
        # Draw label text
        cv2.putText(frame, label,
                   (bbox[0], bbox[1] - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    return frame