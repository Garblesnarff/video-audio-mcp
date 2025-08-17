
import ffmpeg
import os
import re

def remove_silence(media_path: str, output_media_path: str, 
                   silence_threshold_db: float = -30.0, 
                   min_silence_duration_ms: int = 500) -> str:
    """Removes silent segments from an audio or video file.

    Args:
        media_path: Path to the input audio or video file.
        output_media_path: Path to save the media file with silences removed.
        silence_threshold_db: The noise level (in dBFS) below which is considered silence (e.g., -30.0).
        min_silence_duration_ms: Minimum duration (in milliseconds) of silence to be removed (e.g., 500).
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(media_path):
        return f"Error: Input media file not found at {media_path}"
    if min_silence_duration_ms <= 0:
        return "Error: Minimum silence duration must be positive."

    min_silence_duration_s = min_silence_duration_ms / 1000.0

    try:
        # Step 1: Detect silence using silencedetect filter
        # The output of silencedetect is written to stderr
        silence_detection_process = (
            ffmpeg
            .input(media_path)
            .filter('silencedetect', n=f'{silence_threshold_db}dB', d=min_silence_duration_s)
            .output('-', format='null') # Output to null as we only need stderr
            .run_async(pipe_stderr=True)
        )
        _, stderr_bytes = silence_detection_process.communicate()
        stderr_str = stderr_bytes.decode('utf8')

        # Step 2: Parse silencedetect output from stderr
        silence_starts = [float(x) for x in re.findall(r"silence_start: (\d+\.?\d*)", stderr_str)]
        silence_ends = [float(x) for x in re.findall(r"silence_end: (\d+\.?\d*)", stderr_str)]
        # silencedetect might also output silence_duration, but start/end are more direct for segmenting

        if not silence_starts: # No silences detected, or only one long silence which means the file might be entirely silent or entirely loud
            # If the file is entirely silent, ffmpeg might not produce silence_start/end, or it might be one large segment.
            # A robust way to check if any sound exists might be needed if this is problematic.
            # For now, if no silences are explicitly detected, we can assume no segments need removing.
            # Or, copy the file as is.
            # Let's try to copy the file as is, as no silences were detected for removal.
            try:
                ffmpeg.input(media_path).output(output_media_path, c='copy').run(capture_stdout=True, capture_stderr=True)
                return f"No significant silences detected (or file is entirely silent/loud). Original media copied to {output_media_path}."
            except ffmpeg.Error as e_copy:
                 return f"No significant silences detected, but error copying original file: {e_copy.stderr.decode('utf8') if e_copy.stderr else str(e_copy)}"

        # Ensure starts and ends are paired correctly. Silencedetect should output them in order.
        # If there's a mismatch, it indicates a parsing error or unexpected ffmpeg output.
        if len(silence_starts) != len(silence_ends):
            # It's possible for a file to end in silence, in which case silence_end might be missing for the last detected silence_start.
            # Or start with silence, where silence_start is 0.
            # A more robust parsing might be needed if ffmpeg output varies significantly.
            # For now, we assume they are paired from the output. If not, it's an issue.
             pass # Continue and see, this might mean it ends with silence and last end is EOF

        # Get total duration of the media for the last segment
        probe = ffmpeg.probe(media_path)
        duration_str = probe['format']['duration']
        total_duration = float(duration_str)

        # Step 3: Construct segments to keep (non-silent parts)
        sound_segments = []
        current_pos = 0.0
        for i in range(len(silence_starts)):
            start_silence = silence_starts[i]
            end_silence = silence_ends[i] if i < len(silence_ends) else total_duration

            if start_silence > current_pos: # There is sound before this silence
                sound_segments.append((current_pos, start_silence))
            current_pos = end_silence # Move current position to the end of this silence
        
        if current_pos < total_duration: # There is sound after the last silence detected
            sound_segments.append((current_pos, total_duration))
        
        if not sound_segments:
            return f"Error: No sound segments were identified to keep. The media might be entirely silent according to the thresholds, or too short."

        # Step 4: Construct select filter expressions
        video_select_filter_parts = []
        audio_select_filter_parts = []
        for start, end in sound_segments:
            video_select_filter_parts.append(f'between(t,{start},{end})')
            audio_select_filter_parts.append(f'between(t,{start},{end})')

        video_select_expr = "+".join(video_select_filter_parts)
        audio_select_expr = "+".join(audio_select_filter_parts)

        # Step 5: Apply filters and output
        input_media = ffmpeg.input(media_path)
        
        has_video = any(s['codec_type'] == 'video' for s in probe['streams'])
        has_audio = any(s['codec_type'] == 'audio' for s in probe['streams'])

        output_streams = []
        if has_video:
            processed_video = input_media.video.filter('select', video_select_expr).filter('setpts', 'PTS-STARTPTS')
            output_streams.append(processed_video)
        if has_audio:
            processed_audio = input_media.audio.filter('aselect', audio_select_expr).filter('asetpts', 'PTS-STARTPTS')
            output_streams.append(processed_audio)
        
        if not output_streams:
            return "Error: The input media does not seem to have video or audio streams."

        ffmpeg.output(*output_streams, output_media_path).run(capture_stdout=True, capture_stderr=True)
        return f"Silent segments removed. Output saved to {output_media_path}"

    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error removing silence: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred while removing silence: {str(e)}"
