import ffmpeg
import os
import tempfile

def apply_video_morphing(input_videos: list[str], output_video_path: str,
                        morph_type: str = "smooth", morph_duration: float = 2.0,
                        easing: str = "linear", custom_params: dict = None) -> str:
    """Applies smooth morphing transitions between multiple video clips.
    
    Args:
        input_videos: List of video file paths to morph between
        output_video_path: Path to save the morphed video
        morph_type: Type of morphing effect. Options:
            - 'smooth': Smooth blending between clips
            - 'warp': Geometric warping transition
            - 'liquid': Liquid-like flowing transition
            - 'spiral': Spiral morphing effect
            - 'zoom_morph': Zoom-based morphing
            - 'twist': Twisting transition
            - 'stretch': Stretching/squashing morph
            - 'ripple_morph': Ripple-based morphing
        morph_duration: Duration of each morph transition in seconds
        easing: Easing function ('linear', 'ease_in', 'ease_out', 'ease_in_out')
        custom_params: Optional dictionary for morph-specific parameters
    
    Returns:
        A status message indicating success or failure.
    """
    if not input_videos or len(input_videos) < 2:
        return "Error: At least 2 video files are required for morphing"
    
    for video_path in input_videos:
        if not os.path.exists(video_path):
            return f"Error: Video file not found at {video_path}"
    
    if morph_duration <= 0:
        return "Error: Morph duration must be positive"
    
    custom_params = custom_params or {}
    
    try:
        # Define morphing configurations
        morph_configs = {
            'smooth': _create_smooth_morph,
            'warp': _create_warp_morph,
            'liquid': _create_liquid_morph,
            'spiral': _create_spiral_morph,
            'zoom_morph': _create_zoom_morph,
            'twist': _create_twist_morph,
            'stretch': _create_stretch_morph,
            'ripple_morph': _create_ripple_morph
        }
        
        if morph_type not in morph_configs:
            available_morphs = ', '.join(morph_configs.keys())
            return f"Error: Unknown morph type '{morph_type}'. Available morphs: {available_morphs}"
        
        # Load input videos
        inputs = []
        for video_path in input_videos:
            inputs.append(ffmpeg.input(video_path))
        
        # Generate morph filter complex
        filter_complex_parts = []
        current_output = '[0:v]'
        
        for i in range(len(input_videos) - 1):
            next_input = f'[{i+1}:v]'
            transition_output = f'[v{i}]' if i < len(input_videos) - 2 else '[vout]'
            
            morph_filter = morph_configs[morph_type](
                current_output, next_input, transition_output,
                morph_duration, easing, custom_params
            )
            filter_complex_parts.append(morph_filter)
            current_output = transition_output
        
        filter_complex = ';'.join(filter_complex_parts)
        
        # Create output
        output = ffmpeg.output(
            *inputs,
            output_video_path,
            filter_complex=filter_complex,
            map='[vout]',
            vcodec='libx264',
            pix_fmt='yuv420p'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Video morphing '{morph_type}' applied successfully between {len(input_videos)} videos. Duration: {morph_duration}s each. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error applying video morphing: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def _create_smooth_morph(input1: str, input2: str, output: str, duration: float, easing: str, params: dict) -> str:
    """Create smooth morphing transition."""
    alpha_curve = _get_easing_curve(easing, duration)
    return f"{input1}{input2}blend=all_mode=normal:all_opacity='{alpha_curve}':enable='between(t,0,{duration})'{output}"


def _create_warp_morph(input1: str, input2: str, output: str, duration: float, easing: str, params: dict) -> str:
    """Create geometric warping morph transition."""
    warp_strength = params.get('warp_strength', 0.5)
    
    # Create warping effect using perspective filter
    perspective_expr = f"x/(W+{warp_strength}*W*sin(t*2*PI/{duration})):y/(H+{warp_strength}*H*cos(t*2*PI/{duration}))"
    
    return f"""
    {input1}perspective=interpolation=linear:
    x0='0':y0='0':x1='W':y1='0':x2='W':y2='H':x3='0':y3='H':
    enable='between(t,0,{duration/2})'[warped1];
    {input2}perspective=interpolation=linear:
    x0='0':y0='0':x1='W':y1='0':x2='W':y2='H':x3='0':y3='H':
    enable='between(t,{duration/2},{duration})'[warped2];
    [warped1][warped2]blend=all_mode=normal:all_opacity='if(lt(t,{duration/2}),1-t/{duration/2},t/{duration/2}-0.5)'{output}
    """


def _create_liquid_morph(input1: str, input2: str, output: str, duration: float, easing: str, params: dict) -> str:
    """Create liquid-like flowing morph transition."""
    flow_speed = params.get('flow_speed', 1.0)
    viscosity = params.get('viscosity', 0.5)
    
    # Simulate liquid flow using displacement mapping
    return f"""
    {input1}format=rgba,geq=
    r='r(X+10*sin(T*{flow_speed}),Y+10*cos(T*{flow_speed}))':
    g='g(X+10*sin(T*{flow_speed}),Y+10*cos(T*{flow_speed}))':
    b='b(X+10*sin(T*{flow_speed}),Y+10*cos(T*{flow_speed}))':
    a='a(X,Y)*(1-T/{duration})':
    enable='between(t,0,{duration})'[liquid1];
    {input2}format=rgba,geq=
    r='r(X-10*sin(T*{flow_speed}),Y-10*cos(T*{flow_speed}))':
    g='g(X-10*sin(T*{flow_speed}),Y-10*cos(T*{flow_speed}))':
    b='b(X-10*sin(T*{flow_speed}),Y-10*cos(T*{flow_speed}))':
    a='a(X,Y)*(T/{duration})':
    enable='between(t,0,{duration})'[liquid2];
    [liquid1][liquid2]overlay{output}
    """


def _create_spiral_morph(input1: str, input2: str, output: str, duration: float, easing: str, params: dict) -> str:
    """Create spiral morphing effect."""
    spiral_speed = params.get('spiral_speed', 2.0)
    spiral_tightness = params.get('tightness', 1.0)
    
    return f"""
    {input1}rotate='t*{spiral_speed}*2*PI/{duration}':ow=rotw(t*{spiral_speed}*2*PI/{duration}):oh=roth(t*{spiral_speed}*2*PI/{duration}):
    enable='between(t,0,{duration})'[spiral1];
    {input2}rotate='-t*{spiral_speed}*2*PI/{duration}':ow=rotw(-t*{spiral_speed}*2*PI/{duration}):oh=roth(-t*{spiral_speed}*2*PI/{duration}):
    enable='between(t,0,{duration})'[spiral2];
    [spiral1][spiral2]blend=all_mode=normal:all_opacity='t/{duration}'{output}
    """


def _create_zoom_morph(input1: str, input2: str, output: str, duration: float, easing: str, params: dict) -> str:
    """Create zoom-based morphing transition."""
    zoom_factor = params.get('zoom_factor', 2.0)
    zoom_center_x = params.get('center_x', 0.5)
    zoom_center_y = params.get('center_y', 0.5)
    
    # Zoom out first video while zooming in second
    scale_out = f"1+{zoom_factor}*t/{duration}"
    scale_in = f"{zoom_factor}-{zoom_factor}*t/{duration}"
    
    return f"""
    {input1}scale=iw*{scale_out}:ih*{scale_out},
    crop=iw:ih:(iw-ow)/2:(ih-oh)/2:
    enable='between(t,0,{duration})'[zoom_out];
    {input2}scale=iw*{scale_in}:ih*{scale_in},
    crop=iw:ih:(iw-ow)/2:(ih-oh)/2:
    enable='between(t,0,{duration})'[zoom_in];
    [zoom_out][zoom_in]blend=all_mode=normal:all_opacity='t/{duration}'{output}
    """


def _create_twist_morph(input1: str, input2: str, output: str, duration: float, easing: str, params: dict) -> str:
    """Create twisting morph transition."""
    twist_angle = params.get('twist_angle', 360)
    twist_radius = params.get('radius', 0.5)
    
    # Apply twisting distortion
    twist_expr = f"(t/{duration})*{twist_angle}*PI/180"
    
    return f"""
    {input1}geq=
    r='r(X+{twist_radius}*W*cos({twist_expr}),Y+{twist_radius}*H*sin({twist_expr}))':
    g='g(X+{twist_radius}*W*cos({twist_expr}),Y+{twist_radius}*H*sin({twist_expr}))':
    b='b(X+{twist_radius}*W*cos({twist_expr}),Y+{twist_radius}*H*sin({twist_expr}))':
    enable='between(t,0,{duration})'[twisted1];
    {input2}geq=
    r='r(X-{twist_radius}*W*cos({twist_expr}),Y-{twist_radius}*H*sin({twist_expr}))':
    g='g(X-{twist_radius}*W*cos({twist_expr}),Y-{twist_radius}*H*sin({twist_expr}))':
    b='b(X-{twist_radius}*W*cos({twist_expr}),Y-{twist_radius}*H*sin({twist_expr}))':
    enable='between(t,0,{duration})'[twisted2];
    [twisted1][twisted2]blend=all_mode=normal:all_opacity='t/{duration}'{output}
    """


def _create_stretch_morph(input1: str, input2: str, output: str, duration: float, easing: str, params: dict) -> str:
    """Create stretching/squashing morph transition."""
    stretch_factor = params.get('stretch_factor', 2.0)
    direction = params.get('direction', 'horizontal')  # horizontal, vertical, both
    
    if direction == 'horizontal':
        scale_expr1 = f"1+{stretch_factor}*sin(t*PI/{duration}):1"
        scale_expr2 = f"1+{stretch_factor}*cos(t*PI/{duration}):1"
    elif direction == 'vertical':
        scale_expr1 = f"1:1+{stretch_factor}*sin(t*PI/{duration})"
        scale_expr2 = f"1:1+{stretch_factor}*cos(t*PI/{duration})"
    else:  # both
        scale_expr1 = f"1+{stretch_factor}*sin(t*PI/{duration}):1+{stretch_factor}*cos(t*PI/{duration})"
        scale_expr2 = f"1+{stretch_factor}*cos(t*PI/{duration}):1+{stretch_factor}*sin(t*PI/{duration})"
    
    return f"""
    {input1}scale={scale_expr1}:
    enable='between(t,0,{duration})'[stretched1];
    {input2}scale={scale_expr2}:
    enable='between(t,0,{duration})'[stretched2];
    [stretched1][stretched2]blend=all_mode=normal:all_opacity='t/{duration}'{output}
    """


def _create_ripple_morph(input1: str, input2: str, output: str, duration: float, easing: str, params: dict) -> str:
    """Create ripple-based morphing transition."""
    ripple_frequency = params.get('frequency', 5.0)
    ripple_amplitude = params.get('amplitude', 20.0)
    ripple_speed = params.get('speed', 2.0)
    
    # Create ripple distortion effect
    ripple_x = f"X+{ripple_amplitude}*sin((X+Y)*{ripple_frequency}/100+t*{ripple_speed})"
    ripple_y = f"Y+{ripple_amplitude}*cos((X+Y)*{ripple_frequency}/100+t*{ripple_speed})"
    
    return f"""
    {input1}geq=r='r({ripple_x},{ripple_y})':g='g({ripple_x},{ripple_y})':b='b({ripple_x},{ripple_y})':
    enable='between(t,0,{duration})'[rippled1];
    {input2}geq=r='r({ripple_x},{ripple_y})':g='g({ripple_x},{ripple_y})':b='b({ripple_x},{ripple_y})':
    enable='between(t,0,{duration})'[rippled2];
    [rippled1][rippled2]blend=all_mode=normal:all_opacity='t/{duration}'{output}
    """


def _get_easing_curve(easing: str, duration: float) -> str:
    """Generate easing curve expression for smooth transitions."""
    t_norm = f"t/{duration}"
    
    easing_curves = {
        'linear': t_norm,
        'ease_in': f"pow({t_norm}, 2)",
        'ease_out': f"1-pow(1-{t_norm}, 2)",
        'ease_in_out': f"if(lt({t_norm}, 0.5), 2*pow({t_norm}, 2), 1-2*pow(1-{t_norm}, 2))",
        'bounce': f"{t_norm}*(2-{t_norm})"
    }
    
    return easing_curves.get(easing, t_norm)


def create_shape_morph(input_video_path: str, output_video_path: str,
                      shape_sequence: list[str], morph_duration: float = 2.0,
                      shape_color: str = "white", background_color: str = "black") -> str:
    """Creates animated shape morphing overlay on video.
    
    Args:
        input_video_path: Path to the source video
        output_video_path: Path to save the video with shape morphing
        shape_sequence: List of shapes to morph between ('circle', 'square', 'triangle', 'star', 'heart')
        morph_duration: Duration of each shape morph in seconds
        shape_color: Color of the morphing shapes
        background_color: Background color for shapes
    
    Returns:
        A status message indicating success or failure.
    """
    if not shape_sequence or len(shape_sequence) < 2:
        return "Error: At least 2 shapes are required for shape morphing"
    
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        
        # Create shape sequence with morphing
        shape_filters = []
        total_duration = len(shape_sequence) * morph_duration
        
        for i, shape in enumerate(shape_sequence):
            start_time = i * morph_duration
            end_time = (i + 1) * morph_duration
            
            shape_filter = _create_shape_overlay(shape, start_time, end_time, shape_color, background_color)
            shape_filters.append(shape_filter)
        
        # Combine all shape overlays
        filter_complex = f"[0:v]{';'.join(shape_filters)}[vout]"
        
        output = ffmpeg.output(
            input_stream,
            output_video_path,
            filter_complex=filter_complex,
            vcodec='libx264',
            acodec='copy'
        ).global_args('-map', '[vout]', '-map', '0:a?')
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Shape morphing created successfully with {len(shape_sequence)} shapes. Total duration: {total_duration}s. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating shape morph: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def _create_shape_overlay(shape: str, start_time: float, end_time: float, color: str, bg_color: str) -> str:
    """Create overlay filter for a specific shape."""
    duration = end_time - start_time
    
    shape_configs = {
        'circle': f"drawbox=x=(w-100)/2:y=(h-100)/2:w=100:h=100:color={color}:thickness=fill",
        'square': f"drawbox=x=(w-100)/2:y=(h-100)/2:w=100:h=100:color={color}:thickness=fill",
        'triangle': f"drawtext=text='▲':fontsize=100:fontcolor={color}:x=(w-text_w)/2:y=(h-text_h)/2",
        'star': f"drawtext=text='★':fontsize=100:fontcolor={color}:x=(w-text_w)/2:y=(h-text_h)/2",
        'heart': f"drawtext=text='♥':fontsize=100:fontcolor={color}:x=(w-text_w)/2:y=(h-text_h)/2"
    }
    
    shape_filter = shape_configs.get(shape, shape_configs['circle'])
    
    return f"{shape_filter}:enable='between(t,{start_time},{end_time})'"