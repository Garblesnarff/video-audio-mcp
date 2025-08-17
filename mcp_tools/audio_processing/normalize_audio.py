
import ffmpeg
import re
import subprocess

def normalize_audio(input_audio_path: str, output_audio_path: str,
                    loudness_target_i: float = -23.0,
                    loudness_range_lra: float = 7.0,
                    true_peak_tp: float = -2.0) -> str:
    """Normalizes the audio loudness to EBU R128 standard using a two-pass process.

    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the normalized audio file.
        loudness_target_i: Target integrated loudness in LUFS. Default: -23.0.
        loudness_range_lra: Target loudness range in LU. Default: 7.0.
        true_peak_tp: Target true peak in dBTP. Default: -2.0.

    Returns:
        A status message indicating success or failure.
    """
    try:
        # Pass 1: Analyze audio and get loudness statistics
        # Use subprocess directly to capture stderr for parsing
        cmd_pass1 = [
            'ffmpeg',
            '-i', input_audio_path,
            '-af', 'loudnorm=print_format=json:I={}:LRA={}:TP={}:linear=true'.format(
                loudness_target_i, loudness_range_lra, true_peak_tp
            ),
            '-f', 'null',
            '-'
        ]
        
        process1 = subprocess.run(cmd_pass1, capture_output=True, text=True, check=False)
        if process1.returncode != 0:
            return f"Error during loudnorm pass 1: {process1.stderr}"

        # Parse the JSON output from stderr
        stats_match = re.search(r'\{[^}]*\}', process1.stderr)
        if not stats_match:
            return f"Error: Could not find loudnorm statistics in stderr output. Stderr: {process1.stderr}"
        
        stats_json_str = stats_match.group(0)
        
        # Extract relevant stats for pass 2
        # Using regex to parse key-value pairs as the output might not be strict JSON
        # Integrated Loudness (I)
        input_i_match = re.search(r'"input_i":\s*([-\d.]+)', stats_json_str)
        input_i = float(input_i_match.group(1)) if input_i_match else 0.0

        # Loudness Range (LRA)
        input_lra_match = re.search(r'"input_lra":\s*([-\d.]+)', stats_json_str)
        input_lra = float(input_lra_match.group(1)) if input_lra_match else 0.0

        # True Peak (TP)
        input_tp_match = re.search(r'"input_tp":\s*([-\d.]+)', stats_json_str)
        input_tp = float(input_tp_match.group(1)) if input_tp_match else 0.0

        # True Peak (TP)
        input_thresh_match = re.search(r'"input_thresh":\s*([-\d.]+)', stats_json_str)
        input_thresh = float(input_thresh_match.group(1)) if input_thresh_match else 0.0

        # Measured values for pass 2
        measured_i_match = re.search(r'"measured_i":\s*([-\d.]+)', stats_json_str)
        measured_i = float(measured_i_match.group(1)) if measured_i_match else 0.0

        measured_lra_match = re.search(r'"measured_lra":\s*([-\d.]+)', stats_json_str)
        measured_lra = float(measured_lra_match.group(1)) if measured_lra_match else 0.0

        measured_tp_match = re.search(r'"measured_tp":\s*([-\d.]+)', stats_json_str)
        measured_tp = float(measured_tp_match.group(1)) if measured_tp_match else 0.0

        measured_thresh_match = re.search(r'"measured_thresh":\s*([-\d.]+)', stats_json_str)
        measured_thresh = float(measured_thresh_match.group(1)) if measured_thresh_match else 0.0

        target_offset_match = re.search(r'"target_offset":\s*([-\d.]+)', stats_json_str)
        target_offset = float(target_offset_match.group(1)) if target_offset_match else 0.0

        # Pass 2: Apply normalization with calculated parameters
        # Use the measured values from pass 1
        loudnorm_filter_pass2 = (
            f"loudnorm=I={loudness_target_i}:LRA={loudness_range_lra}:TP={true_peak_tp}:"
            f"measured_i={measured_i}:measured_lra={measured_lra}:measured_tp={measured_tp}:"
            f"measured_thresh={measured_thresh}:target_offset={target_offset}:linear=true:print_format=json"
        )

        ffmpeg.input(input_audio_path).output(
            output_audio_path,
            af=loudnorm_filter_pass2
        ).run(capture_stdout=True, capture_stderr=True)

        return f"Audio normalized successfully to {loudness_target_i} LUFS and saved to {output_audio_path}"
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        return f"Error normalizing audio: {error_message}"
    except FileNotFoundError:
        return f"Error: Input audio file not found at {input_audio_path}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
