import ffmpeg
import os

def create_audio_visualization(input_audio_path: str, output_video_path: str,
                             visualization_type: str, duration: float = None,
                             resolution: str = "1920x1080", fps: int = 30,
                             custom_params: dict = None) -> str:
    """Creates visual representations of audio content for music videos and presentations.
    
    Args:
        input_audio_path: Path to the source audio file
        output_video_path: Path to save the visualization video
        visualization_type: Type of visualization. Options:
            - 'spectrum': Frequency spectrum analyzer
            - 'waveform': Audio waveform display
            - 'oscilloscope': Oscilloscope-style visualization
            - 'bars': Frequency bars (equalizer style)
            - 'circle': Circular frequency visualization
            - 'particles': Particle-based audio reactive animation
            - 'tunnel': 3D tunnel effect reactive to audio
            - 'mandala': Mandala pattern visualization
            - 'plasma': Plasma effect synchronized to audio
            - 'matrix': Matrix rain effect with audio reactivity
        duration: Duration of visualization (None for full audio duration)
        resolution: Output video resolution (e.g., "1920x1080", "1280x720")
        fps: Output video frame rate
        custom_params: Optional dictionary for visualization-specific parameters
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_audio_path):
        return f"Error: Input audio file not found at {input_audio_path}"
    
    custom_params = custom_params or {}
    
    try:
        # Get audio duration if not specified
        if duration is None:
            probe = ffmpeg.probe(input_audio_path)
            duration = float(probe['format']['duration'])
        
        # Parse resolution
        width, height = map(int, resolution.split('x'))
        
        # Define visualization configurations
        viz_configs = {
            'spectrum': _create_spectrum_viz,
            'waveform': _create_waveform_viz,
            'oscilloscope': _create_oscilloscope_viz,
            'bars': _create_bars_viz,
            'circle': _create_circle_viz,
            'particles': _create_particles_viz,
            'tunnel': _create_tunnel_viz,
            'mandala': _create_mandala_viz,
            'plasma': _create_plasma_viz,
            'matrix': _create_matrix_viz
        }
        
        if visualization_type not in viz_configs:
            available_viz = ', '.join(viz_configs.keys())
            return f"Error: Unknown visualization type '{visualization_type}'. Available types: {available_viz}"
        
        # Load audio input
        audio_input = ffmpeg.input(input_audio_path)
        
        # Create visualization filter complex
        filter_complex = viz_configs[visualization_type](
            audio_input, width, height, fps, duration, custom_params
        )
        
        # Create output
        output = ffmpeg.output(
            audio_input,
            output_video_path,
            filter_complex=filter_complex,
            vcodec='libx264',
            pix_fmt='yuv420p',
            r=fps,
            t=duration
        ).global_args('-map', '[vout]', '-map', '0:a')
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Audio visualization '{visualization_type}' created successfully. Resolution: {resolution}, Duration: {duration}s. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating audio visualization: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def _create_spectrum_viz(audio_input, width: int, height: int, fps: int, duration: float, params: dict) -> str:
    """Create frequency spectrum visualization."""
    color = params.get('color', 'cyan')
    scale = params.get('scale', 'log')  # log, lin, sqrt
    
    return f'''
    [0:a]showfreqs=size={width}x{height}:mode=bar:colors={color}:scale={scale}[vout]
    '''


def _create_waveform_viz(audio_input, width: int, height: int, fps: int, duration: float, params: dict) -> str:
    """Create waveform visualization."""
    color = params.get('color', 'white')
    mode = params.get('mode', 'line')  # line, bar, dot
    scale = params.get('scale', 'lin')
    
    return f'''
    [0:a]showwaves=size={width}x{height}:mode={mode}:colors={color}:scale={scale}[vout]
    '''


def _create_oscilloscope_viz(audio_input, width: int, height: int, fps: int, duration: float, params: dict) -> str:
    """Create oscilloscope-style visualization."""
    color = params.get('color', 'green')
    zoom = params.get('zoom', 1.0)
    
    return f'''
    [0:a]showwaves=size={width}x{height}:mode=line:colors={color}:scale=lin,
    scale={width*zoom}:{height*zoom},crop={width}:{height}:(iw-ow)/2:(ih-oh)/2[vout]
    '''


def _create_bars_viz(audio_input, width: int, height: int, fps: int, duration: float, params: dict) -> str:
    """Create equalizer-style frequency bars."""
    color_scheme = params.get('colors', 'red|orange|yellow|green|blue|purple')
    
    return f'''
    [0:a]showfreqs=size={width}x{height}:mode=bar:colors={color_scheme}:scale=log[vout]
    '''


def _create_circle_viz(audio_input, width: int, height: int, fps: int, duration: float, params: dict) -> str:
    """Create circular frequency visualization."""
    color = params.get('color', 'rainbow')
    
    # Create circular spectrum using polar coordinates
    return f'''
    [0:a]showfreqs=size={width}x{height}:mode=bar:colors={color}:scale=log,
    geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':
    enable='between(t,0,{duration})'[vout]
    '''


def _create_particles_viz(audio_input, width: int, height: int, fps: int, duration: float, params: dict) -> str:
    """Create particle-based audio reactive visualization."""
    particle_count = params.get('particles', 1000)
    color = params.get('color', 'white')
    
    # Simulate particles using noise and audio reactivity
    return f'''
    [0:a]showvolume=f=1:b=4:w=20:h=20:fade=0.95:c={color}[vol];
    color=black:size={width}x{height}:rate={fps}[bg];
    [bg]noise=alls={particle_count}:allf=t,
    colorkey=color=black:similarity=0.3:blend=0.1[particles];
    [particles][vol]overlay=W-w-10:10[vout]
    '''


def _create_tunnel_viz(audio_input, width: int, height: int, fps: int, duration: float, params: dict) -> str:
    """Create 3D tunnel effect reactive to audio."""
    tunnel_speed = params.get('speed', 1.0)
    color_shift = params.get('color_shift', True)
    
    tunnel_rotation = f'(t*{tunnel_speed}*2*PI)'
    
    filter_complex = f'''
    color=black:size={width}x{height}:rate={fps}[bg];
    [bg]geq=
    r='128+127*sin(hypot(X-W/2,Y-H/2)/20+{tunnel_rotation})':
    g='128+127*sin(hypot(X-W/2,Y-H/2)/20+{tunnel_rotation}+2*PI/3)':
    b='128+127*sin(hypot(X-W/2,Y-H/2)/20+{tunnel_rotation}+4*PI/3)':
    enable='between(t,0,{duration})'[tunnel];
    [0:a]showvolume=f=1:b=4:w=100:h=20:fade=0.9[vol];
    [tunnel][vol]overlay=(W-w)/2:H-h-20[vout]
    '''
    
    return filter_complex


def _create_mandala_viz(audio_input, width: int, height: int, fps: int, duration: float, params: dict) -> str:
    """Create mandala pattern visualization."""
    symmetry = params.get('symmetry', 8)
    rotation_speed = params.get('rotation', 0.5)
    
    return f'''
    [0:a]showfreqs=size={width//4}x{height//4}:mode=bar:colors=rainbow:scale=log[freq];
    [freq]scale={width}:{height},
    rotate='t*{rotation_speed}*2*PI':ow={width}:oh={height}:c=black[mandala];
    [mandala]geq=
    r='r(W/2+(X-W/2)*cos({symmetry}*atan2(Y-H/2,X-W/2))-(Y-H/2)*sin({symmetry}*atan2(Y-H/2,X-W/2)),H/2+(X-W/2)*sin({symmetry}*atan2(Y-H/2,X-W/2))+(Y-H/2)*cos({symmetry}*atan2(Y-H/2,X-W/2)))':
    g='g(W/2+(X-W/2)*cos({symmetry}*atan2(Y-H/2,X-W/2))-(Y-H/2)*sin({symmetry}*atan2(Y-H/2,X-W/2)),H/2+(X-W/2)*sin({symmetry}*atan2(Y-H/2,X-W/2))+(Y-H/2)*cos({symmetry}*atan2(Y-H/2,X-W/2)))':
    b='b(W/2+(X-W/2)*cos({symmetry}*atan2(Y-H/2,X-W/2))-(Y-H/2)*sin({symmetry}*atan2(Y-H/2,X-W/2)),H/2+(X-W/2)*sin({symmetry}*atan2(Y-H/2,X-W/2))+(Y-H/2)*cos({symmetry}*atan2(Y-H/2,X-W/2)))'[vout]
    '''


def _create_plasma_viz(audio_input, width: int, height: int, fps: int, duration: float, params: dict) -> str:
    """Create plasma effect synchronized to audio."""
    plasma_speed = params.get('speed', 1.0)
    color_intensity = params.get('intensity', 1.0)
    
    return f'''
    color=black:size={width}x{height}:rate={fps}[bg];
    [bg]geq=
    r='128+127*{color_intensity}*sin(X/20+t*{plasma_speed})*sin(Y/20+t*{plasma_speed})':
    g='128+127*{color_intensity}*sin((X+Y)/20+t*{plasma_speed}*1.5)':
    b='128+127*{color_intensity}*sin(sqrt((X-W/2)*(X-W/2)+(Y-H/2)*(Y-H/2))/20+t*{plasma_speed}*2)':
    enable='between(t,0,{duration})'[plasma];
    [0:a]showvolume=f=1:b=4:w=200:h=20:fade=0.8[vol];
    [plasma][vol]overlay=(W-w)/2:20[vout]
    '''


def _create_matrix_viz(audio_input, width: int, height: int, fps: int, duration: float, params: dict) -> str:
    """Create Matrix rain effect with audio reactivity."""
    rain_density = params.get('density', 0.1)
    fall_speed = params.get('speed', 2.0)
    
    return f'''
    color=black:size={width}x{height}:rate={fps}[bg];
    [bg]drawtext=text='0123456789ABCDEF':fontsize=20:fontcolor=green:
    x='mod(t*{fall_speed}*50,W)':y='mod(t*{fall_speed}*100,H)':
    enable='between(t,0,{duration})'[matrix];
    [0:a]showwaves=size={width}x100:mode=line:colors=green:scale=lin[waves];
    [matrix][waves]overlay=0:H-h[vout]
    '''


def create_lyric_visualization(audio_path: str, lyrics_file: str, output_video_path: str,
                             background_type: str = "spectrum", font_size: int = 48,
                             font_color: str = "white") -> str:
    """Creates a lyric video with audio visualization background.
    
    Args:
        audio_path: Path to the audio file
        lyrics_file: Path to lyrics file (SRT format or plain text)
        output_video_path: Path to save the lyric video
        background_type: Type of background visualization ('spectrum', 'waveform', 'particles')
        font_size: Size of lyric text
        font_color: Color of lyric text
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(audio_path):
        return f"Error: Audio file not found at {audio_path}"
    
    if not os.path.exists(lyrics_file):
        return f"Error: Lyrics file not found at {lyrics_file}"
    
    try:
        # Get audio duration
        probe = ffmpeg.probe(audio_path)
        duration = float(probe['format']['duration'])
        
        audio_input = ffmpeg.input(audio_path)
        
        # Create background visualization
        if background_type == "spectrum":
            bg_filter = "[0:a]showfreqs=size=1920x1080:mode=bar:colors=rainbow:scale=log[bg]"
        elif background_type == "waveform":
            bg_filter = "[0:a]showwaves=size=1920x1080:mode=line:colors=cyan:scale=lin[bg]"
        else:  # particles
            bg_filter = """
            color=black:size=1920x1080:rate=30[base];
            [base]noise=alls=500:allf=t,colorkey=color=black:similarity=0.3:blend=0.1[bg]
            """
        
        # Add lyrics overlay
        filter_complex = f'''
        {bg_filter};
        [bg]subtitles={lyrics_file}:force_style='FontSize={font_size},PrimaryColour=&H{font_color.replace("#", "")}&'[vout]
        '''
        
        output = ffmpeg.output(
            audio_input,
            output_video_path,
            filter_complex=filter_complex,
            vcodec='libx264',
            pix_fmt='yuv420p'
        ).global_args('-map', '[vout]', '-map', '0:a')
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Lyric visualization created successfully with {background_type} background. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating lyric visualization: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def create_music_video_template(audio_path: str, image_path: str, output_video_path: str,
                               template_style: str = "modern", beat_detection: bool = True) -> str:
    """Creates a music video template with synchronized visuals.
    
    Args:
        audio_path: Path to the audio file
        image_path: Path to album artwork or background image
        output_video_path: Path to save the music video
        template_style: Style template ('modern', 'retro', 'minimal', 'energetic')
        beat_detection: Whether to sync visuals to audio beats
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(audio_path):
        return f"Error: Audio file not found at {audio_path}"
    
    if not os.path.exists(image_path):
        return f"Error: Image file not found at {image_path}"
    
    try:
        audio_input = ffmpeg.input(audio_path)
        image_input = ffmpeg.input(image_path, loop=1)
        
        # Get audio duration
        probe = ffmpeg.probe(audio_path)
        duration = float(probe['format']['duration'])
        
        # Style-specific effects
        if template_style == "modern":
            effect_filter = """
            scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,
            gblur=sigma=2,colorbalance=rs=0.1:gs=0.1:bs=-0.1[img];
            [0:a]showfreqs=size=1920x200:mode=bar:colors=cyan|blue:scale=log[freq];
            [img][freq]overlay=0:H-h:alpha=0.7[vout]
            """
        elif template_style == "retro":
            effect_filter = """
            scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,
            colorchannelmixer=rr=0.393:rg=0.769:rb=0.189:gr=0.349:gg=0.686:gb=0.168:br=0.272:bg=0.534:bb=0.131,
            noise=alls=10:allf=t[img];
            [0:a]showwaves=size=1920x100:mode=line:colors=orange:scale=lin[wave];
            [img][wave]overlay=0:H-h[vout]
            """
        elif template_style == "minimal":
            effect_filter = """
            scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,
            eq=contrast=1.2:brightness=0.1[img];
            [img]drawtext=text='♪':fontsize=100:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:
            alpha='0.5+0.5*sin(t*2*PI)'[vout]
            """
        else:  # energetic
            effect_filter = """
            scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,
            hue=h=sin(t*2)*180:s=1.5,
            rotate='sin(t)*PI/180':ow=rotw(sin(t)*PI/180):oh=roth(sin(t)*PI/180)[img];
            [0:a]showfreqs=size=1920x1080:mode=bar:colors=red|yellow|green|cyan|blue|magenta:scale=log[freq];
            [img][freq]blend=all_mode=overlay:all_opacity=0.5[vout]
            """
        
        output = ffmpeg.output(
            image_input,
            audio_input,
            output_video_path,
            filter_complex=f'[0:v]{effect_filter}',
            vcodec='libx264',
            pix_fmt='yuv420p',
            t=duration
        ).global_args('-map', '[vout]', '-map', '1:a')
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Music video template '{template_style}' created successfully. Duration: {duration}s. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating music video template: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"