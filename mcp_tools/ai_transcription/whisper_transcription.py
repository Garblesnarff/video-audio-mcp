import os
import json
import tempfile
from typing import List, Dict, Optional, Union
import ffmpeg

def transcribe_audio_whisper(audio_path: str, 
                           model_size: str = "base",
                           language: str = "auto",
                           output_format: str = "srt",
                           include_timestamps: bool = True,
                           speaker_diarization: bool = False) -> str:
    """
    Transcribe audio using OpenAI Whisper with advanced options.
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size ("tiny", "base", "small", "medium", "large", "large-v2", "large-v3", "turbo")
        language: Target language code or "auto" for detection
        output_format: Output format ("srt", "vtt", "txt", "json", "tsv")
        include_timestamps: Whether to include timestamp information
        speaker_diarization: Whether to attempt speaker identification (experimental)
    
    Returns:
        Transcription result as formatted string
    """
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file does not exist: {audio_path}")
    
    try:
        # Try to import faster-whisper first, fall back to openai-whisper
        try:
            from faster_whisper import WhisperModel
            use_faster = True
        except ImportError:
            try:
                import whisper
                use_faster = False
            except ImportError:
                return "Error: Neither faster-whisper nor openai-whisper is installed. Install with: pip install faster-whisper"
        
        # Load model
        if use_faster:
            # Use faster-whisper for better performance
            model = WhisperModel(model_size, device="auto", compute_type="auto")
            segments, info = model.transcribe(audio_path, 
                                            language=None if language == "auto" else language,
                                            word_timestamps=include_timestamps)
            
            # Convert segments to list for processing
            segments_list = list(segments)
            detected_language = info.language
            
        else:
            # Use standard openai-whisper
            model = whisper.load_model(model_size)
            result = model.transcribe(audio_path, 
                                    language=None if language == "auto" else language,
                                    word_timestamps=include_timestamps)
            segments_list = result["segments"]
            detected_language = result["language"]
        
        # Format output based on requested format
        if output_format == "srt":
            return format_as_srt(segments_list, use_faster)
        elif output_format == "vtt":
            return format_as_vtt(segments_list, use_faster)
        elif output_format == "json":
            return format_as_json(segments_list, detected_language, use_faster)
        elif output_format == "tsv":
            return format_as_tsv(segments_list, use_faster)
        else:  # txt
            return format_as_txt(segments_list, use_faster)
            
    except Exception as e:
        return f"Error during transcription: {str(e)}"


def transcribe_video_whisper(video_path: str,
                           model_size: str = "base",
                           language: str = "auto", 
                           output_format: str = "srt",
                           extract_audio_first: bool = True) -> str:
    """
    Transcribe video using OpenAI Whisper by extracting audio first.
    
    Args:
        video_path: Path to video file
        model_size: Whisper model size
        language: Target language code or "auto"
        output_format: Output format
        extract_audio_first: Whether to extract audio to temp file first
    
    Returns:
        Transcription result
    """
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file does not exist: {video_path}")
    
    try:
        if extract_audio_first:
            # Extract audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
            
            # Extract audio using ffmpeg
            input_stream = ffmpeg.input(video_path)
            audio_stream = input_stream.audio
            output = ffmpeg.output(audio_stream, temp_audio_path, 
                                 ar=16000, ac=1, f='wav')  # 16kHz mono for Whisper
            ffmpeg.run(output, overwrite_output=True, quiet=True)
            
            # Transcribe the extracted audio
            result = transcribe_audio_whisper(temp_audio_path, model_size, 
                                            language, output_format)
            
            # Clean up temporary file
            os.unlink(temp_audio_path)
            
            return result
        else:
            # Transcribe video directly (if Whisper supports it)
            return transcribe_audio_whisper(video_path, model_size, 
                                          language, output_format)
            
    except Exception as e:
        return f"Error transcribing video: {str(e)}"


def batch_transcribe_videos(video_directory: str,
                          output_directory: str,
                          model_size: str = "base",
                          language: str = "auto",
                          output_format: str = "srt",
                          file_pattern: str = "*.mp4") -> str:
    """
    Batch transcribe multiple videos in a directory.
    
    Args:
        video_directory: Directory containing video files
        output_directory: Directory for transcription outputs
        model_size: Whisper model size
        language: Target language
        output_format: Output format
        file_pattern: Pattern to match files
    
    Returns:
        Summary of batch transcription results
    """
    
    if not os.path.exists(video_directory):
        raise FileNotFoundError(f"Video directory does not exist: {video_directory}")
    
    try:
        import glob
        
        os.makedirs(output_directory, exist_ok=True)
        
        # Find all matching video files
        search_pattern = os.path.join(video_directory, "**", file_pattern)
        video_files = glob.glob(search_pattern, recursive=True)
        
        if not video_files:
            return f"No video files found matching pattern: {file_pattern}"
        
        processed_count = 0
        failed_count = 0
        error_messages = []
        
        for video_file in video_files:
            try:
                # Generate output filename
                rel_path = os.path.relpath(video_file, video_directory)
                base_name = os.path.splitext(rel_path)[0]
                
                if output_format == "srt":
                    output_file = os.path.join(output_directory, f"{base_name}.srt")
                elif output_format == "vtt":
                    output_file = os.path.join(output_directory, f"{base_name}.vtt")
                elif output_format == "json":
                    output_file = os.path.join(output_directory, f"{base_name}_transcript.json")
                else:
                    output_file = os.path.join(output_directory, f"{base_name}_transcript.txt")
                
                # Create output subdirectories if needed
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                # Transcribe video
                transcription = transcribe_video_whisper(video_file, model_size, 
                                                       language, output_format)
                
                # Save transcription
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(transcription)
                
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                error_messages.append(f"{os.path.basename(video_file)}: {str(e)}")
        
        result = f"Batch transcription complete: {processed_count} videos transcribed"
        if failed_count > 0:
            result += f", {failed_count} failed"
            result += f"\\nFirst few errors: {'; '.join(error_messages[:3])}"
        
        return result
        
    except Exception as e:
        return f"Error in batch transcription: {str(e)}"


