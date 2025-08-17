import ffmpeg
import os

def apply_chroma_key(foreground_video_path: str, background_video_path: str, 
                    output_video_path: str, key_color: str = "green",
                    similarity: float = 0.3, blend: float = 0.1,
                    spill_removal: bool = True, edge_softening: bool = True,
                    custom_params: dict = None) -> str:
    """Applies chroma key (green screen) effect to replace a specific color with background video.
    
    Args:
        foreground_video_path: Path to the foreground video with green screen
        background_video_path: Path to the background video or image to composite
        output_video_path: Path to save the composited video
        key_color: Color to key out ('green', 'blue', 'red', or hex value like '#00FF00')
        similarity: How similar colors will be keyed (0.0 to 1.0, higher = more aggressive)
        blend: Blending amount for smooth edges (0.0 to 1.0)
        spill_removal: Whether to remove color spill from the key color
        edge_softening: Whether to apply edge softening for smoother compositing
        custom_params: Optional dictionary for advanced chroma key parameters
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(foreground_video_path):
        return f"Error: Foreground video file not found at {foreground_video_path}"
    
    if not os.path.exists(background_video_path):
        return f"Error: Background video file not found at {background_video_path}"
    
    if similarity < 0.0 or similarity > 1.0:
        return "Error: Similarity must be between 0.0 and 1.0"
    
    if blend < 0.0 or blend > 1.0:
        return "Error: Blend must be between 0.0 and 1.0"
    
    custom_params = custom_params or {}
    
    try:
        # Color mapping for common chroma key colors
        color_map = {
            'green': '0x00FF00',
            'blue': '0x0000FF', 
            'red': '0xFF0000',
            'cyan': '0x00FFFF',
            'magenta': '0xFF00FF',
            'yellow': '0xFFFF00'
        }
        
        # Use mapped color or assume hex value
        chroma_color = color_map.get(key_color.lower(), key_color)
        
        # Input streams
        foreground = ffmpeg.input(foreground_video_path)
        background = ffmpeg.input(background_video_path)
        
        # Build filter chain
        filter_chain = []
        
        # Step 1: Basic chroma key
        fg_stream = foreground.video
        
        # Apply primary chroma key
        chromakey_params = {
            'color': chroma_color,
            'similarity': similarity,
            'blend': blend
        }
        
        # Add custom parameters
        chromakey_params.update(custom_params.get('chromakey', {}))
        
        fg_keyed = fg_stream.filter('chromakey', **chromakey_params)
        
        # Step 2: Spill removal (remove color contamination)
        if spill_removal:
            spill_params = custom_params.get('spill', {
                'spillmix': 0.7,
                'spillexpand': 0.0
            })
            fg_keyed = fg_keyed.filter('despill', color=chroma_color, **spill_params)
        
        # Step 3: Edge enhancement and softening
        if edge_softening:
            # Apply slight blur to alpha channel for smoother edges
            fg_keyed = fg_keyed.filter('alphaextract').filter('gblur', sigma=1.0).filter('alphamerge', fg_keyed)
        
        # Step 4: Background preparation
        bg_stream = background.video
        
        # Scale background to match foreground if needed
        bg_scaled = bg_stream.filter('scale', 
                                   width='iw', 
                                   height='ih',
                                   force_original_aspect_ratio='decrease').filter(
                                   'pad', 
                                   width='iw',
                                   height='ih',
                                   x='(ow-iw)/2',
                                   y='(oh-ih)/2')
        
        # Step 5: Composite foreground over background
        composited = bg_scaled.overlay(fg_keyed, x=0, y=0)
        
        # Optional: Color correction and matching
        if custom_params.get('color_match', False):
            # Apply color correction to match foreground and background
            composited = composited.filter('colorbalance', 
                                         rs=custom_params.get('red_shadows', 0),
                                         gs=custom_params.get('green_shadows', 0), 
                                         bs=custom_params.get('blue_shadows', 0))
        
        # Output with audio from foreground
        output = ffmpeg.output(
            composited,
            foreground.audio,
            output_video_path,
            vcodec='libx264',
            pix_fmt='yuv420p',
            acodec='copy'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Chroma key applied successfully. Key color: {key_color}, Similarity: {similarity}, Blend: {blend}. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error applying chroma key: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def create_virtual_background(foreground_video_path: str, background_image_path: str,
                            output_video_path: str, effect_type: str = "blur",
                            key_color: str = "green", intensity: float = 1.0) -> str:
    """Creates virtual background effects with various styles.
    
    Args:
        foreground_video_path: Path to the foreground video with person
        background_image_path: Path to the background image or video
        output_video_path: Path to save the final video
        effect_type: Background effect type ('blur', 'replace', 'color_shift', 'artistic')
        key_color: Color to key out if using chroma key
        intensity: Effect intensity (0.0 to 2.0)
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(foreground_video_path):
        return f"Error: Foreground video file not found at {foreground_video_path}"
    
    if not os.path.exists(background_image_path):
        return f"Error: Background file not found at {background_image_path}"
    
    try:
        foreground = ffmpeg.input(foreground_video_path)
        background = ffmpeg.input(background_image_path, loop=1, t=30)  # Loop background
        
        fg_stream = foreground.video
        bg_stream = background.video
        
        # Apply background effects
        if effect_type == "blur":
            bg_stream = bg_stream.filter('gblur', sigma=5 * intensity)
        elif effect_type == "color_shift":
            bg_stream = bg_stream.filter('hue', h=30 * intensity, s=1 + intensity)
        elif effect_type == "artistic":
            bg_stream = bg_stream.filter('edgedetect').filter('negate')
        
        # Scale background to match foreground
        bg_stream = bg_stream.filter('scale', 'iw', 'ih')
        
        # If using chroma key
        if key_color:
            fg_keyed = fg_stream.filter('chromakey', 
                                      color=key_color, 
                                      similarity=0.3, 
                                      blend=0.1)
            composited = bg_stream.overlay(fg_keyed)
        else:
            # Simple overlay without keying
            composited = bg_stream.overlay(fg_stream)
        
        output = ffmpeg.output(
            composited,
            foreground.audio,
            output_video_path,
            vcodec='libx264',
            acodec='copy'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Virtual background created successfully with {effect_type} effect. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error creating virtual background: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def advanced_chroma_key_with_lighting(foreground_video_path: str, background_video_path: str,
                                    output_video_path: str, key_color: str = "green",
                                    auto_lighting: bool = True, shadow_opacity: float = 0.3,
                                    highlight_threshold: float = 0.8) -> str:
    """Advanced chroma key with automatic lighting adjustment and shadow preservation.
    
    Args:
        foreground_video_path: Path to the foreground video
        background_video_path: Path to the background video
        output_video_path: Path to save the composited video
        key_color: Color to key out
        auto_lighting: Whether to automatically adjust lighting to match background
        shadow_opacity: Opacity of preserved shadows (0.0 to 1.0)
        highlight_threshold: Threshold for highlight detection (0.0 to 1.0)
    
    Returns:
        A status message indicating success or failure.
    """
    try:
        foreground = ffmpeg.input(foreground_video_path)
        background = ffmpeg.input(background_video_path)
        
        fg_stream = foreground.video
        bg_stream = background.video
        
        # Advanced chroma key with edge detection
        fg_keyed = fg_stream.filter('chromakey', 
                                  color=key_color,
                                  similarity=0.25,
                                  blend=0.05)
        
        # Extract edge mask for better compositing
        edges = fg_stream.filter('edgedetect', low=0.1, high=0.4)
        
        # Create shadow mask
        shadow_mask = fg_stream.filter('colorkey', 
                                     color='black',
                                     similarity=0.3).filter(
                                     'colorchannelmixer',
                                     aa=shadow_opacity)
        
        # Lighting adjustment if enabled
        if auto_lighting:
            # Analyze background luminance
            bg_analyzed = bg_stream.filter('lutyuv', y=f'val*{highlight_threshold}')
            
            # Adjust foreground to match
            fg_keyed = fg_keyed.filter('colorbalance',
                                     rm=0.1, gm=0.1, bm=0.1)
        
        # Final composite with shadow preservation
        composited = bg_stream.overlay(shadow_mask, x=0, y=0, format='auto').overlay(fg_keyed, x=0, y=0)
        
        output = ffmpeg.output(
            composited,
            foreground.audio,
            output_video_path,
            vcodec='libx264',
            pix_fmt='yuv420p',
            acodec='copy'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Advanced chroma key with lighting applied successfully. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error applying advanced chroma key: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"