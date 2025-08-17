import ffmpeg
import os

def mix_audio_tracks(audio_sources: list[dict], output_audio_path: str,
                    master_volume: float = 1.0, fade_in: float = 0.0,
                    fade_out: float = 0.0, normalize: bool = True) -> str:
    """Mixes multiple audio tracks together with individual controls.
    
    Args:
        audio_sources: List of audio source dictionaries, each containing:
            - 'path': Path to audio file
            - 'volume': Volume level (0.0 to 2.0, default 1.0)
            - 'start_time': Start time in output (seconds, default 0.0)
            - 'duration': Duration to include (seconds, None for full duration)
            - 'pan': Stereo panning (-1.0 left to 1.0 right, 0.0 center)
            - 'fade_in': Fade in duration (seconds, default 0.0)
            - 'fade_out': Fade out duration (seconds, default 0.0)
            - 'loop': Whether to loop the track (bool, default False)
        output_audio_path: Path to save the mixed audio
        master_volume: Overall output volume (0.0 to 2.0)
        fade_in: Master fade in duration (seconds)
        fade_out: Master fade out duration (seconds)
        normalize: Whether to normalize the final output
    
    Returns:
        A status message indicating success or failure.
    """
    if not audio_sources:
        return "Error: No audio sources provided"
    
    # Validate all source files exist
    for i, source in enumerate(audio_sources):
        if 'path' not in source:
            return f"Error: No path specified for audio source {i+1}"
        if not os.path.exists(source['path']):
            return f"Error: Audio file not found at {source['path']}"
    
    try:
        # Process each audio source
        processed_streams = []
        
        for i, source in enumerate(audio_sources):
            input_stream = ffmpeg.input(source['path'])
            audio_stream = input_stream.audio
            
            # Apply individual track settings
            volume = source.get('volume', 1.0)
            start_time = source.get('start_time', 0.0)
            duration = source.get('duration')
            pan = source.get('pan', 0.0)
            track_fade_in = source.get('fade_in', 0.0)
            track_fade_out = source.get('fade_out', 0.0)
            loop_track = source.get('loop', False)
            
            # Apply looping if specified
            if loop_track and duration:
                audio_stream = audio_stream.filter('aloop', loop=-1, size=int(duration * 48000))
            
            # Apply volume adjustment
            if volume != 1.0:
                audio_stream = audio_stream.filter('volume', volume=volume)
            
            # Apply panning
            if pan != 0.0:
                # Convert pan value to left/right channel gains
                left_gain = 1.0 - max(0, pan)
                right_gain = 1.0 + min(0, pan)
                audio_stream = audio_stream.filter('pan', f'stereo|c0={left_gain}*c0|c1={right_gain}*c1')
            
            # Apply track-specific fade in/out
            if track_fade_in > 0:
                audio_stream = audio_stream.filter('afade', type='in', duration=track_fade_in)
            if track_fade_out > 0:
                audio_stream = audio_stream.filter('afade', type='out', duration=track_fade_out)
            
            # Add delay for start time
            if start_time > 0:
                audio_stream = audio_stream.filter('adelay', delays=f'{int(start_time * 1000)}')
            
            processed_streams.append(audio_stream)
        
        # Mix all streams together
        if len(processed_streams) == 1:
            mixed_audio = processed_streams[0]
        else:
            # Use amix filter for multiple streams
            mixed_audio = ffmpeg.filter(processed_streams, 'amix', inputs=len(processed_streams), weights=' '.join(['1'] * len(processed_streams)))
        
        # Apply master volume
        if master_volume != 1.0:
            mixed_audio = mixed_audio.filter('volume', volume=master_volume)
        
        # Apply master fade in/out
        if fade_in > 0:
            mixed_audio = mixed_audio.filter('afade', type='in', duration=fade_in)
        if fade_out > 0:
            mixed_audio = mixed_audio.filter('afade', type='out', duration=fade_out)
        
        # Apply normalization if requested
        if normalize:
            mixed_audio = mixed_audio.filter('dynaudnorm')
        
        # Output the mixed audio
        output = ffmpeg.output(mixed_audio, output_audio_path)
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Mixed {len(audio_sources)} audio tracks successfully. Master volume: {master_volume}. Output saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error mixing audio tracks: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def create_audio_bed(background_music_path: str, vocal_tracks: list[str],
                    output_audio_path: str, music_volume: float = 0.3,
                    vocal_volume: float = 1.0, ducking_enabled: bool = True,
                    ducking_threshold: float = -20.0) -> str:
    """Creates an audio bed by mixing background music with vocal tracks and applying ducking.
    
    Args:
        background_music_path: Path to background music file
        vocal_tracks: List of paths to vocal/speech audio files
        output_audio_path: Path to save the mixed audio bed
        music_volume: Volume of background music (0.0 to 1.0)
        vocal_volume: Volume of vocal tracks (0.0 to 2.0)
        ducking_enabled: Whether to duck (lower) music when vocals are present
        ducking_threshold: Audio level threshold for ducking (dB)
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(background_music_path):
        return f"Error: Background music file not found at {background_music_path}"
    
    for vocal_path in vocal_tracks:
        if not os.path.exists(vocal_path):
            return f"Error: Vocal track not found at {vocal_path}"
    
    try:
        # Load background music
        bg_music = ffmpeg.input(background_music_path).audio
        
        # Set background music volume
        bg_music = bg_music.filter('volume', volume=music_volume)
        
        # Mix vocal tracks if multiple
        if len(vocal_tracks) == 1:
            vocals = ffmpeg.input(vocal_tracks[0]).audio
        else:
            vocal_streams = [ffmpeg.input(path).audio for path in vocal_tracks]
            vocals = ffmpeg.filter(vocal_streams, 'amix', inputs=len(vocal_streams))
        
        # Apply vocal volume
        vocals = vocals.filter('volume', volume=vocal_volume)
        
        # Apply ducking if enabled
        if ducking_enabled:
            # Use sidechaincompress to duck music when vocals are present
            mixed_audio = ffmpeg.filter([bg_music, vocals], 'sidechaincompress',
                                      threshold=ducking_threshold,
                                      ratio=4,
                                      attack=5,
                                      release=50,
                                      makeup=2)
        else:
            # Simple mix without ducking
            mixed_audio = ffmpeg.filter([bg_music, vocals], 'amix', inputs=2)
        
        # Output the audio bed
        output = ffmpeg.output(mixed_audio, output_audio_path)
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        ducking_status = "with ducking" if ducking_enabled else "without ducking"
        return f"Audio bed created successfully {ducking_status}. Background: {music_volume}, Vocals: {vocal_volume}. Output saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating audio bed: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def create_stereo_mix(left_audio_path: str, right_audio_path: str,
                     output_audio_path: str, balance: float = 0.0,
                     crossfeed: float = 0.0) -> str:
    """Creates a stereo mix from separate left and right audio channels.
    
    Args:
        left_audio_path: Path to left channel audio
        right_audio_path: Path to right channel audio
        output_audio_path: Path to save the stereo mix
        balance: Stereo balance (-1.0 = left only, 1.0 = right only, 0.0 = center)
        crossfeed: Amount of crossfeed between channels (0.0 to 1.0)
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(left_audio_path):
        return f"Error: Left audio file not found at {left_audio_path}"
    
    if not os.path.exists(right_audio_path):
        return f"Error: Right audio file not found at {right_audio_path}"
    
    try:
        left_audio = ffmpeg.input(left_audio_path).audio
        right_audio = ffmpeg.input(right_audio_path).audio
        
        # Apply crossfeed if specified
        if crossfeed > 0:
            # Mix some of right into left and vice versa
            left_with_crossfeed = ffmpeg.filter([left_audio, right_audio], 'amix', 
                                              inputs=2, 
                                              weights=f'1 {crossfeed}')
            right_with_crossfeed = ffmpeg.filter([right_audio, left_audio], 'amix', 
                                               inputs=2, 
                                               weights=f'1 {crossfeed}')
            left_audio = left_with_crossfeed
            right_audio = right_with_crossfeed
        
        # Apply balance
        if balance != 0:
            left_gain = 1.0 - max(0, balance)
            right_gain = 1.0 + min(0, balance)
            left_audio = left_audio.filter('volume', volume=left_gain)
            right_audio = right_audio.filter('volume', volume=right_gain)
        
        # Merge into stereo
        stereo_mix = ffmpeg.filter([left_audio, right_audio], 'amerge', inputs=2)
        
        output = ffmpeg.output(stereo_mix, output_audio_path, ac=2)
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Stereo mix created successfully. Balance: {balance}, Crossfeed: {crossfeed}. Output saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating stereo mix: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def create_surround_mix(audio_sources: dict, output_audio_path: str,
                       format: str = "5.1") -> str:
    """Creates a surround sound mix from multiple audio sources.
    
    Args:
        audio_sources: Dictionary mapping channels to audio file paths:
            - 'front_left': Path to front left channel
            - 'front_right': Path to front right channel
            - 'center': Path to center channel
            - 'lfe': Path to LFE/subwoofer channel
            - 'rear_left': Path to rear left channel (5.1/7.1)
            - 'rear_right': Path to rear right channel (5.1/7.1)
            - 'side_left': Path to side left channel (7.1 only)
            - 'side_right': Path to side right channel (7.1 only)
        output_audio_path: Path to save the surround mix
        format: Surround format ('5.1' or '7.1')
    
    Returns:
        A status message indicating success or failure.
    """
    required_channels = {
        '5.1': ['front_left', 'front_right', 'center', 'lfe', 'rear_left', 'rear_right'],
        '7.1': ['front_left', 'front_right', 'center', 'lfe', 'rear_left', 'rear_right', 'side_left', 'side_right']
    }
    
    if format not in required_channels:
        return f"Error: Unsupported surround format '{format}'. Supported: 5.1, 7.1"
    
    # Check if all required channels are provided
    missing_channels = []
    for channel in required_channels[format]:
        if channel not in audio_sources:
            missing_channels.append(channel)
        elif not os.path.exists(audio_sources[channel]):
            return f"Error: Audio file not found for {channel} channel at {audio_sources[channel]}"
    
    if missing_channels:
        return f"Error: Missing audio sources for channels: {', '.join(missing_channels)}"
    
    try:
        # Load all channel inputs
        channel_streams = []
        for channel in required_channels[format]:
            audio_stream = ffmpeg.input(audio_sources[channel]).audio
            channel_streams.append(audio_stream)
        
        # Merge into multi-channel audio
        if format == '5.1':
            surround_mix = ffmpeg.filter(channel_streams, 'amerge', inputs=6)
            channel_layout = '5.1'
        else:  # 7.1
            surround_mix = ffmpeg.filter(channel_streams, 'amerge', inputs=8)
            channel_layout = '7.1'
        
        # Set proper channel layout
        surround_mix = surround_mix.filter('aformat', channel_layouts=channel_layout)
        
        output = ffmpeg.output(surround_mix, output_audio_path)
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Surround sound mix ({format}) created successfully with {len(channel_streams)} channels. Output saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating surround mix: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def mix_with_timeline(timeline_config: dict, output_audio_path: str) -> str:
    """Creates an audio mix based on a timeline configuration with precise timing.
    
    Args:
        timeline_config: Dictionary containing:
            - 'duration': Total timeline duration in seconds
            - 'tracks': List of track dictionaries, each containing:
                - 'audio_path': Path to audio file
                - 'start': Start time on timeline (seconds)
                - 'end': End time on timeline (seconds)
                - 'volume': Track volume (0.0 to 2.0)
                - 'fade_in': Fade in duration (seconds, optional)
                - 'fade_out': Fade out duration (seconds, optional)
        output_audio_path: Path to save the timeline mix
    
    Returns:
        A status message indicating success or failure.
    """
    if 'duration' not in timeline_config or 'tracks' not in timeline_config:
        return "Error: Timeline config must contain 'duration' and 'tracks'"
    
    total_duration = timeline_config['duration']
    tracks = timeline_config['tracks']
    
    if not tracks:
        return "Error: No tracks specified in timeline"
    
    try:
        # Create silence base track for the full duration
        base_silence = ffmpeg.input(f'anullsrc=channel_layout=stereo:sample_rate=48000', f='lavfi', t=total_duration).audio
        
        # Process each track according to timeline
        processed_tracks = [base_silence]
        
        for i, track in enumerate(tracks):
            if 'audio_path' not in track or 'start' not in track or 'end' not in track:
                return f"Error: Track {i+1} missing required fields (audio_path, start, end)"
            
            if not os.path.exists(track['audio_path']):
                return f"Error: Audio file not found for track {i+1} at {track['audio_path']}"
            
            audio_path = track['audio_path']
            start_time = track['start']
            end_time = track['end']
            volume = track.get('volume', 1.0)
            fade_in = track.get('fade_in', 0.0)
            fade_out = track.get('fade_out', 0.0)
            
            # Load and trim audio
            track_duration = end_time - start_time
            audio_stream = ffmpeg.input(audio_path, ss=0, t=track_duration).audio
            
            # Apply volume
            if volume != 1.0:
                audio_stream = audio_stream.filter('volume', volume=volume)
            
            # Apply fades
            if fade_in > 0:
                audio_stream = audio_stream.filter('afade', type='in', duration=fade_in)
            if fade_out > 0:
                audio_stream = audio_stream.filter('afade', type='out', duration=fade_out)
            
            # Add delay to position on timeline
            if start_time > 0:
                audio_stream = audio_stream.filter('adelay', delays=f'{int(start_time * 1000)}')
            
            processed_tracks.append(audio_stream)
        
        # Mix all tracks together
        mixed_audio = ffmpeg.filter(processed_tracks, 'amix', inputs=len(processed_tracks))
        
        output = ffmpeg.output(mixed_audio, output_audio_path)
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Timeline audio mix created successfully with {len(tracks)} tracks over {total_duration}s. Output saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating timeline mix: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"