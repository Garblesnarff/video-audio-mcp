import ffmpeg
import os

def apply_video_filters(input_video_path: str, output_video_path: str, 
                       filter_type: str, intensity: float = 1.0, 
                       custom_params: dict = None) -> str:
    """Applies various video filters to enhance or stylize video content.
    
    Args:
        input_video_path: Path to the source video file
        output_video_path: Path to save the filtered video
        filter_type: Type of filter to apply. Options:
            - 'blur': Gaussian blur effect
            - 'sharpen': Sharpen details
            - 'vintage': Vintage film look with grain and color shifts
            - 'sepia': Sepia tone effect
            - 'blackwhite': Convert to black and white
            - 'brightness': Adjust brightness
            - 'contrast': Adjust contrast
            - 'saturation': Adjust color saturation
            - 'vignette': Add dark vignette effect
            - 'grain': Add film grain texture
            - 'chromatic_aberration': Add chromatic aberration effect
            - 'glow': Add soft glow effect
        intensity: Filter intensity (0.0 to 2.0, default 1.0)
        custom_params: Optional dictionary for filter-specific parameters
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    if intensity < 0.0 or intensity > 2.0:
        return "Error: Intensity must be between 0.0 and 2.0"
    
    custom_params = custom_params or {}
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        
        # Define filter configurations
        filter_configs = {
            'blur': {
                'filter': 'gblur',
                'params': {'sigma': 2.0 * intensity}
            },
            'sharpen': {
                'filter': 'unsharp',
                'params': {
                    'luma_msize_x': 5,
                    'luma_msize_y': 5, 
                    'luma_amount': 1.0 + intensity,
                    'chroma_msize_x': 5,
                    'chroma_msize_y': 5,
                    'chroma_amount': 1.0 + (intensity * 0.5)
                }
            },
            'vintage': {
                'filter': 'colorchannelmixer',
                'params': {
                    'rr': 0.393 + (intensity * 0.1),
                    'rg': 0.769 - (intensity * 0.1),
                    'rb': 0.189,
                    'gr': 0.349,
                    'gg': 0.686 + (intensity * 0.1),
                    'gb': 0.168,
                    'br': 0.272,
                    'bg': 0.534,
                    'bb': 0.131 + (intensity * 0.2)
                },
                'post_filters': [
                    ('curves', {'preset': 'vintage'}),
                    ('noise', {'alls': int(10 * intensity), 'allf': 't'})
                ]
            },
            'sepia': {
                'filter': 'colorchannelmixer',
                'params': {
                    'rr': 0.393 * intensity + (1 - intensity),
                    'rg': 0.769 * intensity,
                    'rb': 0.189 * intensity,
                    'gr': 0.349 * intensity,
                    'gg': 0.686 * intensity + (1 - intensity),
                    'gb': 0.168 * intensity,
                    'br': 0.272 * intensity,
                    'bg': 0.534 * intensity,
                    'bb': 0.131 * intensity + (1 - intensity)
                }
            },
            'blackwhite': {
                'filter': 'colorchannelmixer',
                'params': {
                    'rr': 0.299 * intensity + (1 - intensity),
                    'rg': 0.587 * intensity,
                    'rb': 0.114 * intensity,
                    'gr': 0.299 * intensity,
                    'gg': 0.587 * intensity + (1 - intensity),
                    'gb': 0.114 * intensity,
                    'br': 0.299 * intensity,
                    'bg': 0.587 * intensity,
                    'bb': 0.114 * intensity + (1 - intensity)
                }
            },
            'brightness': {
                'filter': 'eq',
                'params': {'brightness': (intensity - 1.0) * 0.3}
            },
            'contrast': {
                'filter': 'eq',
                'params': {'contrast': intensity}
            },
            'saturation': {
                'filter': 'eq',
                'params': {'saturation': intensity}
            },
            'vignette': {
                'filter': 'vignette',
                'params': {
                    'angle': 'PI/4',
                    'x0': 'W/2',
                    'y0': 'H/2',
                    'mode': 'backward',
                    'eval': 'init',
                    'dither': 1,
                    'aspect': 1,
                    'a': f'PI/{3.0/intensity}'  # Adjust vignette size based on intensity
                }
            },
            'grain': {
                'filter': 'noise',
                'params': {
                    'alls': int(20 * intensity),
                    'allf': 't+u'
                }
            },
            'chromatic_aberration': {
                'custom_complex': True,
                'filter_complex': f'''
                [0:v]split=3[r][g][b];
                [r]lutrgb=r=val:g=0:b=0,crop=iw-{int(4*intensity)}:ih:{int(2*intensity)}:0[r_shifted];
                [g]lutrgb=r=0:g=val:b=0[g_normal];
                [b]lutrgb=r=0:g=0:b=val,crop=iw-{int(4*intensity)}:ih:0:{int(2*intensity)}[b_shifted];
                [r_shifted][g_normal]blend=all_mode=addition[rg];
                [rg][b_shifted]blend=all_mode=addition[v]
                '''
            },
            'glow': {
                'custom_complex': True,
                'filter_complex': f'''
                [0:v]split[main][glow];
                [glow]gblur=sigma={5*intensity}[glowblur];
                [main][glowblur]blend=all_mode=addition:all_opacity={0.3*intensity}[v]
                '''
            }
        }
        
        if filter_type not in filter_configs:
            available_filters = ', '.join(filter_configs.keys())
            return f"Error: Unknown filter type '{filter_type}'. Available filters: {available_filters}"
        
        config = filter_configs[filter_type]
        
        # Merge custom parameters
        if 'params' in config:
            config['params'].update(custom_params)
        
        # Apply filter
        if config.get('custom_complex'):
            # Use complex filter for advanced effects
            output = ffmpeg.output(
                input_stream,
                output_video_path,
                filter_complex=config['filter_complex'],
                map='[v]',
                acodec='copy'
            )
        else:
            # Apply standard filter
            video_stream = input_stream.video
            video_stream = video_stream.filter(config['filter'], **config['params'])
            
            # Apply post-filters if defined
            if 'post_filters' in config:
                for post_filter, post_params in config['post_filters']:
                    video_stream = video_stream.filter(post_filter, **post_params)
            
            output = ffmpeg.output(
                video_stream,
                input_stream.audio,
                output_video_path,
                vcodec='libx264',
                acodec='copy'
            )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Video filter '{filter_type}' applied successfully with intensity {intensity}. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error applying video filter: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"