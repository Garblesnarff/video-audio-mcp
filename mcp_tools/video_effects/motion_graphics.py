import ffmpeg
import os
import math

def create_motion_graphics(input_video_path: str, output_video_path: str,
                          graphics_type: str, start_time: float = 0.0, 
                          duration: float = 5.0, custom_params: dict = None) -> str:
    """Creates animated motion graphics overlays on video content.
    
    Args:
        input_video_path: Path to the source video file (can be None for graphics-only output)
        output_video_path: Path to save the video with motion graphics
        graphics_type: Type of motion graphics. Options:
            - 'animated_text': Text with animation effects (typewriter, fade, slide, etc.)
            - 'geometric_shapes': Animated geometric shapes (circles, rectangles, lines)
            - 'particle_system': Particle effects (snow, rain, sparks, bubbles)
            - 'progress_bar': Animated progress bars and loading indicators
            - 'counter': Animated number counters and timers
            - 'waveform': Audio waveform visualization
            - 'oscilloscope': Oscilloscope-style audio visualization
            - 'spinning_logo': Spinning/rotating logo animation
            - 'sliding_panels': Animated sliding panels and overlays
            - 'burst_animation': Burst/explosion animation effects
        start_time: Start time for the graphics in seconds
        duration: Duration of the graphics animation in seconds
        custom_params: Dictionary with graphics-specific parameters
    
    Returns:
        A status message indicating success or failure.
    """
    if input_video_path and not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    custom_params = custom_params or {}
    
    try:
        # Define motion graphics configurations
        graphics_configs = {
            'animated_text': _create_animated_text,
            'geometric_shapes': _create_geometric_shapes,
            'particle_system': _create_particle_system,
            'progress_bar': _create_progress_bar,
            'counter': _create_counter,
            'waveform': _create_waveform,
            'oscilloscope': _create_oscilloscope,
            'spinning_logo': _create_spinning_logo,
            'sliding_panels': _create_sliding_panels,
            'burst_animation': _create_burst_animation
        }
        
        if graphics_type not in graphics_configs:
            available_types = ', '.join(graphics_configs.keys())
            return f"Error: Unknown graphics type '{graphics_type}'. Available types: {available_types}"
        
        # Generate the filter complex for the motion graphics
        filter_complex = graphics_configs[graphics_type](
            start_time, duration, custom_params
        )
        
        if input_video_path:
            # Overlay on existing video
            input_stream = ffmpeg.input(input_video_path)
            output = ffmpeg.output(
                input_stream,
                output_video_path,
                filter_complex=filter_complex,
                vcodec='libx264',
                acodec='copy'
            ).global_args('-map', '[vout]', '-map', '0:a?')
        else:
            # Create graphics-only video
            color_source = ffmpeg.input(
                'color=black:size=1920x1080:rate=30',
                f='lavfi',
                t=duration
            )
            output = ffmpeg.output(
                color_source,
                output_video_path,
                filter_complex=filter_complex,
                map='[vout]',
                vcodec='libx264',
                pix_fmt='yuv420p'
            )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Motion graphics '{graphics_type}' created successfully. Duration: {duration}s. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating motion graphics: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def _create_animated_text(start_time: float, duration: float, params: dict) -> str:
    """Create animated text graphics filter complex."""
    text = params.get('text', 'Sample Text')
    font_size = params.get('font_size', 48)
    font_color = params.get('font_color', 'white')
    animation = params.get('animation', 'typewriter')  # typewriter, fade_in, slide_in, bounce
    x_pos = params.get('x_pos', '(w-text_w)/2')
    y_pos = params.get('y_pos', '(h-text_h)/2')
    
    if animation == 'typewriter':
        # Typewriter effect - reveal characters one by one
        filter_complex = f'''
        [0:v]drawtext=text='{text}':fontsize={font_size}:fontcolor={font_color}:
        x={x_pos}:y={y_pos}:
        enable='between(t,{start_time},{start_time + duration})':
        textfile=<(printf "%s" "{text}" | fold -w 1 | head -n "$(echo "({math.floor(duration * 10)} * (t - {start_time}) / {duration})" | bc)")
        [vout]
        '''
    elif animation == 'fade_in':
        # Fade in effect
        alpha_expr = f'if(between(t,{start_time},{start_time + duration}),(t-{start_time})/{duration},0)'
        filter_complex = f'''
        [0:v]drawtext=text='{text}':fontsize={font_size}:fontcolor={font_color}:
        x={x_pos}:y={y_pos}:alpha='{alpha_expr}':
        enable='between(t,{start_time},{start_time + duration})'[vout]
        '''
    elif animation == 'slide_in':
        # Slide in from left
        x_expr = f'if(between(t,{start_time},{start_time + duration}),-w+(w+text_w)*(t-{start_time})/{duration},{x_pos})'
        filter_complex = f'''
        [0:v]drawtext=text='{text}':fontsize={font_size}:fontcolor={font_color}:
        x='{x_expr}':y={y_pos}:
        enable='between(t,{start_time},{start_time + duration})'[vout]
        '''
    else:  # bounce
        # Bouncing animation
        y_expr = f'{y_pos}+sin((t-{start_time})*2*PI)*20'
        filter_complex = f'''
        [0:v]drawtext=text='{text}':fontsize={font_size}:fontcolor={font_color}:
        x={x_pos}:y='{y_expr}':
        enable='between(t,{start_time},{start_time + duration})'[vout]
        '''
    
    return filter_complex


