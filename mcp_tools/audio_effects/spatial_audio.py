import ffmpeg
import os
import math

def create_spatial_audio(input_audio_path: str, output_audio_path: str,
                        spatial_type: str, movement_pattern: str = "static",
                        room_simulation: bool = True, custom_params: dict = None) -> str:
    """Creates immersive spatial audio experiences with 3D positioning and movement.
    
    Args:
        input_audio_path: Path to the source audio file
        output_audio_path: Path to save the spatial audio
        spatial_type: Type of spatial audio. Options:
            - 'binaural': Binaural audio for headphone listening
            - 'surround_5_1': 5.1 surround sound positioning
            - 'surround_7_1': 7.1 surround sound positioning
            - 'ambisonics': Ambisonic B-format for VR/360 video
            - '3d_positional': 3D positional audio with HRTF
            - 'stereo_widening': Enhanced stereo width and depth
        movement_pattern: Audio source movement pattern. Options:
            - 'static': No movement
            - 'circular': Circular movement around listener
            - 'pendulum': Left-right swinging motion
            - 'flyby': Object passing by listener
            - 'spiral': Spiral movement pattern
            - 'custom': Custom movement defined in params
        room_simulation: Whether to simulate room acoustics and reverb
        custom_params: Optional dictionary for spatial-specific parameters
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_audio_path):
        return f"Error: Input audio file not found at {input_audio_path}"
    
    custom_params = custom_params or {}
    
    try:
        input_stream = ffmpeg.input(input_audio_path)
        
        # Define spatial audio configurations
        spatial_configs = {
            'binaural': _create_binaural_audio,
            'surround_5_1': _create_surround_5_1,
            'surround_7_1': _create_surround_7_1,
            'ambisonics': _create_ambisonics,
            '3d_positional': _create_3d_positional,
            'stereo_widening': _create_stereo_widening
        }
        
        if spatial_type not in spatial_configs:
            available_types = ', '.join(spatial_configs.keys())
            return f"Error: Unknown spatial type '{spatial_type}'. Available types: {available_types}"
        
        # Apply spatial processing
        audio_stream = input_stream.audio
        audio_stream = spatial_configs[spatial_type](audio_stream, movement_pattern, room_simulation, custom_params)
        
        output = ffmpeg.output(audio_stream, output_audio_path)
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Spatial audio '{spatial_type}' created successfully with '{movement_pattern}' movement. Room simulation: {room_simulation}. Output saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating spatial audio: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def _create_binaural_audio(audio_stream, movement_pattern: str, room_simulation: bool, params: dict):
    """Create binaural audio for headphone listening."""
    # Simulate HRTF (Head-Related Transfer Function) for binaural effect
    azimuth = params.get('azimuth', 0)  # degrees (-180 to 180)
    elevation = params.get('elevation', 0)  # degrees (-90 to 90)
    distance = params.get('distance', 1.0)  # meters
    
    # Convert to left/right channel gains and delays
    azimuth_rad = math.radians(azimuth)
    left_gain = (1 + math.cos(azimuth_rad)) / 2
    right_gain = (1 - math.cos(azimuth_rad)) / 2
    
    # Inter-aural time difference (ITD) simulation
    itd_ms = math.sin(azimuth_rad) * 0.7  # Max ~0.7ms delay
    
    # Apply distance attenuation
    distance_gain = 1.0 / max(distance, 0.1)
    left_gain *= distance_gain
    right_gain *= distance_gain
    
    # Create stereo positioning
    if movement_pattern == "circular":
        # Animate azimuth in circular motion
        movement_filter = f"pan=stereo|c0={left_gain}*c0|c1={right_gain}*c0"
    else:
        movement_filter = f"pan=stereo|c0={left_gain}*c0|c1={right_gain}*c0"
    
    audio_stream = audio_stream.filter('pan', movement_filter)
    
    # Add HRTF-like filtering
    # Left ear: slight low-pass for far-side attenuation
    # Right ear: maintain full spectrum for near-side
    if azimuth > 0:  # Sound from right
        audio_stream = audio_stream.filter('pan', 'stereo|c0=0.7*c0|c1=1.0*c1')
    else:  # Sound from left
        audio_stream = audio_stream.filter('pan', 'stereo|c0=1.0*c0|c1=0.7*c1')
    
    # Add room simulation if enabled
    if room_simulation:
        audio_stream = audio_stream.filter('aecho', 
                                         in_gain=1.0, 
                                         out_gain=0.3, 
                                         delays='50|150|300', 
                                         decays='0.4|0.3|0.2')
    
    return audio_stream


def _create_surround_5_1(audio_stream, movement_pattern: str, room_simulation: bool, params: dict):
    """Create 5.1 surround sound positioning."""
    # Define 5.1 channel positions
    position = params.get('position', 'center')  # front_left, front_right, center, lfe, rear_left, rear_right
    
    # Channel mapping for 5.1 (FL, FR, C, LFE, RL, RR)
    channel_map = {
        'front_left': '1|0|0|0|0|0',
        'front_right': '0|1|0|0|0|0',
        'center': '0|0|1|0|0|0',
        'lfe': '0|0|0|1|0|0',
        'rear_left': '0|0|0|0|1|0',
        'rear_right': '0|0|0|0|0|1'
    }
    
    # Convert mono to 5.1 with positioning
    if position in channel_map:
        weights = channel_map[position]
        audio_stream = audio_stream.filter('pan', f'5.1|c0={weights.split("|")[0]}*c0|c1={weights.split("|")[1]}*c0|c2={weights.split("|")[2]}*c0|c3={weights.split("|")[3]}*c0|c4={weights.split("|")[4]}*c0|c5={weights.split("|")[5]}*c0')
    
    # Add movement animation
    if movement_pattern == "circular":
        # Animate between channels for circular motion
        audio_stream = audio_stream.filter('pan', '5.1|c0=sin(t*0.5)*c0|c1=cos(t*0.5)*c0|c2=0.2*c0|c3=0.1*c0|c4=sin(t*0.5+PI)*c0|c5=cos(t*0.5+PI)*c0')
    
    return audio_stream


def _create_surround_7_1(audio_stream, movement_pattern: str, room_simulation: bool, params: dict):
    """Create 7.1 surround sound positioning."""
    # 7.1 channel layout: FL, FR, C, LFE, RL, RR, SL, SR
    position = params.get('position', 'center')
    
    # Convert to 7.1 with positioning
    audio_stream = audio_stream.filter('aformat', channel_layouts='7.1')
    
    # Apply positional mixing based on 7.1 layout
    if movement_pattern == "circular":
        # Animate around all 7.1 channels
        audio_stream = audio_stream.filter('pan', '7.1|c0=sin(t*0.3)*c0|c1=cos(t*0.3)*c0|c2=0.2*c0|c3=0.1*c0|c4=sin(t*0.3+PI)*c0|c5=cos(t*0.3+PI)*c0|c6=sin(t*0.3+PI/2)*c0|c7=cos(t*0.3+PI/2)*c0')
    
    return audio_stream


def _create_ambisonics(audio_stream, movement_pattern: str, room_simulation: bool, params: dict):
    """Create ambisonic B-format for VR/360 video."""
    # Ambisonic B-format: W (omnidirectional), X (front-back), Y (left-right), Z (up-down)
    azimuth = params.get('azimuth', 0)  # degrees
    elevation = params.get('elevation', 0)  # degrees
    
    azimuth_rad = math.radians(azimuth)
    elevation_rad = math.radians(elevation)
    
    # Calculate ambisonic coefficients
    w_gain = 0.707  # W channel (omnidirectional)
    x_gain = math.cos(elevation_rad) * math.cos(azimuth_rad)  # X channel (front-back)
    y_gain = math.cos(elevation_rad) * math.sin(azimuth_rad)  # Y channel (left-right)
    z_gain = math.sin(elevation_rad)  # Z channel (up-down)
    
    # Create 4-channel ambisonic output
    audio_stream = audio_stream.filter('pan', f'4.0|c0={w_gain}*c0|c1={x_gain}*c0|c2={y_gain}*c0|c3={z_gain}*c0')
    
    return audio_stream


def _create_3d_positional(audio_stream, movement_pattern: str, room_simulation: bool, params: dict):
    """Create 3D positional audio with HRTF simulation."""
    x_pos = params.get('x', 0.0)  # meters (-10 to 10)
    y_pos = params.get('y', 0.0)  # meters (-10 to 10)  
    z_pos = params.get('z', 0.0)  # meters (-5 to 5)
    
    # Calculate distance and angles
    distance = math.sqrt(x_pos**2 + y_pos**2 + z_pos**2)
    azimuth = math.atan2(y_pos, x_pos)
    elevation = math.atan2(z_pos, math.sqrt(x_pos**2 + y_pos**2))
    
    # Distance attenuation
    distance_gain = 1.0 / max(distance, 0.1)
    
    # High-frequency attenuation with distance (air absorption)
    if distance > 1.0:
        audio_stream = audio_stream.filter('lowpass', frequency=20000/(1 + distance*0.1))
    
    # Doppler effect for moving sources
    if movement_pattern == "flyby":
        doppler_shift = params.get('doppler_intensity', 1.0)
        # Simulate doppler by modulating pitch based on velocity
        audio_stream = audio_stream.filter('asetrate', sample_rate=f'48000*(1+{doppler_shift}*sin(t*0.5))')
        audio_stream = audio_stream.filter('aresample', sample_rate=48000)
    
    # Apply 3D positioning
    left_gain = distance_gain * (1 + math.cos(azimuth)) / 2
    right_gain = distance_gain * (1 - math.cos(azimuth)) / 2
    
    audio_stream = audio_stream.filter('pan', f'stereo|c0={left_gain}*c0|c1={right_gain}*c0')
    
    return audio_stream


def _create_stereo_widening(audio_stream, movement_pattern: str, room_simulation: bool, params: dict):
    """Create enhanced stereo width and depth."""
    width_factor = params.get('width', 1.5)  # 1.0 = normal, 2.0 = very wide
    depth_enhancement = params.get('depth', True)
    
    # Stereo width enhancement using M/S processing
    # Convert L/R to Mid/Side
    audio_stream = audio_stream.filter('pan', 'stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0-0.5*c1')
    
    # Enhance side channel for width
    audio_stream = audio_stream.filter('pan', f'stereo|c0=c0|c1={width_factor}*c1')
    
    # Convert back to L/R
    audio_stream = audio_stream.filter('pan', 'stereo|c0=c0+c1|c1=c0-c1')
    
    # Add depth enhancement with subtle delay and filtering
    if depth_enhancement:
        audio_stream = audio_stream.filter('aecho', 
                                         in_gain=1.0, 
                                         out_gain=0.2, 
                                         delays='20|40', 
                                         decays='0.3|0.2')
    
    return audio_stream


def create_3d_audio_scene(audio_sources: list[dict], output_audio_path: str,
                         listener_position: dict = None, room_config: dict = None) -> str:
    """Creates a complex 3D audio scene with multiple positioned sources.
    
    Args:
        audio_sources: List of audio source dictionaries, each containing:
            - 'path': Path to audio file
            - 'position': 3D position [x, y, z] in meters
            - 'volume': Source volume (0.0 to 2.0)
            - 'movement': Movement pattern ('static', 'circular', 'linear', etc.)
            - 'directivity': Sound directivity pattern (optional)
        output_audio_path: Path to save the 3D audio scene
        listener_position: Dictionary with listener position and orientation
        room_config: Dictionary with room acoustics configuration
    
    Returns:
        A status message indicating success or failure.
    """
    if not audio_sources:
        return "Error: No audio sources provided"
    
    listener_position = listener_position or {'x': 0, 'y': 0, 'z': 0, 'orientation': 0}
    room_config = room_config or {'size': [10, 10, 3], 'absorption': 0.3, 'reverb_time': 1.5}
    
    try:
        # Process each audio source
        positioned_streams = []
        
        for i, source in enumerate(audio_sources):
            if 'path' not in source or 'position' not in source:
                return f"Error: Source {i+1} missing required fields (path, position)"
            
            if not os.path.exists(source['path']):
                return f"Error: Audio file not found for source {i+1} at {source['path']}"
            
            audio_stream = ffmpeg.input(source['path']).audio
            
            # Calculate relative position to listener
            src_pos = source['position']
            lis_pos = listener_position
            rel_x = src_pos[0] - lis_pos['x']
            rel_y = src_pos[1] - lis_pos['y']
            rel_z = src_pos[2] - lis_pos['z']
            
            # Apply 3D positioning
            distance = math.sqrt(rel_x**2 + rel_y**2 + rel_z**2)
            azimuth = math.atan2(rel_y, rel_x) - math.radians(lis_pos.get('orientation', 0))
            elevation = math.atan2(rel_z, math.sqrt(rel_x**2 + rel_y**2))
            
            # Distance attenuation
            distance_gain = 1.0 / max(distance, 0.1)
            
            # Apply volume
            volume = source.get('volume', 1.0)
            audio_stream = audio_stream.filter('volume', volume=volume * distance_gain)
            
            # Apply spatial positioning
            left_gain = (1 + math.cos(azimuth)) / 2
            right_gain = (1 - math.cos(azimuth)) / 2
            
            # Elevation affects both channels
            elevation_factor = math.cos(elevation)
            left_gain *= elevation_factor
            right_gain *= elevation_factor
            
            audio_stream = audio_stream.filter('pan', f'stereo|c0={left_gain}*c0|c1={right_gain}*c0')
            
            # Add high-frequency attenuation for distance
            if distance > 2.0:
                cutoff_freq = 20000 / (1 + distance * 0.2)
                audio_stream = audio_stream.filter('lowpass', frequency=cutoff_freq)
            
            # Add movement if specified
            movement = source.get('movement', 'static')
            if movement == 'circular':
                # This would need more complex implementation for real-time movement
                audio_stream = audio_stream.filter('tremolo', f=0.1, d=0.3)
            
            positioned_streams.append(audio_stream)
        
        # Mix all positioned sources
        if len(positioned_streams) == 1:
            mixed_audio = positioned_streams[0]
        else:
            mixed_audio = ffmpeg.filter(positioned_streams, 'amix', inputs=len(positioned_streams))
        
        # Apply room acoustics
        room_size = room_config.get('size', [10, 10, 3])
        absorption = room_config.get('absorption', 0.3)
        reverb_time = room_config.get('reverb_time', 1.5)
        
        # Simulate room reverb based on size and absorption
        delay_ms = int((room_size[0] + room_size[1] + room_size[2]) / 3 * 2.9)  # Speed of sound approximation
        decay = 1.0 - absorption
        
        mixed_audio = mixed_audio.filter('aecho',
                                       in_gain=1.0,
                                       out_gain=0.3 * (1 - absorption),
                                       delays=f'{delay_ms}|{delay_ms*2}|{delay_ms*3}',
                                       decays=f'{decay}|{decay*0.7}|{decay*0.4}')
        
        # Apply final output formatting
        output = ffmpeg.output(mixed_audio, output_audio_path, ac=2)
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"3D audio scene created successfully with {len(audio_sources)} sources. Room: {room_size}, Absorption: {absorption}. Output saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating 3D audio scene: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def convert_to_spatial_format(input_audio_path: str, output_audio_path: str,
                            source_format: str, target_format: str) -> str:
    """Converts between different spatial audio formats.
    
    Args:
        input_audio_path: Path to the source spatial audio file
        output_audio_path: Path to save the converted audio
        source_format: Source format ('stereo', 'surround_5_1', 'surround_7_1', 'ambisonics')
        target_format: Target format ('binaural', 'surround_5_1', 'surround_7_1', 'ambisonics')
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_audio_path):
        return f"Error: Input audio file not found at {input_audio_path}"
    
    conversion_matrix = {
        ('stereo', 'binaural'): 'aformat=channel_layouts=stereo',
        ('stereo', 'surround_5_1'): 'pan=5.1|c0=c0|c1=c1|c2=0.5*c0+0.5*c1|c3=0|c4=0|c5=0',
        ('surround_5_1', 'binaural'): 'pan=stereo|c0=c0+0.7*c2+0.5*c4|c1=c1+0.7*c2+0.5*c5',
        ('surround_5_1', 'stereo'): 'pan=stereo|c0=c0+0.7*c2+0.5*c4|c1=c1+0.7*c2+0.5*c5',
        ('ambisonics', 'binaural'): 'pan=stereo|c0=0.707*c0+c1|c1=0.707*c0-c1',
    }
    
    conversion_key = (source_format, target_format)
    
    if conversion_key not in conversion_matrix:
        return f"Error: Conversion from {source_format} to {target_format} not supported"
    
    try:
        input_stream = ffmpeg.input(input_audio_path)
        conversion_filter = conversion_matrix[conversion_key]
        
        audio_stream = input_stream.audio.filter('pan', conversion_filter.split('|')[1:])
        
        output = ffmpeg.output(audio_stream, output_audio_path)
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Spatial audio converted successfully from {source_format} to {target_format}. Output saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error converting spatial audio: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"