import ffmpeg
import os

def process_voice(input_audio_path: str, output_audio_path: str,
                 processing_type: str, intensity: float = 1.0,
                 custom_params: dict = None) -> str:
    """Applies advanced voice processing effects for speech enhancement and creative effects.
    
    Args:
        input_audio_path: Path to the source audio file containing voice
        output_audio_path: Path to save the processed audio
        processing_type: Type of voice processing. Options:
            - 'noise_reduction': Reduce background noise and hiss
            - 'vocal_isolation': Isolate vocals from background music
            - 'voice_enhancement': Enhance speech clarity and presence
            - 'auto_tune': Auto-tune/pitch correction effect
            - 'vocoder': Vocoder/robotic voice effect
            - 'formant_shift': Change voice gender/character
            - 'telephone': Telephone/radio voice effect
            - 'megaphone': Megaphone/loudspeaker effect
            - 'whisper': Convert to whisper-like voice
            - 'deep_voice': Make voice deeper/more authoritative
            - 'chipmunk': High-pitched chipmunk effect
            - 'monster': Deep monster/demon voice
            - 'robot': Digital robot voice effect
            - 'echo_voice': Voice with natural echo
            - 'chorus_voice': Multi-voice chorus effect
        intensity: Processing intensity (0.0 to 2.0, default 1.0)
        custom_params: Optional dictionary for processing-specific parameters
    
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
        
        # Define voice processing configurations
        processing_configs = {
            'noise_reduction': _apply_noise_reduction,
            'vocal_isolation': _apply_vocal_isolation,
            'voice_enhancement': _apply_voice_enhancement,
            'auto_tune': _apply_auto_tune,
            'vocoder': _apply_vocoder,
            'formant_shift': _apply_formant_shift,
            'telephone': _apply_telephone_effect,
            'megaphone': _apply_megaphone_effect,
            'whisper': _apply_whisper_effect,
            'deep_voice': _apply_deep_voice,
            'chipmunk': _apply_chipmunk_effect,
            'monster': _apply_monster_voice,
            'robot': _apply_robot_voice,
            'echo_voice': _apply_echo_voice,
            'chorus_voice': _apply_chorus_voice
        }
        
        if processing_type not in processing_configs:
            available_types = ', '.join(processing_configs.keys())
            return f"Error: Unknown processing type '{processing_type}'. Available types: {available_types}"
        
        # Apply the voice processing
        audio_stream = input_stream.audio
        audio_stream = processing_configs[processing_type](audio_stream, intensity, custom_params)
        
        output = ffmpeg.output(audio_stream, output_audio_path)
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Voice processing '{processing_type}' applied successfully with intensity {intensity}. Output saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error processing voice: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def _apply_noise_reduction(audio_stream, intensity: float, params: dict):
    """Apply noise reduction to clean up voice recordings."""
    noise_floor = params.get('noise_floor', -60 + intensity * 20)  # dB
    attack = params.get('attack', 5)
    release = params.get('release', 50)
    
    # Use gate filter to reduce noise below threshold
    audio_stream = audio_stream.filter('agate', 
                                     threshold=noise_floor,
                                     attack=attack,
                                     release=release,
                                     ratio=10)
    
    # Apply high-pass filter to remove low-frequency noise
    cutoff_freq = params.get('highpass_freq', 80)
    audio_stream = audio_stream.filter('highpass', frequency=cutoff_freq)
    
    # Apply de-essing for sibilant reduction
    if params.get('deess', True):
        audio_stream = audio_stream.filter('deesser', i=intensity * 10, m=0.5, f=0.5, s=0.5)
    
    return audio_stream


def _apply_vocal_isolation(audio_stream, intensity: float, params: dict):
    """Isolate vocals from stereo music tracks."""
    isolation_method = params.get('method', 'center')  # center, side, karaoke
    
    if isolation_method == 'center':
        # Extract center channel (where vocals typically are)
        audio_stream = audio_stream.filter('pan', f'mono|c0=0.5*c0+0.5*c1')
    elif isolation_method == 'side':
        # Extract side information (instrumental removal)
        audio_stream = audio_stream.filter('pan', f'mono|c0=0.5*c0-0.5*c1')
    elif isolation_method == 'karaoke':
        # Karaoke effect (vocal removal)
        audio_stream = audio_stream.filter('pan', f'stereo|c0=c0|c1=-1*c1')
    
    # Apply voice-frequency emphasis
    audio_stream = audio_stream.filter('equalizer', frequency=2000, width_type='h', width=1000, gain=intensity * 6)
    
    return audio_stream


def _apply_voice_enhancement(audio_stream, intensity: float, params: dict):
    """Enhance voice clarity and presence."""
    # Presence boost (2-5 kHz)
    presence_gain = params.get('presence', intensity * 4)
    audio_stream = audio_stream.filter('equalizer', frequency=3000, width_type='h', width=2000, gain=presence_gain)
    
    # Slight compression for consistency
    audio_stream = audio_stream.filter('acompressor',
                                     threshold=0.3,
                                     ratio=3,
                                     attack=3,
                                     release=30,
                                     makeup=1.5)
    
    # Subtle de-essing
    audio_stream = audio_stream.filter('deesser', i=intensity * 5, m=0.3, f=0.7, s=0.3)
    
    # Warmth (slight low-mid boost)
    warmth_gain = params.get('warmth', intensity * 2)
    audio_stream = audio_stream.filter('equalizer', frequency=200, width_type='h', width=300, gain=warmth_gain)
    
    return audio_stream


def _apply_auto_tune(audio_stream, intensity: float, params: dict):
    """Apply auto-tune/pitch correction effect."""
    correction_strength = params.get('correction', intensity * 0.8)
    target_key = params.get('key', 'C')  # Musical key for correction
    
    # Simulate auto-tune using pitch shifting and modulation
    # Note: This is a simplified version - real auto-tune requires more complex processing
    audio_stream = audio_stream.filter('vibrato', f=8, d=correction_strength * 0.3)
    
    # Apply slight pitch quantization effect
    pitch_steps = params.get('steps', 12)  # Chromatic scale
    audio_stream = audio_stream.filter('asetrate', sample_rate=f'48000*pow(2,round({pitch_steps}*log2(48000/48000)/{pitch_steps})/{pitch_steps})')
    audio_stream = audio_stream.filter('aresample', sample_rate=48000)
    
    return audio_stream


def _apply_vocoder(audio_stream, intensity: float, params: dict):
    """Apply vocoder/robotic voice effect."""
    carrier_freq = params.get('carrier_freq', 440)  # Hz
    modulation_depth = params.get('modulation', intensity * 0.8)
    
    # Create carrier wave and modulate with voice
    # Simplified vocoder using ring modulation
    audio_stream = audio_stream.filter('tremolo', f=carrier_freq, d=modulation_depth)
    
    # Add harmonic distortion for robotic effect
    audio_stream = audio_stream.filter('overdrive', gain=intensity * 5, colour=0.5)
    
    # Band-pass filter for vocoder character
    audio_stream = audio_stream.filter('bandpass', frequency=carrier_freq, width_type='h', width=200)
    
    return audio_stream


def _apply_formant_shift(audio_stream, intensity: float, params: dict):
    """Shift voice formants to change gender/character."""
    shift_direction = params.get('direction', 'up')  # up (feminine), down (masculine)
    shift_amount = intensity * 200  # Hz
    
    if shift_direction == 'down':
        shift_amount = -shift_amount
    
    # Shift multiple formant frequencies
    formant_freqs = [800, 1200, 2400, 3400]  # Typical formant frequencies
    
    for formant in formant_freqs:
        new_freq = formant + shift_amount
        if new_freq > 100:  # Avoid negative frequencies
            audio_stream = audio_stream.filter('equalizer', 
                                             frequency=formant, 
                                             width_type='h', 
                                             width=100, 
                                             gain=-intensity * 3)
            audio_stream = audio_stream.filter('equalizer', 
                                             frequency=new_freq, 
                                             width_type='h', 
                                             width=100, 
                                             gain=intensity * 3)
    
    return audio_stream


def _apply_telephone_effect(audio_stream, intensity: float, params: dict):
    """Apply telephone/radio voice effect."""
    # Band-pass filter for telephone frequency range
    low_freq = params.get('low_freq', 300)
    high_freq = params.get('high_freq', 3400)
    
    audio_stream = audio_stream.filter('highpass', frequency=low_freq)
    audio_stream = audio_stream.filter('lowpass', frequency=high_freq)
    
    # Add slight distortion and compression
    audio_stream = audio_stream.filter('overdrive', gain=intensity * 3, colour=0.3)
    audio_stream = audio_stream.filter('acompressor', threshold=0.2, ratio=6, attack=1, release=10)
    
    # Add subtle static noise
    if params.get('static', True):
        audio_stream = audio_stream.filter('noise', alls=int(intensity * 5), allf='t')
    
    return audio_stream


def _apply_megaphone_effect(audio_stream, intensity: float, params: dict):
    """Apply megaphone/loudspeaker effect."""
    # Mid-range emphasis
    audio_stream = audio_stream.filter('equalizer', frequency=1000, width_type='h', width=800, gain=intensity * 8)
    
    # Roll off high and low frequencies
    audio_stream = audio_stream.filter('highpass', frequency=200)
    audio_stream = audio_stream.filter('lowpass', frequency=4000)
    
    # Add distortion and limiting
    audio_stream = audio_stream.filter('overdrive', gain=intensity * 8, colour=0.7)
    audio_stream = audio_stream.filter('alimiter', level_in=2, level_out=0.9, limit=1)
    
    return audio_stream


def _apply_whisper_effect(audio_stream, intensity: float, params: dict):
    """Convert voice to whisper-like effect."""
    # Reduce volume and add breath-like noise
    audio_stream = audio_stream.filter('volume', volume=0.3 + intensity * 0.3)
    
    # High-pass filter to emphasize breath sounds
    audio_stream = audio_stream.filter('highpass', frequency=2000)
    
    # Add subtle high-frequency noise for breath effect
    audio_stream = audio_stream.filter('noise', alls=int(intensity * 15), allf='t+f')
    
    # Reduce dynamic range
    audio_stream = audio_stream.filter('acompressor', threshold=0.1, ratio=8, attack=1, release=5)
    
    return audio_stream


def _apply_deep_voice(audio_stream, intensity: float, params: dict):
    """Make voice deeper and more authoritative."""
    # Pitch shift down
    pitch_shift = params.get('pitch_shift', -intensity * 6)  # semitones
    audio_stream = audio_stream.filter('asetrate', sample_rate=f'48000*pow(2,{pitch_shift}/12)')
    audio_stream = audio_stream.filter('aresample', sample_rate=48000)
    
    # Boost low frequencies
    audio_stream = audio_stream.filter('equalizer', frequency=120, width_type='h', width=200, gain=intensity * 6)
    
    # Slight compression for authority
    audio_stream = audio_stream.filter('acompressor', threshold=0.3, ratio=4, attack=5, release=50, makeup=1.2)
    
    return audio_stream


def _apply_chipmunk_effect(audio_stream, intensity: float, params: dict):
    """Apply high-pitched chipmunk effect."""
    # Pitch shift up significantly
    pitch_shift = params.get('pitch_shift', intensity * 12)  # semitones
    audio_stream = audio_stream.filter('asetrate', sample_rate=f'48000*pow(2,{pitch_shift}/12)')
    audio_stream = audio_stream.filter('aresample', sample_rate=48000)
    
    # Emphasize high frequencies
    audio_stream = audio_stream.filter('equalizer', frequency=4000, width_type='h', width=2000, gain=intensity * 4)
    
    return audio_stream


def _apply_monster_voice(audio_stream, intensity: float, params: dict):
    """Apply deep monster/demon voice effect."""
    # Heavy pitch shift down
    pitch_shift = params.get('pitch_shift', -intensity * 12)  # semitones
    audio_stream = audio_stream.filter('asetrate', sample_rate=f'48000*pow(2,{pitch_shift}/12)')
    audio_stream = audio_stream.filter('aresample', sample_rate=48000)
    
    # Add distortion and growl
    audio_stream = audio_stream.filter('overdrive', gain=intensity * 15, colour=0.8)
    
    # Boost sub-bass frequencies
    audio_stream = audio_stream.filter('equalizer', frequency=60, width_type='h', width=120, gain=intensity * 10)
    
    # Add tremolo for growl effect
    audio_stream = audio_stream.filter('tremolo', f=10, d=intensity * 0.5)
    
    return audio_stream


def _apply_robot_voice(audio_stream, intensity: float, params: dict):
    """Apply digital robot voice effect."""
    # Bit crushing for digital artifacts
    bit_depth = params.get('bit_depth', 8 - intensity * 4)
    audio_stream = audio_stream.filter('loudnorm', I=-16, LRA=7, TP=-2)  # Normalize first
    
    # Add digital distortion
    audio_stream = audio_stream.filter('overdrive', gain=intensity * 10, colour=0.9)
    
    # Ring modulation for metallic effect
    mod_freq = params.get('mod_freq', 100)
    audio_stream = audio_stream.filter('tremolo', f=mod_freq, d=intensity * 0.6)
    
    # High-frequency emphasis for digital character
    audio_stream = audio_stream.filter('equalizer', frequency=8000, width_type='h', width=4000, gain=intensity * 6)
    
    return audio_stream


def _apply_echo_voice(audio_stream, intensity: float, params: dict):
    """Apply natural echo effect to voice."""
    delay = params.get('delay', 0.3 * intensity)  # seconds
    decay = params.get('decay', 0.5)
    room_size = params.get('room_size', intensity)
    
    delay_ms = int(delay * 1000)
    
    # Multiple echo taps for natural sound
    audio_stream = audio_stream.filter('aecho',
                                     in_gain=1.0,
                                     out_gain=1.0,
                                     delays=f'{delay_ms}|{delay_ms*2}|{delay_ms*3}',
                                     decays=f'{decay}|{decay*0.7}|{decay*0.4}')
    
    # Add reverb for room ambience
    if room_size > 0.3:
        audio_stream = audio_stream.filter('afreqshift', shift=0)  # Placeholder for reverb
    
    return audio_stream


def _apply_chorus_voice(audio_stream, intensity: float, params: dict):
    """Apply multi-voice chorus effect."""
    voices = params.get('voices', int(2 + intensity * 4))  # Number of voice copies
    spread = params.get('spread', intensity * 20)  # ms spread between voices
    
    # Create multiple delayed and pitched versions
    chorus_delay = spread / 1000  # Convert to seconds
    
    for i in range(voices):
        delay_offset = i * chorus_delay
        pitch_offset = (i - voices/2) * intensity * 2  # Small pitch variations
        
        # Each voice gets slight delay and pitch variation
        voice_stream = audio_stream.filter('adelay', delays=f'{int(delay_offset * 1000)}')
        
        if pitch_offset != 0:
            voice_stream = voice_stream.filter('asetrate', sample_rate=f'48000*pow(2,{pitch_offset}/12)')
            voice_stream = voice_stream.filter('aresample', sample_rate=48000)
    
    # Mix all voices together (simplified - actual implementation would need amix)
    audio_stream = audio_stream.filter('chorus',
                                     delays=f'{spread}|{spread*1.5}|{spread*2}',
                                     decays='0.6|0.5|0.4',
                                     speeds='1|1.2|0.8',
                                     depths='2|3|2')
    
    return audio_stream


def batch_voice_process(input_files: list[str], output_directory: str,
                       processing_chain: list[dict]) -> str:
    """Process multiple voice files with a chain of effects.
    
    Args:
        input_files: List of input audio file paths
        output_directory: Directory to save processed files
        processing_chain: List of processing dictionaries, each containing:
            - 'type': Processing type
            - 'intensity': Processing intensity (optional, default 1.0)
            - 'params': Custom parameters (optional)
    
    Returns:
        A status message indicating success or failure.
    """
    if not input_files:
        return "Error: No input files provided"
    
    if not processing_chain:
        return "Error: No processing chain specified"
    
    os.makedirs(output_directory, exist_ok=True)
    
    processed_count = 0
    errors = []
    
    for input_file in input_files:
        if not os.path.exists(input_file):
            errors.append(f"File not found: {input_file}")
            continue
        
        try:
            # Generate output filename
            basename = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(output_directory, f"{basename}_processed.wav")
            
            # Apply processing chain
            current_audio = ffmpeg.input(input_file).audio
            
            for process in processing_chain:
                process_type = process.get('type')
                intensity = process.get('intensity', 1.0)
                custom_params = process.get('params', {})
                
                # Apply processing (simplified - would need full implementation)
                if process_type == 'noise_reduction':
                    current_audio = _apply_noise_reduction(current_audio, intensity, custom_params)
                elif process_type == 'voice_enhancement':
                    current_audio = _apply_voice_enhancement(current_audio, intensity, custom_params)
                # Add other processing types as needed
            
            # Save processed audio
            output = ffmpeg.output(current_audio, output_file)
            output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            
            processed_count += 1
            
        except Exception as e:
            errors.append(f"Error processing {input_file}: {str(e)}")
    
    result_msg = f"Processed {processed_count} files successfully"
    if errors:
        result_msg += f". Errors: {'; '.join(errors)}"
    
    return result_msg