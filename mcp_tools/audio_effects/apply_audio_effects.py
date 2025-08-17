import ffmpeg
import os

def apply_audio_effects(input_audio_path: str, output_audio_path: str,
                       effect_type: str, intensity: float = 1.0,
                       custom_params: dict = None) -> str:
    """Applies various audio effects to enhance or stylize audio content.
    
    Args:
        input_audio_path: Path to the source audio file
        output_audio_path: Path to save the processed audio
        effect_type: Type of audio effect. Options:
            - 'reverb': Reverb/echo effect for spaciousness
            - 'echo': Echo effect with delay
            - 'chorus': Chorus effect for richness
            - 'distortion': Distortion/overdrive effect
            - 'pitch_shift': Pitch shifting (higher/lower)
            - 'flanger': Flanger swooshing effect
            - 'phaser': Phaser modulation effect
            - 'tremolo': Tremolo amplitude modulation
            - 'vibrato': Vibrato frequency modulation
            - 'compressor': Dynamic range compression
            - 'limiter': Audio limiting for loudness
            - 'equalizer': Multi-band EQ adjustment
            - 'bass_boost': Bass frequency enhancement
            - 'treble_boost': Treble frequency enhancement
            - 'vintage': Vintage tape/vinyl sound
        intensity: Effect intensity (0.0 to 2.0, default 1.0)
        custom_params: Optional dictionary for effect-specific parameters
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_audio_path):
        return f"Error: Input audio file not found at {input_audio_path}"
    
    if intensity < 0.0 or intensity > 2.0:
        return "Error: Intensity must be between 0.0 and 2.0"
    
    custom_params = custom_params or {}
    
    try:
        input_stream = ffmpeg.input(input_audio_path)
        
        # Define effect configurations
        effect_configs = {
            'reverb': _create_reverb_effect,
            'echo': _create_echo_effect,
            'chorus': _create_chorus_effect,
            'distortion': _create_distortion_effect,
            'pitch_shift': _create_pitch_shift_effect,
            'flanger': _create_flanger_effect,
            'phaser': _create_phaser_effect,
            'tremolo': _create_tremolo_effect,
            'vibrato': _create_vibrato_effect,
            'compressor': _create_compressor_effect,
            'limiter': _create_limiter_effect,
            'equalizer': _create_equalizer_effect,
            'bass_boost': _create_bass_boost_effect,
            'treble_boost': _create_treble_boost_effect,
            'vintage': _create_vintage_effect
        }
        
        if effect_type not in effect_configs:
            available_effects = ', '.join(effect_configs.keys())
            return f"Error: Unknown effect type '{effect_type}'. Available effects: {available_effects}"
        
        # Apply the effect
        audio_stream = input_stream.audio
        audio_stream = effect_configs[effect_type](audio_stream, intensity, custom_params)
        
        output = ffmpeg.output(audio_stream, output_audio_path)
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Audio effect '{effect_type}' applied successfully with intensity {intensity}. Output saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error applying audio effect: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def _create_reverb_effect(audio_stream, intensity: float, params: dict):
    """Create reverb effect."""
    room_size = params.get('room_size', 0.5 + intensity * 0.3)
    damping = params.get('damping', 0.5)
    wet_level = params.get('wet_level', 0.3 * intensity)
    dry_level = params.get('dry_level', 1.0 - wet_level)
    
    return audio_stream.filter('afreqshift', shift=0).filter(
        'aecho', 
        in_gain=1.0,
        out_gain=wet_level,
        delays=f'{int(50 * room_size)}|{int(100 * room_size)}|{int(150 * room_size)}',
        decays=f'{damping}|{damping * 0.8}|{damping * 0.6}'
    )


def _create_echo_effect(audio_stream, intensity: float, params: dict):
    """Create echo effect."""
    delay = params.get('delay', 0.5 * intensity)  # in seconds
    decay = params.get('decay', 0.6)
    
    delay_ms = int(delay * 1000)
    
    return audio_stream.filter(
        'aecho',
        in_gain=1.0,
        out_gain=1.0,
        delays=f'{delay_ms}',
        decays=f'{decay * intensity}'
    )


def _create_chorus_effect(audio_stream, intensity: float, params: dict):
    """Create chorus effect."""
    delay = params.get('delay', 40 + intensity * 20)  # ms
    decay = params.get('decay', 0.5)
    speed = params.get('speed', 0.5 * intensity)
    depth = params.get('depth', 2.0 * intensity)
    
    return audio_stream.filter(
        'chorus',
        delays=f'{delay}',
        decays=f'{decay}',
        speeds=f'{speed}',
        depths=f'{depth}'
    )


def _create_distortion_effect(audio_stream, intensity: float, params: dict):
    """Create distortion effect."""
    gain = params.get('gain', 10 + intensity * 20)
    
    # Use overdrive filter for distortion
    return audio_stream.filter('volume', volume=gain).filter('alimiter', level_in=1, level_out=0.8)


def _create_pitch_shift_effect(audio_stream, intensity: float, params: dict):
    """Create pitch shifting effect."""
    # Intensity > 1.0 = higher pitch, < 1.0 = lower pitch
    shift_semitones = params.get('semitones', (intensity - 1.0) * 12)
    
    return audio_stream.filter('asetrate', sample_rate=f'48000*pow(2,{shift_semitones}/12)').filter('aresample', sample_rate=48000)


def _create_flanger_effect(audio_stream, intensity: float, params: dict):
    """Create flanger effect."""
    delay = params.get('delay', 5 + intensity * 10)
    depth = params.get('depth', 2 * intensity)
    regen = params.get('regen', 0.5 * intensity)
    width = params.get('width', 71)
    speed = params.get('speed', 0.5 * intensity)
    shape = params.get('shape', 'sin')
    phase = params.get('phase', 25)
    interp = params.get('interp', 'linear')
    
    return audio_stream.filter(
        'flanger',
        delay=delay,
        depth=depth,
        regen=regen,
        width=width,
        speed=speed,
        shape=shape,
        phase=phase,
        interp=interp
    )


def _create_phaser_effect(audio_stream, intensity: float, params: dict):
    """Create phaser effect."""
    in_gain = params.get('in_gain', 0.4)
    out_gain = params.get('out_gain', 0.74)
    delay = params.get('delay', 3.0 * intensity)
    decay = params.get('decay', 0.4)
    speed = params.get('speed', 0.5 * intensity)
    
    return audio_stream.filter(
        'aphaser',
        in_gain=in_gain,
        out_gain=out_gain,
        delay=delay,
        decay=decay,
        speed=speed
    )


def _create_tremolo_effect(audio_stream, intensity: float, params: dict):
    """Create tremolo effect."""
    frequency = params.get('frequency', 5.0 * intensity)
    depth = params.get('depth', 0.5 * intensity)
    
    return audio_stream.filter('tremolo', f=frequency, d=depth)


def _create_vibrato_effect(audio_stream, intensity: float, params: dict):
    """Create vibrato effect."""
    frequency = params.get('frequency', 5.0 * intensity)
    depth = params.get('depth', 0.5 * intensity)
    
    return audio_stream.filter('vibrato', f=frequency, d=depth)


def _create_compressor_effect(audio_stream, intensity: float, params: dict):
    """Create compressor effect."""
    threshold = params.get('threshold', 0.125)
    ratio = params.get('ratio', 2 + intensity * 6)  # 2:1 to 8:1
    attack = params.get('attack', 3)
    release = params.get('release', 80)
    makeup = params.get('makeup', 2)
    
    return audio_stream.filter(
        'acompressor',
        threshold=threshold,
        ratio=ratio,
        attack=attack,
        release=release,
        makeup=makeup
    )


def _create_limiter_effect(audio_stream, intensity: float, params: dict):
    """Create limiter effect."""
    level_in = params.get('level_in', 1)
    level_out = params.get('level_out', 0.8 + intensity * 0.15)
    limit = params.get('limit', 1)
    attack = params.get('attack', 5)
    release = params.get('release', 50)
    
    return audio_stream.filter(
        'alimiter',
        level_in=level_in,
        level_out=level_out,
        limit=limit,
        attack=attack,
        release=release
    )


def _create_equalizer_effect(audio_stream, intensity: float, params: dict):
    """Create equalizer effect."""
    # Default EQ curve, can be customized via params
    bass_gain = params.get('bass', intensity * 5)      # 60Hz
    mid_gain = params.get('mids', 0)                   # 1kHz  
    treble_gain = params.get('treble', intensity * 3)  # 10kHz
    
    # Apply multiple band filters
    audio_with_eq = audio_stream
    
    if bass_gain != 0:
        audio_with_eq = audio_with_eq.filter('equalizer', frequency=60, width_type='h', width=200, gain=bass_gain)
    
    if mid_gain != 0:
        audio_with_eq = audio_with_eq.filter('equalizer', frequency=1000, width_type='h', width=500, gain=mid_gain)
    
    if treble_gain != 0:
        audio_with_eq = audio_with_eq.filter('equalizer', frequency=10000, width_type='h', width=2000, gain=treble_gain)
    
    return audio_with_eq


def _create_bass_boost_effect(audio_stream, intensity: float, params: dict):
    """Create bass boost effect."""
    frequency = params.get('frequency', 80)
    gain = params.get('gain', intensity * 8)
    width = params.get('width', 100)
    
    return audio_stream.filter('equalizer', frequency=frequency, width_type='h', width=width, gain=gain)


def _create_treble_boost_effect(audio_stream, intensity: float, params: dict):
    """Create treble boost effect."""
    frequency = params.get('frequency', 8000)
    gain = params.get('gain', intensity * 6)
    width = params.get('width', 2000)
    
    return audio_stream.filter('equalizer', frequency=frequency, width_type='h', width=width, gain=gain)


def _create_vintage_effect(audio_stream, intensity: float, params: dict):
    """Create vintage tape/vinyl sound effect."""
    # Combine multiple effects for vintage sound
    warmth = params.get('warmth', intensity * 0.3)
    saturation = params.get('saturation', intensity * 0.2)
    hiss_level = params.get('hiss', intensity * 0.1)
    
    # Apply warmth (slight bass boost + treble roll-off)
    vintage_audio = audio_stream.filter('equalizer', frequency=100, width_type='h', width=100, gain=warmth * 10)
    vintage_audio = vintage_audio.filter('equalizer', frequency=8000, width_type='h', width=2000, gain=-warmth * 5)
    
    # Add subtle saturation/compression
    vintage_audio = vintage_audio.filter('acompressor', threshold=0.3, ratio=3, attack=5, release=50, makeup=1)
    
    # Add tape hiss simulation (very subtle high-frequency noise)
    if hiss_level > 0:
        vintage_audio = vintage_audio.filter('highpass', frequency=5000).filter('volume', volume=hiss_level)
    
    return vintage_audio


def create_audio_chain(input_audio_path: str, output_audio_path: str,
                      effects_chain: list[dict]) -> str:
    """Applies a chain of multiple audio effects in sequence.
    
    Args:
        input_audio_path: Path to the source audio file
        output_audio_path: Path to save the processed audio
        effects_chain: List of effect dictionaries, each containing:
            - 'type': Effect type
            - 'intensity': Effect intensity (optional, default 1.0)
            - 'params': Custom parameters (optional)
    
    Returns:
        A status message indicating success or failure.
    """
    if not effects_chain:
        return "Error: No effects specified in chain"
    
    if not os.path.exists(input_audio_path):
        return f"Error: Input audio file not found at {input_audio_path}"
    
    try:
        input_stream = ffmpeg.input(input_audio_path)
        audio_stream = input_stream.audio
        
        # Apply effects in sequence
        for i, effect in enumerate(effects_chain):
            effect_type = effect.get('type')
            intensity = effect.get('intensity', 1.0)
            custom_params = effect.get('params', {})
            
            if not effect_type:
                return f"Error: Effect type not specified for effect {i+1}"
            
            # Get effect function
            effect_configs = {
                'reverb': _create_reverb_effect,
                'echo': _create_echo_effect,
                'chorus': _create_chorus_effect,
                'distortion': _create_distortion_effect,
                'pitch_shift': _create_pitch_shift_effect,
                'flanger': _create_flanger_effect,
                'phaser': _create_phaser_effect,
                'tremolo': _create_tremolo_effect,
                'vibrato': _create_vibrato_effect,
                'compressor': _create_compressor_effect,
                'limiter': _create_limiter_effect,
                'equalizer': _create_equalizer_effect,
                'bass_boost': _create_bass_boost_effect,
                'treble_boost': _create_treble_boost_effect,
                'vintage': _create_vintage_effect
            }
            
            if effect_type not in effect_configs:
                return f"Error: Unknown effect type '{effect_type}' in chain position {i+1}"
            
            # Apply effect
            audio_stream = effect_configs[effect_type](audio_stream, intensity, custom_params)
        
        output = ffmpeg.output(audio_stream, output_audio_path)
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        effects_summary = ', '.join([f"{e['type']}({e.get('intensity', 1.0)})" for e in effects_chain])
        return f"Audio effects chain applied successfully: {effects_summary}. Output saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error applying audio effects chain: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"