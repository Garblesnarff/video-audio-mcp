import ffmpeg
import os
from typing import Optional, Dict

def upscale_video(input_video_path: str, output_video_path: str,
                 scale_factor: float = 2.0,
                 upscale_method: str = "lanczos",
                 enhance_quality: bool = True,
                 target_resolution: str = None,
                 maintain_aspect: bool = True) -> str:
    """
    Upscale video resolution using various algorithms.
    
    Args:
        input_video_path: Path to the input video file
        output_video_path: Path for the output video file
        scale_factor: Factor to upscale by (2.0 = double resolution)
        upscale_method: Algorithm ("lanczos", "bicubic", "bilinear", "neighbor", "spline")
        enhance_quality: Apply additional sharpening and enhancement
        target_resolution: Specific target resolution ("1920x1080", "3840x2160")
        maintain_aspect: Whether to maintain aspect ratio
    
    Returns:
        Success message with output file path
    """
    
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video file does not exist: {input_video_path}")
    
    try:
        # Get video information
        probe = ffmpeg.probe(input_video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        
        input_stream = ffmpeg.input(input_video_path)
        
        # Calculate target dimensions
        if target_resolution:
            target_width, target_height = map(int, target_resolution.split('x'))
        else:
            target_width = int(width * scale_factor)
            target_height = int(height * scale_factor)
        
        # Apply scaling with chosen algorithm
        scale_params = {
            'width': target_width,
            'height': target_height
        }
        
        if maintain_aspect:
            scale_params['force_original_aspect_ratio'] = 'decrease'
        
        # Map upscale methods to FFmpeg flags
        method_map = {
            'lanczos': 'lanczos',
            'bicubic': 'bicubic', 
            'bilinear': 'bilinear',
            'neighbor': 'neighbor',
            'spline': 'spline'
        }
        
        if upscale_method in method_map:
            scale_params['flags'] = method_map[upscale_method]
        
        video_stream = input_stream.video.filter('scale', **scale_params)
        
        # Apply enhancement filters
        if enhance_quality:
            # Unsharp mask for sharpening
            video_stream = video_stream.filter('unsharp', 
                                             luma_msize_x=5, luma_msize_y=5,
                                             luma_amount=1.2, luma_threshold=0)
            
            # Slight noise reduction
            video_stream = video_stream.filter('hqdn3d', 2, 1, 2, 1)
            
            # Color enhancement
            video_stream = video_stream.filter('eq', 
                                             contrast=1.1, brightness=0.02, 
                                             saturation=1.05, gamma=0.98)
        
        # Pad to exact dimensions if needed and maintaining aspect
        if maintain_aspect and target_resolution:
            video_stream = video_stream.filter('pad', target_width, target_height, 
                                             '(ow-iw)/2', '(oh-ih)/2', 'black')
        
        # Output with high quality settings
        output = ffmpeg.output(video_stream, input_stream.audio, output_video_path,
                             vcodec='libx264', acodec='aac',
                             preset='slow', crf=15,
                             **{'movflags': '+faststart'})
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully upscaled video to {target_width}x{target_height}: {output_video_path}"
        
    except Exception as e:
        return f"Error upscaling video: {str(e)}"


def color_correction(input_video_path: str, output_video_path: str,
                    correction_type: str = "auto",
                    custom_params: Dict = None,
                    reference_image: str = None,
                    maintain_quality: bool = True) -> str:
    """
    Apply color correction and grading to video.
    
    Args:
        input_video_path: Path to the input video file
        output_video_path: Path for the output video file
        correction_type: Type of correction ("auto", "warm", "cool", "vintage", "vibrant", "custom")
        custom_params: Custom color parameters (brightness, contrast, saturation, etc.)
        reference_image: Path to reference image for color matching
        maintain_quality: Whether to maintain original quality
    
    Returns:
        Success message with output file path
    """
    
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video file does not exist: {input_video_path}")
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        video_stream = input_stream.video
        
        if correction_type == "auto":
            # Auto levels and color balance
            video_stream = video_stream.filter('eq', contrast=1.1, brightness=0.02, gamma=0.95)
            video_stream = video_stream.filter('colorbalance', 
                                             shadows=0.02, midtones=0.01, highlights=-0.01)
            
        elif correction_type == "warm":
            # Warm color tone
            video_stream = video_stream.filter('colortemperature', temperature=3200)
            video_stream = video_stream.filter('eq', saturation=1.15, gamma=0.92)
            
        elif correction_type == "cool":
            # Cool color tone
            video_stream = video_stream.filter('colortemperature', temperature=6500)
            video_stream = video_stream.filter('eq', saturation=1.1, contrast=1.05)
            
        elif correction_type == "vintage":
            # Vintage film look
            video_stream = video_stream.filter('eq', 
                                             contrast=0.9, brightness=0.1, 
                                             saturation=0.8, gamma=1.1)
            video_stream = video_stream.filter('colorbalance',
                                             shadows=0.1, midtones=0.05, highlights=-0.02)
            # Add slight sepia
            video_stream = video_stream.filter('colorchannelmixer',
                                             rr=0.393, rg=0.769, rb=0.189,
                                             gr=0.349, gg=0.686, gb=0.168,
                                             br=0.272, bg=0.534, bb=0.131)
            
        elif correction_type == "vibrant":
            # Enhanced vibrant colors
            video_stream = video_stream.filter('eq', 
                                             contrast=1.2, saturation=1.3, 
                                             brightness=0.03, gamma=0.9)
            video_stream = video_stream.filter('vibrance', intensity=0.2)
            
        elif correction_type == "custom" and custom_params:
            # Apply custom parameters
            eq_params = {}
            if 'brightness' in custom_params:
                eq_params['brightness'] = custom_params['brightness']
            if 'contrast' in custom_params:
                eq_params['contrast'] = custom_params['contrast']
            if 'saturation' in custom_params:
                eq_params['saturation'] = custom_params['saturation']
            if 'gamma' in custom_params:
                eq_params['gamma'] = custom_params['gamma']
            
            if eq_params:
                video_stream = video_stream.filter('eq', **eq_params)
            
            # Color balance
            if any(k in custom_params for k in ['shadows', 'midtones', 'highlights']):
                balance_params = {}
                for key in ['shadows', 'midtones', 'highlights']:
                    if key in custom_params:
                        balance_params[key] = custom_params[key]
                video_stream = video_stream.filter('colorbalance', **balance_params)
        
        # Reference-based color matching
        if reference_image and os.path.exists(reference_image):
            ref_input = ffmpeg.input(reference_image, loop=1, t=1)
            video_stream = ffmpeg.filter([video_stream, ref_input], 'colormap')
        
        # Output parameters
        output_params = {
            'vcodec': 'libx264',
            'acodec': 'aac'
        }
        
        if maintain_quality:
            output_params.update({
                'preset': 'medium',
                'crf': 18
            })
        
        output = ffmpeg.output(video_stream, input_stream.audio, output_video_path, **output_params)
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully applied {correction_type} color correction: {output_video_path}"
        
    except Exception as e:
        return f"Error applying color correction: {str(e)}"


def auto_enhance_video(input_video_path: str, output_video_path: str,
                      enhancement_level: str = "medium",
                      enhance_audio: bool = True,
                      stabilize: bool = False,
                      denoise: bool = True) -> str:
    """
    Automatically enhance video quality with multiple improvements.
    
    Args:
        input_video_path: Path to the input video file
        output_video_path: Path for the output video file
        enhancement_level: Level of enhancement ("light", "medium", "aggressive")
        enhance_audio: Whether to enhance audio as well
        stabilize: Whether to apply video stabilization
        denoise: Whether to apply noise reduction
    
    Returns:
        Success message with output file path
    """
    
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video file does not exist: {input_video_path}")
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        video_stream = input_stream.video
        audio_stream = input_stream.audio
        
        # Enhancement parameters based on level
        if enhancement_level == "light":
            contrast_boost = 1.05
            saturation_boost = 1.02
            sharpening = 0.5
            noise_reduction = 1
        elif enhancement_level == "medium":
            contrast_boost = 1.1
            saturation_boost = 1.08
            sharpening = 1.0
            noise_reduction = 2
        else:  # aggressive
            contrast_boost = 1.2
            saturation_boost = 1.15
            sharpening = 1.5
            noise_reduction = 3
        
        # Apply video stabilization first if requested
        if stabilize:
            video_stream = video_stream.filter('deshake', x=-1, y=-1, w=-1, h=-1, rx=16, ry=16)
        
        # Noise reduction
        if denoise:
            video_stream = video_stream.filter('hqdn3d', noise_reduction, 1, noise_reduction, 1)
        
        # Color and contrast enhancement
        video_stream = video_stream.filter('eq',
                                         contrast=contrast_boost,
                                         brightness=0.02,
                                         saturation=saturation_boost,
                                         gamma=0.95)
        
        # Sharpening
        video_stream = video_stream.filter('unsharp',
                                         luma_msize_x=5, luma_msize_y=5,
                                         luma_amount=sharpening,
                                         chroma_msize_x=3, chroma_msize_y=3,
                                         chroma_amount=sharpening * 0.5)
        
        # Color balance fine-tuning
        video_stream = video_stream.filter('colorbalance',
                                         shadows=0.01,
                                         midtones=0.005,
                                         highlights=-0.005)
        
        # Audio enhancement
        if enhance_audio:
            # Normalize audio levels
            audio_stream = audio_stream.filter('loudnorm', i=-16.0, tp=-1.5, lra=11.0)
            
            # Enhance audio quality
            audio_stream = audio_stream.filter('highpass', f=80)  # Remove low-frequency noise
            audio_stream = audio_stream.filter('lowpass', f=15000)  # Remove high-frequency noise
            
            # Dynamic range compression
            audio_stream = audio_stream.filter('compand',
                                             attacks='0.1',
                                             decays='0.3',
                                             points='-80/-80|-20/-15|-10/-10|0/-3|20/0')
        
        # Output with optimized settings
        output = ffmpeg.output(video_stream, audio_stream, output_video_path,
                             vcodec='libx264', acodec='aac',
                             preset='medium', crf=16,
                             **{'movflags': '+faststart'})
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return f"Successfully enhanced video ({enhancement_level} level): {output_video_path}"
        
    except Exception as e:
        return f"Error enhancing video: {str(e)}"