def format_as_srt(segments, use_faster_format=False):
    """Format segments as SRT subtitle format."""
    srt_content = []
    
    for i, segment in enumerate(segments, 1):
        if use_faster_format:
            start_time = format_timestamp(segment.start)
            end_time = format_timestamp(segment.end)
            text = segment.text.strip()
        else:
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()
        
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(text)
        srt_content.append("")  # Empty line between subtitles
    
    return "\\n".join(srt_content)


def format_as_vtt(segments, use_faster_format=False):
    """Format segments as WebVTT format."""
    vtt_content = ["WEBVTT", ""]
    
    for segment in segments:
        if use_faster_format:
            start_time = format_timestamp(segment.start, vtt_format=True)
            end_time = format_timestamp(segment.end, vtt_format=True)
            text = segment.text.strip()
        else:
            start_time = format_timestamp(segment["start"], vtt_format=True)
            end_time = format_timestamp(segment["end"], vtt_format=True)
            text = segment["text"].strip()
        
        vtt_content.append(f"{start_time} --> {end_time}")
        vtt_content.append(text)
        vtt_content.append("")
    
    return "\\n".join(vtt_content)


def format_as_json(segments, language, use_faster_format=False):
    """Format segments as JSON."""
    json_data = {
        "language": language,
        "segments": []
    }
    
    for segment in segments:
        if use_faster_format:
            seg_data = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }
        else:
            seg_data = {
                "start": segment["start"],
                "end": segment["end"], 
                "text": segment["text"].strip()
            }
        json_data["segments"].append(seg_data)
    
    return json.dumps(json_data, indent=2, ensure_ascii=False)


def format_as_tsv(segments, use_faster_format=False):
    """Format segments as TSV (Tab Separated Values)."""
    tsv_lines = ["start\\tend\\ttext"]
    
    for segment in segments:
        if use_faster_format:
            start = f"{segment.start:.3f}"
            end = f"{segment.end:.3f}"
            text = segment.text.strip().replace("\\t", " ")
        else:
            start = f"{segment['start']:.3f}"
            end = f"{segment['end']:.3f}"
            text = segment["text"].strip().replace("\\t", " ")
        
        tsv_lines.append(f"{start}\\t{end}\\t{text}")
    
    return "\\n".join(tsv_lines)


def format_as_txt(segments, use_faster_format=False):
    """Format segments as plain text."""
    txt_lines = []
    
    for segment in segments:
        if use_faster_format:
            text = segment.text.strip()
        else:
            text = segment["text"].strip()
        txt_lines.append(text)
    
    return " ".join(txt_lines)


def format_timestamp(seconds, vtt_format=False):
    """Format seconds as timestamp string."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    
    if vtt_format:
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
    else:
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")


def create_styled_subtitles(video_path: str, transcription_path: str, 
                          output_video_path: str,
                          subtitle_style: Dict = None) -> str:
    """
    Burn styled subtitles into video using transcription file.
    
    Args:
        video_path: Path to input video
        transcription_path: Path to SRT/VTT transcription file
        output_video_path: Path for output video with burned subtitles
        subtitle_style: Dictionary with style parameters
    
    Returns:
        Success message
    """
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file does not exist: {video_path}")
    
    if not os.path.exists(transcription_path):
        raise FileNotFoundError(f"Transcription file does not exist: {transcription_path}")
    
    # Default subtitle style
    if not subtitle_style:
        subtitle_style = {
            'font_size': 24,
            'font_color': 'white',
            'background_color': 'black@0.5',
            'position': 'bottom_center',
            'margin': 20
        }
    
    try:
        input_stream = ffmpeg.input(video_path)
        
        # Build subtitle filter
        subtitle_filter = f"subtitles={transcription_path}"
        
        # Add style parameters
        style_params = []
        if 'font_size' in subtitle_style:
            style_params.append(f"FontSize={subtitle_style['font_size']}")
        if 'font_color' in subtitle_style:
            style_params.append(f"PrimaryColour=&H{color_to_hex(subtitle_style['font_color'])}")
        if 'background_color' in subtitle_style:
            style_params.append(f"BackColour=&H{color_to_hex(subtitle_style['background_color'])}")
        
        if style_params:
            subtitle_filter += f":force_style='{','.join(style_params)}'"
        
        # Apply subtitle filter
        video_stream = input_stream.video.filter('subtitles', transcription_path,
                                                force_style=','.join(style_params) if style_params else None)
        
        output = ffmpeg.output(video_stream, input_stream.audio, output_video_path,
                             vcodec='libx264', acodec='aac',
                             preset='medium', crf=18)
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully created video with styled subtitles: {output_video_path}"
        
    except Exception as e:
        return f"Error creating styled subtitles: {str(e)}"


def color_to_hex(color_name):
    """Convert color name to hex for subtitle styling."""
    color_map = {
        'white': 'FFFFFF',
        'black': '000000',
        'red': 'FF0000',
        'green': '00FF00',
        'blue': '0000FF',
        'yellow': 'FFFF00',
        'cyan': '00FFFF',
        'magenta': 'FF00FF'
    }
    return color_map.get(color_name.lower(), 'FFFFFF')