def _create_geometric_shapes(start_time: float, duration: float, params: dict) -> str:
    """Create animated geometric shapes filter complex."""
    shape_type = params.get('shape', 'circle')  # circle, rectangle, line, triangle
    color = params.get('color', 'red')
    size = params.get('size', 100)
    animation = params.get('animation', 'rotate')  # rotate, scale, translate
    
    if shape_type == 'circle':
        if animation == 'rotate':
            # Rotating circle
            x_expr = f'w/2+{size}*cos((t-{start_time})*2*PI/{duration})'
            y_expr = f'h/2+{size}*sin((t-{start_time})*2*PI/{duration})'
        else:  # scale
            x_expr = f'w/2'
            y_expr = f'h/2'
            size_expr = f'{size}*(1+0.5*sin((t-{start_time})*4*PI/{duration}))'
            
        filter_complex = f'''
        [0:v]drawbox=x={x_expr}-{size}/2:y={y_expr}-{size}/2:w={size}:h={size}:
        color={color}:thickness=fill:
        enable='between(t,{start_time},{start_time + duration})'[vout]
        '''
    
    elif shape_type == 'line':
        # Animated line
        filter_complex = f'''
        [0:v]drawbox=x=w/4:y=h/2:w='w/2*(t-{start_time})/{duration}':h=5:
        color={color}:thickness=fill:
        enable='between(t,{start_time},{start_time + duration})'[vout]
        '''
    
    return filter_complex


def _create_particle_system(start_time: float, duration: float, params: dict) -> str:
    """Create particle system effects filter complex."""
    particle_type = params.get('type', 'snow')  # snow, rain, sparks, bubbles
    density = params.get('density', 100)
    
    if particle_type == 'snow':
        # Snow effect using noise
        filter_complex = f'''
        [0:v]noise=alls={density}:allf=t+u,
        colorkey=color=black:similarity=0.3:blend=0.1:
        enable='between(t,{start_time},{start_time + duration})'[vout]
        '''
    elif particle_type == 'rain':
        # Rain effect using motion blur
        filter_complex = f'''
        [0:v]noise=alls={density}:allf=t,
        motion_blur=radius=10:angle=270:
        enable='between(t,{start_time},{start_time + duration})'[vout]
        '''
    else:  # sparks
        filter_complex = f'''
        [0:v]noise=alls={density}:allf=t,
        hue=s=2:h=sin(t)*180:
        enable='between(t,{start_time},{start_time + duration})'[vout]
        '''
    
    return filter_complex


def _create_progress_bar(start_time: float, duration: float, params: dict) -> str:
    """Create animated progress bar filter complex."""
    bar_color = params.get('color', 'green')
    bg_color = params.get('bg_color', 'gray')
    width = params.get('width', 400)
    height = params.get('height', 20)
    x_pos = params.get('x', '(w-400)/2')
    y_pos = params.get('y', 'h-100')
    
    progress_width = f'{width}*(t-{start_time})/{duration}'
    
    filter_complex = f'''
    [0:v]drawbox=x={x_pos}:y={y_pos}:w={width}:h={height}:color={bg_color}:thickness=fill,
    drawbox=x={x_pos}:y={y_pos}:w='{progress_width}':h={height}:color={bar_color}:thickness=fill:
    enable='between(t,{start_time},{start_time + duration})'[vout]
    '''
    
    return filter_complex


