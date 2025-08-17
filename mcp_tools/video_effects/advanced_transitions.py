import ffmpeg
import os
import tempfile
import math

def apply_advanced_transitions(video_paths: list[str], output_video_path: str,
                             transition_type: str, transition_duration: float = 1.0,
                             direction: str = "right", custom_params: dict = None) -> str:
    """Applies advanced transition effects between multiple video clips.
    
    Args:
        video_paths: List of paths to video files to join with transitions
        output_video_path: Path to save the final video with transitions
        transition_type: Type of transition. Options:
            - 'slide': Slide transition in specified direction
            - 'wipe': Wipe effect in specified direction  
            - 'zoom': Zoom in/out transition
            - 'circle': Circular reveal/conceal
            - 'polygon': Polygonal transition effect
            - 'spin': Spinning transition
            - 'cube': 3D cube rotation effect
            - 'page_turn': Page turning effect
            - 'ripple': Ripple distortion transition
            - 'pixelize': Pixelization transition
        transition_duration: Duration of each transition in seconds
        direction: Direction for directional transitions ('left', 'right', 'up', 'down')
        custom_params: Optional dictionary for transition-specific parameters
    
    Returns:
        A status message indicating success or failure.
    """
    if not video_paths or len(video_paths) < 2:
        return "Error: At least 2 video files are required for transitions"
    
    for video_path in video_paths:
        if not os.path.exists(video_path):
            return f"Error: Video file not found at {video_path}"
    
    if transition_duration <= 0:
        return "Error: Transition duration must be positive"
        
    custom_params = custom_params or {}
    
    try:
        # Define transition filter complexes
        transition_configs = {
            'slide': _get_slide_transition,
            'wipe': _get_wipe_transition,
            'zoom': _get_zoom_transition,
            'circle': _get_circle_transition,
            'polygon': _get_polygon_transition,
            'spin': _get_spin_transition,
            'cube': _get_cube_transition,
            'page_turn': _get_page_turn_transition,
            'ripple': _get_ripple_transition,
            'pixelize': _get_pixelize_transition
        }
        
        if transition_type not in transition_configs:
            available_transitions = ', '.join(transition_configs.keys())
            return f"Error: Unknown transition type '{transition_type}'. Available transitions: {available_transitions}"
        
        # Build the complex filter chain
        inputs = []
        for i, video_path in enumerate(video_paths):
            inputs.append(ffmpeg.input(video_path))
        
        # Create transition chain
        filter_complex_parts = []
        current_output = '[0:v]'
        
        for i in range(len(video_paths) - 1):
            next_input = f'[{i+1}:v]'
            transition_output = f'[v{i}]' if i < len(video_paths) - 2 else '[vout]'
            
            transition_filter = transition_configs[transition_type](
                current_output, next_input, transition_output, 
                transition_duration, direction, custom_params
            )
            filter_complex_parts.append(transition_filter)
            current_output = transition_output
        
        filter_complex = ';'.join(filter_complex_parts)
        
        # Create output with complex filter
        output = ffmpeg.output(
            *inputs,
            output_video_path,
            filter_complex=filter_complex,
            map='[vout]',
            vcodec='libx264',
            pix_fmt='yuv420p'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Advanced transition '{transition_type}' applied successfully between {len(video_paths)} videos. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error applying advanced transition: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def _get_slide_transition(input1: str, input2: str, output: str, duration: float, direction: str, params: dict) -> str:
    """Generate slide transition filter complex."""
    direction_map = {
        'left': 'slide_left',
        'right': 'slide_right', 
        'up': 'slide_up',
        'down': 'slide_down'
    }
    slide_dir = direction_map.get(direction, 'slide_right')
    
    return f"{input1}{input2}xfade=transition={slide_dir}:duration={duration}:offset=0{output}"


def _get_wipe_transition(input1: str, input2: str, output: str, duration: float, direction: str, params: dict) -> str:
    """Generate wipe transition filter complex."""
    direction_map = {
        'left': 'wipeleft',
        'right': 'wiperight',
        'up': 'wipeup', 
        'down': 'wipedown'
    }
    wipe_dir = direction_map.get(direction, 'wiperight')
    
    return f"{input1}{input2}xfade=transition={wipe_dir}:duration={duration}:offset=0{output}"


def _get_zoom_transition(input1: str, input2: str, output: str, duration: float, direction: str, params: dict) -> str:
    """Generate zoom transition filter complex."""
    zoom_type = 'zoomin' if direction in ['in', 'zoom_in'] else 'fadefast'
    return f"{input1}{input2}xfade=transition={zoom_type}:duration={duration}:offset=0{output}"


def _get_circle_transition(input1: str, input2: str, output: str, duration: float, direction: str, params: dict) -> str:
    """Generate circular transition filter complex."""
    return f"{input1}{input2}xfade=transition=circleopen:duration={duration}:offset=0{output}"


def _get_polygon_transition(input1: str, input2: str, output: str, duration: float, direction: str, params: dict) -> str:
    """Generate polygonal transition filter complex."""
    sides = params.get('sides', 6)
    return f"{input1}{input2}xfade=transition=hexagonalize:duration={duration}:offset=0{output}"


def _get_spin_transition(input1: str, input2: str, output: str, duration: float, direction: str, params: dict) -> str:
    """Generate spinning transition filter complex."""
    return f"{input1}{input2}xfade=transition=rotate:duration={duration}:offset=0{output}"


def _get_cube_transition(input1: str, input2: str, output: str, duration: float, direction: str, params: dict) -> str:
    """Generate 3D cube transition filter complex."""
    cube_dir = 'left' if direction == 'left' else 'right'
    return f"{input1}{input2}xfade=transition=cube{cube_dir}:duration={duration}:offset=0{output}"


def _get_page_turn_transition(input1: str, input2: str, output: str, duration: float, direction: str, params: dict) -> str:
    """Generate page turn transition filter complex."""
    return f"{input1}{input2}xfade=transition=pageturn:duration={duration}:offset=0{output}"


def _get_ripple_transition(input1: str, input2: str, output: str, duration: float, direction: str, params: dict) -> str:
    """Generate ripple transition filter complex."""
    return f"{input1}{input2}xfade=transition=ripple:duration={duration}:offset=0{output}"


def _get_pixelize_transition(input1: str, input2: str, output: str, duration: float, direction: str, params: dict) -> str:
    """Generate pixelize transition filter complex."""
    return f"{input1}{input2}xfade=transition=pixelize:duration={duration}:offset=0{output}"