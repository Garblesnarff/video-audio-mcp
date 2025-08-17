import ffmpeg
import os

def denoise_video(input_video_path: str, output_video_path: str,
                 denoise_method: str = "nlmeans", strength: float = 1.0,
                 quality_preset: str = "medium", preserve_details: bool = True,
                 custom_params: dict = None) -> str:
    """Removes noise from video using advanced denoising algorithms.
    
    Args:
        input_video_path: Path to the source video file
        output_video_path: Path to save the denoised video
        denoise_method: Denoising algorithm to use:
            - 'nlmeans': Non-local means (highest quality, slowest)
            - 'hqdn3d': High quality denoiser 3D (fast, good quality)
            - 'atadenoise': Adaptive temporal denoise (balanced)
            - 'vaguedenoiser': Wavelet-based denoiser
            - 'bm3d': Block-matching 3D (if available)
            - 'dfttest': DFT test denoiser
        strength: Denoising strength (0.1 to 10.0, higher = more aggressive)
        quality_preset: Processing quality vs speed:
            - 'fast': Quick processing, lower quality
            - 'medium': Balanced processing
            - 'high': Slow processing, best quality
            - 'ultra': Extremely slow, maximum quality
        preserve_details: Whether to preserve fine details (may reduce denoising)
        custom_params: Optional dictionary for method-specific parameters
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    if strength < 0.1 or strength > 10.0:
        return "Error: Strength must be between 0.1 and 10.0"
    
    custom_params = custom_params or {}
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        video_stream = input_stream.video
        
        # Apply denoising based on selected method
        if denoise_method == "nlmeans":
            # Non-local means denoiser - highest quality
            s = strength * 3.0  # Scale strength for nlmeans
            
            if quality_preset == "fast":
                r = 5  # Research size
                p = 3  # Patch size
            elif quality_preset == "medium":
                r = 15
                p = 7
            elif quality_preset == "high":
                r = 21
                p = 9
            else:  # ultra
                r = 31
                p = 15
            
            # Add custom parameters
            nlmeans_params = {
                's': min(s, 30.0),  # Strength (max 30)
                'r': custom_params.get('research_size', r),  # Research size
                'p': custom_params.get('patch_size', p)  # Patch size
            }
            
            video_stream = video_stream.filter('nlmeans', **nlmeans_params)
        
        elif denoise_method == "hqdn3d":
            # High quality denoiser 3D - fast and effective
            luma_spatial = strength * 4.0
            chroma_spatial = strength * 3.0
            luma_temporal = strength * 6.0
            chroma_temporal = strength * 4.5
            
            if quality_preset == "fast":
                luma_spatial *= 0.7
                luma_temporal *= 0.7
            elif quality_preset in ["high", "ultra"]:
                luma_spatial *= 1.3
                luma_temporal *= 1.3
            
            hqdn3d_params = {
                'luma_spatial': custom_params.get('luma_spatial', luma_spatial),
                'chroma_spatial': custom_params.get('chroma_spatial', chroma_spatial),
                'luma_temporal': custom_params.get('luma_temporal', luma_temporal),
                'chroma_temporal': custom_params.get('chroma_temporal', chroma_temporal)
            }
            
            video_stream = video_stream.filter('hqdn3d', **hqdn3d_params)
        
        elif denoise_method == "atadenoise":
            # Adaptive temporal denoiser
            s = strength * 0.02  # atadenoise uses smaller values
            t = custom_params.get('temporal_threshold', 0.04)
            
            atadenoise_params = {
                's': min(s, 0.1),
                't': t
            }
            
            if quality_preset in ["high", "ultra"]:
                atadenoise_params['a'] = custom_params.get('algorithm', 'p')  # Parallel processing
            
            video_stream = video_stream.filter('atadenoise', **atadenoise_params)
        
        elif denoise_method == "vaguedenoiser":
            # Wavelet-based denoiser
            threshold = strength * 6.0
            method = custom_params.get('method', 1)  # 0=soft, 1=hard thresholding
            nsteps = custom_params.get('nsteps', 6)  # Wavelet steps
            
            vague_params = {
                'threshold': min(threshold, 100.0),
                'method': method,
                'nsteps': nsteps
            }
            
            video_stream = video_stream.filter('vaguedenoiser', **vague_params)
        
        elif denoise_method == "bm3d":
            # Block-matching 3D (if available)
            sigma = strength * 25.0
            
            bm3d_params = {
                'sigma': min(sigma, 100.0),
                'block': custom_params.get('block_size', 8),
                'bstep': custom_params.get('block_step', 4),
                'group': custom_params.get('group_size', 1),
                'range': custom_params.get('search_range', 9)
            }
            
            try:
                video_stream = video_stream.filter('bm3d', **bm3d_params)
            except:
                # Fallback to nlmeans if bm3d not available
                return denoise_video(input_video_path, output_video_path, 
                                   "nlmeans", strength, quality_preset, preserve_details)
        
        elif denoise_method == "dfttest":
            # DFT test denoiser
            sigma = strength * 16.0
            
            dfttest_params = {
                'sigma': min(sigma, 100.0),
                'tbsize': custom_params.get('temporal_size', 5),
                'sbsize': custom_params.get('spatial_size', 12),
                'sosize': custom_params.get('spatial_overlap', 9)
            }
            
            try:
                video_stream = video_stream.filter('dfttest', **dfttest_params)
            except:
                # Fallback to hqdn3d if dfttest not available
                return denoise_video(input_video_path, output_video_path,
                                   "hqdn3d", strength, quality_preset, preserve_details)
        
        else:
            return f"Error: Unknown denoise method '{denoise_method}'"
        
        # Post-processing for detail preservation
        if preserve_details and denoise_method in ["nlmeans", "hqdn3d"]:
            # Apply subtle sharpening to restore details lost in denoising
            sharpen_amount = 0.3 if strength > 5.0 else 0.1
            
            unsharp_params = {
                'luma_msize_x': 5,
                'luma_msize_y': 5,
                'luma_amount': sharpen_amount,
                'chroma_msize_x': 5,
                'chroma_msize_y': 5,
                'chroma_amount': sharpen_amount * 0.5
            }
            
            video_stream = video_stream.filter('unsharp', **unsharp_params)
        
        # Set encoding parameters based on quality preset
        if quality_preset == "fast":
            encode_preset = "ultrafast"
            crf = 25
        elif quality_preset == "medium":
            encode_preset = "medium"
            crf = 21
        elif quality_preset == "high":
            encode_preset = "slow"
            crf = 18
        else:  # ultra
            encode_preset = "veryslow"
            crf = 15
        
        # Create output
        output = ffmpeg.output(
            video_stream,
            input_stream.audio,
            output_video_path,
            vcodec='libx264',
            preset=encode_preset,
            crf=crf,
            acodec='copy'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Video denoised successfully using '{denoise_method}' method. Strength: {strength}, Quality: {quality_preset}. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error denoising video: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def denoise_video_advanced(input_video_path: str, output_video_path: str,
                          noise_profile: str = "auto", temporal_consistency: bool = True,
                          grain_preservation: float = 0.0) -> str:
    """Advanced video denoising with automatic noise profiling and grain preservation.
    
    Args:
        input_video_path: Path to the source video file
        output_video_path: Path to save the denoised video
        noise_profile: Noise characteristics:
            - 'auto': Automatically detect noise type
            - 'film_grain': Preserve film grain while removing noise
            - 'digital_noise': Remove digital camera noise
            - 'compression_artifacts': Remove compression artifacts
            - 'old_footage': Restore old/archival footage
        temporal_consistency: Whether to maintain consistency across frames
        grain_preservation: Amount of original grain to preserve (0.0-1.0)
    
    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(input_video_path):
        return f"Error: Input video file not found at {input_video_path}"
    
    try:
        input_stream = ffmpeg.input(input_video_path)
        video_stream = input_stream.video
        
        # Apply denoising strategy based on noise profile
        if noise_profile in ["auto", "digital_noise"]:
            # Two-pass denoising: temporal then spatial
            
            # Pass 1: Temporal denoising
            video_stream = video_stream.filter('hqdn3d',
                                             luma_spatial=0,
                                             chroma_spatial=0,
                                             luma_temporal=6.0,
                                             chroma_temporal=4.5)
            
            # Pass 2: Spatial denoising
            video_stream = video_stream.filter('nlmeans', s=2.0, r=15, p=7)
        
        elif noise_profile == "film_grain":
            # Preserve grain while removing noise
            
            # Light denoising to preserve grain character
            video_stream = video_stream.filter('hqdn3d',
                                             luma_spatial=1.5,
                                             chroma_spatial=1.2,
                                             luma_temporal=3.0,
                                             chroma_temporal=2.0)
            
            # Add back controlled grain if preservation requested
            if grain_preservation > 0:
                grain_strength = int(grain_preservation * 20)
                video_stream = video_stream.filter('noise', 
                                                 alls=grain_strength,
                                                 allf='t+u')
        
        elif noise_profile == "compression_artifacts":
            # Remove blocking and ringing artifacts
            
            # Deblock filter for compression artifacts
            video_stream = video_stream.filter('deblock',
                                             filter='strong',
                                             block=8)
            
            # Follow with gentle denoising
            video_stream = video_stream.filter('hqdn3d',
                                             luma_spatial=2.0,
                                             chroma_spatial=3.0,
                                             luma_temporal=2.0,
                                             chroma_temporal=3.0)
        
        elif noise_profile == "old_footage":
            # Comprehensive restoration for old footage
            
            # Strong temporal denoising for flickering
            video_stream = video_stream.filter('hqdn3d',
                                             luma_spatial=1.0,
                                             chroma_spatial=2.0,
                                             luma_temporal=8.0,
                                             chroma_temporal=6.0)
            
            # Spatial denoising
            video_stream = video_stream.filter('nlmeans', s=4.0, r=21, p=9)
            
            # Deflicker for old film
            video_stream = video_stream.filter('deflicker', size=5, mode='pm')
        
        # Apply temporal consistency if requested
        if temporal_consistency and noise_profile != "old_footage":
            # Additional temporal smoothing
            video_stream = video_stream.filter('minterpolate',
                                             fps=30,
                                             mi_mode='mci',
                                             mc_mode='aobmc',
                                             vsbmc=1)
        
        # Create output with high quality settings
        output = ffmpeg.output(
            video_stream,
            input_stream.audio,
            output_video_path,
            vcodec='libx264',
            preset='slow',
            crf=18,
            acodec='copy'
        )
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        return f"Advanced video denoising completed. Profile: {noise_profile}, Temporal consistency: {temporal_consistency}. Output saved to {output_video_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error in advanced denoising: {error_message}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def batch_denoise_videos(video_list: list[str], output_directory: str,
                        denoise_settings: dict) -> str:
    """Batch denoise multiple videos with the same settings.
    
    Args:
        video_list: List of paths to video files
        output_directory: Directory to save denoised videos
        denoise_settings: Dictionary with denoising parameters
    
    Returns:
        A status message indicating success or failure.
    """
    if not video_list:
        return "Error: No video files provided"
    
    os.makedirs(output_directory, exist_ok=True)
    
    results = []
    successful = 0
    failed = 0
    
    for video_path in video_list:
        if not os.path.exists(video_path):
            results.append(f"FAILED: {video_path} - file not found")
            failed += 1
            continue
        
        try:
            # Generate output filename
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(output_directory, f"{video_name}_denoised.mp4")
            
            # Apply denoising
            result = denoise_video(
                input_video_path=video_path,
                output_video_path=output_path,
                **denoise_settings
            )
            
            if "Error" not in result:
                results.append(f"SUCCESS: {video_name}")
                successful += 1
            else:
                results.append(f"FAILED: {video_name} - {result}")
                failed += 1
                
        except Exception as e:
            results.append(f"FAILED: {video_name} - {str(e)}")
            failed += 1
    
    summary = f"Batch denoising completed. Successful: {successful}, Failed: {failed}"
    if failed > 0:
        summary += f"\n\nDetails:\n" + "\n".join(results)
    
    return summary