def _create_counter(start_time: float, duration: float, params: dict) -> str:
    """Create animated counter filter complex."""
    start_value = params.get('start', 0)
    end_value = params.get('end', 100)
    font_size = params.get('font_size', 72)
    color = params.get('color', 'white')
    x_pos = params.get('x', '(w-text_w)/2')
    y_pos = params.get('y', '(h-text_h)/2')
    
    counter_expr = f'{start_value}+({end_value}-{start_value})*(t-{start_time})/{duration}'
    
    filter_complex = f'''
    [0:v]drawtext=text='%{{eif\\:{counter_expr}\\:d}}':fontsize={font_size}:fontcolor={color}:
    x={x_pos}:y={y_pos}:
    enable='between(t,{start_time},{start_time + duration})'[vout]
    '''
    
    return filter_complex


def _create_waveform(start_time: float, duration: float, params: dict) -> str:
    """Create audio waveform visualization filter complex."""
    color = params.get('color', 'cyan')
    scale = params.get('scale', 'lin')  # lin, log, sqrt, cbrt
    
    filter_complex = f'''
    [0:a]showwaves=size=1920x200:mode=line:colors={color}:scale={scale}:
    enable='between(t,{start_time},{start_time + duration})'[waves];
    [0:v][waves]overlay=0:h-200:
    enable='between(t,{start_time},{start_time + duration})'[vout]
    '''
    
    return filter_complex


def _create_oscilloscope(start_time: float, duration: float, params: dict) -> str:
    """Create oscilloscope visualization filter complex."""
    color = params.get('color', 'green')
    
    filter_complex = f'''
    [0:a]showwaves=size=400x400:mode=line:colors={color}:scale=lin:
    enable='between(t,{start_time},{start_time + duration})'[scope];
    [0:v][scope]overlay=(W-w)/2:(H-h)/2:
    enable='between(t,{start_time},{start_time + duration})'[vout]
    '''
    
    return filter_complex


def _create_spinning_logo(start_time: float, duration: float, params: dict) -> str:
    """Create spinning logo animation filter complex."""
    logo_path = params.get('logo_path', '')
    if not logo_path:
        return "[0:v]copy[vout]"  # No logo provided
    
    rotation_speed = params.get('speed', 1.0)
    size = params.get('size', 200)
    
    rotation_expr = f'(t-{start_time})*{rotation_speed}*2*PI/{duration}'
    
    filter_complex = f'''
    movie={logo_path}[logo];
    [logo]scale={size}:{size},rotate='{rotation_expr}':fillcolor=none:ow=rotw({rotation_expr}):oh=roth({rotation_expr})[rotated_logo];
    [0:v][rotated_logo]overlay=(W-w)/2:(H-h)/2:
    enable='between(t,{start_time},{start_time + duration})'[vout]
    '''
    
    return filter_complex


def _create_sliding_panels(start_time: float, duration: float, params: dict) -> str:
    """Create sliding panels animation filter complex."""
    color = params.get('color', 'blue')
    direction = params.get('direction', 'left')  # left, right, up, down
    panel_width = params.get('width', 300)
    
    if direction == 'left':
        x_expr = f'-{panel_width}+{panel_width}*(t-{start_time})/{duration}'
        y_expr = '0'
        width = panel_width
        height = 'h'
    elif direction == 'right':
        x_expr = f'w-{panel_width}*(t-{start_time})/{duration}'
        y_expr = '0'
        width = panel_width
        height = 'h'
    
    filter_complex = f'''
    [0:v]drawbox=x='{x_expr}':y={y_expr}:w={width}:h={height}:color={color}:thickness=fill:
    enable='between(t,{start_time},{start_time + duration})'[vout]
    '''
    
    return filter_complex


def _create_burst_animation(start_time: float, duration: float, params: dict) -> str:
    """Create burst/explosion animation filter complex."""
    color = params.get('color', 'yellow')
    center_x = params.get('x', 'w/2')
    center_y = params.get('y', 'h/2')
    
    radius_expr = f'100*(t-{start_time})/{duration}'
    alpha_expr = f'1-(t-{start_time})/{duration}'
    
    filter_complex = f'''
    [0:v]drawbox=x={center_x}-'{radius_expr}':y={center_y}-'{radius_expr}':
    w='2*{radius_expr}':h='2*{radius_expr}':color={color}:thickness=10:
    enable='between(t,{start_time},{start_time + duration})'[vout]
    '''
    
    return filter_complex