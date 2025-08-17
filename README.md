<div align="center">
  <img src="icon.svg" alt="Video & Audio Editing MCP Server" width="128" height="128">
</div>

# 🎬 Video & Audio Editing MCP Server

A comprehensive Model Context Protocol (MCP) server that provides powerful video and audio editing capabilities through FFmpeg. This server enables AI assistants to perform professional-grade video editing operations with **104 specialized tools** covering format conversion, trimming, overlays, transitions, advanced audio processing, AI-powered transcription, computer vision, and cutting-edge features like 360° video, object detection, and automated YouTube optimization.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![smithery badge](https://smithery.ai/badge/@misbahsy/video-audio-mcp)](https://smithery.ai/server/@misbahsy/video-audio-mcp)

## ✨ Features

- **🎥 Video Processing**: Format conversion, resolution scaling, codec changes, frame rate adjustment
- **🎵 Audio Processing**: Format conversion, bitrate adjustment, sample rate changes, channel configuration
- **✂️ Editing Tools**: Video trimming, speed adjustment, aspect ratio changes
- **🎨 Overlays & Effects**: Text overlays, image watermarks, subtitle burning
- **🔗 Advanced Editing**: Video concatenation with transitions, B-roll insertion, silence removal
- **🎭 Transitions**: Fade in/out effects, crossfade transitions between clips

## 🛠️ Available Tools

### Core Video Operations
- `extract_audio_from_video` - Extract audio tracks from video files
- `trim_video` - Cut video segments with precise timing
- `convert_video_format` - Convert between video formats (MP4, MOV, AVI, etc.)
- `convert_video_properties` - Comprehensive video property conversion
- `change_aspect_ratio` - Adjust video aspect ratios with padding or cropping
- `set_video_resolution` - Change video resolution with quality preservation
- `set_video_codec` - Switch video codecs (H.264, H.265, VP9, etc.)
- `set_video_bitrate` - Adjust video quality and file size
- `set_video_frame_rate` - Change playback frame rates

### Audio Processing
- `convert_audio_format` - Convert between audio formats (MP3, WAV, AAC, etc.)
- `convert_audio_properties` - Comprehensive audio property conversion
- `set_audio_bitrate` - Adjust audio quality and compression
- `set_audio_sample_rate` - Change audio sample rates
- `set_audio_channels` - Convert between mono and stereo
- `set_video_audio_track_codec` - Change audio codec in video files
- `set_video_audio_track_bitrate` - Adjust audio bitrate in videos
- `set_video_audio_track_sample_rate` - Change audio sample rate in videos
- `set_video_audio_track_channels` - Adjust audio channels in videos

### Creative Tools
- `add_subtitles` - Burn subtitles with custom styling
- `add_text_overlay` - Add dynamic text overlays with timing
- `add_image_overlay` - Insert watermarks and logos
- `add_b_roll` - Insert B-roll footage with transitions
- `add_basic_transitions` - Apply fade in/out effects

### Advanced Editing
- `concatenate_videos` - Join multiple videos with optional transitions
- `change_video_speed` - Create slow-motion or time-lapse effects
- `remove_silence` - Automatically remove silent segments
- `health_check` - Verify server status

### 🎨 Enhanced Video Effects (NEW!)
- `apply_video_filters` - Advanced visual filters (blur, sharpen, vintage, sepia, black/white, grain, glow, etc.)
- `apply_advanced_transitions` - Professional transition effects (slide, wipe, zoom, circle, polygon, spin, cube, page turn)
- `create_motion_graphics` - Animated text, geometric shapes, particles, counters, and more
- `apply_chroma_key` - Green screen/chroma key with advanced lighting and edge softening
- `create_virtual_background` - Virtual backgrounds with blur, color shift, and artistic effects
- `advanced_chroma_key_with_lighting` - Professional chroma key with automatic lighting adjustment
- `apply_video_morphing` - Smooth morphing transitions (liquid, spiral, twist, ripple, etc.)
- `create_shape_morph` - Animated shape morphing overlays

### 🎵 Enhanced Audio Effects (NEW!)
- `apply_audio_effects` - Professional audio effects (reverb, echo, chorus, distortion, pitch shift, etc.)
- `create_audio_chain` - Chain multiple audio effects in sequence
- `mix_audio_tracks` - Multi-track audio mixing with individual controls
- `create_audio_bed` - Background music with vocal tracks and ducking
- `create_stereo_mix` - Advanced stereo mixing with balance and crossfeed
- `create_surround_mix` - 5.1/7.1 surround sound mixing
- `mix_with_timeline` - Precise timeline-based audio mixing

### 📊 Audio Visualization (NEW!)
- `create_audio_visualization` - Spectrum, waveform, oscilloscope, bars, particles, tunnel, mandala effects
- `create_lyric_visualization` - Lyric videos with audio-reactive backgrounds
- `create_music_video_template` - Professional music video templates with synchronized visuals

### 🎤 Voice Processing (NEW!)
- `process_voice` - Advanced voice processing (noise reduction, enhancement, auto-tune, formant shift)
- `batch_voice_process` - Batch process multiple voice files with effect chains

### 🔊 Spatial Audio (NEW!)
- `create_spatial_audio` - Immersive 3D audio (binaural, surround, ambisonics)
- `create_3d_audio_scene` - Complex 3D audio scenes with multiple positioned sources
- `convert_to_spatial_format` - Convert between spatial audio formats

### 🔄 Video Manipulation (Phase 2A - NEW!)
- `rotate_video` - Rotate videos by any angle with smart fill options
- `flip_mirror_video` - Horizontal/vertical flip and mirror effects
- `rotate_and_flip_video` - Combined rotation and flipping operations
- `auto_rotate_video` - Automatically correct video orientation from metadata
- `create_picture_in_picture` - Advanced PiP with animations and positioning
- `create_multi_pip` - Multiple overlay support with layout presets
- `create_animated_pip` - Animated PiP with predefined motion presets

### 🎞️ Frame & Time Manipulation (Phase 2A - NEW!)
- `extract_frames` - Extract frames at intervals, keyframes, or scene changes
- `extract_frame_at_time` - Extract single frame at specific timestamp
- `extract_frames_batch` - Batch frame extraction from multiple videos
- `extract_frame_sequence` - Extract specific frame ranges by number
- `extract_thumbnails` - Smart thumbnail generation with multiple methods
- `generate_smart_thumbnails` - AI-powered thumbnail selection
- `create_thumbnail_grid` - Create mosaic grids from thumbnails
- `reverse_video` - Reverse video with memory management for large files
- `reverse_video_section` - Reverse specific sections while keeping rest normal
- `create_boomerang_effect` - Forward-backward looping effect
- `reverse_with_speed_ramp` - Reverse with speed ramping effects

### 🔧 Video Restoration (Phase 2A - NEW!)
- `denoise_video` - Advanced denoising with multiple algorithms (nlmeans, hqdn3d, etc.)
- `denoise_video_advanced` - Automatic noise profiling and grain preservation
- `batch_denoise_videos` - Batch processing for multiple videos

### 📐 Layout & Composition (Phase 2B - NEW!)
- `create_split_screen` - Split-screen layouts with 2-4 videos (horizontal, vertical, quad)
- `create_video_grid` - Mosaic grid layouts with automatic sizing and custom arrangements
- `crop_video` - Intelligent cropping with presets and aspect ratio targeting
- `create_timelapse` - High-quality timelapse with motion interpolation
- `create_slow_motion` - Advanced slow motion with frame interpolation

### ✨ Quality & Enhancement (Phase 2C - NEW!)
- `upscale_video` - AI-enhanced upscaling with multiple algorithms (Lanczos, bicubic, etc.)
- `color_correction` - Professional color grading (auto, warm, cool, vintage, vibrant)
- `auto_enhance_video` - One-click enhancement with multiple quality improvements
- `stabilize_shaky_video` - Advanced stabilization using vidstab and robust algorithms
- `remove_background` - Background removal with chroma key and color range methods
- `batch_enhance_videos` - Batch processing for quality improvements

### 🚀 Advanced Features (Phase 2D - NEW!)
- `create_slideshow` - Professional slideshows with transitions and background music
- `create_gif_from_video` - Optimized GIF creation with palette optimization
- `batch_process_videos` - Parallel batch processing for multiple operations
- `add_motion_blur` - Realistic motion blur effects with directional control
- `create_360_video` - 360-degree video processing with multiple projections
- `create_cinemagraph` - Living photos with selective motion areas

### 🤖 AI Transcription (Phase 3A - NEW!)
- `transcribe_audio_whisper` - AI-powered speech-to-text using OpenAI Whisper (faster-whisper support)
- `transcribe_video_whisper` - Extract and transcribe audio from video with timestamps
- `batch_transcribe_videos` - Batch transcription for multiple videos with concurrent processing
- `create_styled_subtitles` - Generate and burn stylized subtitles from transcriptions

### 👁️ Computer Vision (Phase 3B - NEW!)
- `detect_objects_yolo` - Real-time object detection using YOLOv8 with bounding box visualization
- `generate_smart_thumbnails_ai` - AI-powered thumbnail generation based on visual content analysis
- `auto_crop_to_subject` - Intelligent auto-cropping to focus on detected subjects with smooth tracking

### 📺 YouTube Optimization (Phase 3C - NEW!)
- `detect_scene_changes` - Automatic scene change detection for chapter generation
- `generate_youtube_chapters` - Create YouTube chapters from scene analysis and transcriptions
- `analyze_content_density` - Identify high-action segments and visual complexity patterns
- `extract_youtube_shorts` - Auto-extract engaging Short-form content with AI analysis

## 🚀 Quick Start

### Prerequisites (local installation)

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **FFmpeg** - [Install FFmpeg](https://ffmpeg.org/download.html)
3. **uv** (recommended) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/) or use pip

### Installation

#### Option 1: Using Smithery (Easiest) ⭐

The simplest way to get started is through the [Smithery MCP registry](https://smithery.ai/server/@misbahsy/video-audio-mcp):

![Clipboard-20250524-191433-493](https://github.com/user-attachments/assets/68b9d98c-6e3e-48fe-9337-d16f8e82e0d6)


#### Option 2: Using uv (Recommended for Development)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/misbahsy/video-audio-mcp.git
cd video-audio-mcp

# Install core dependencies with uv
uv sync

# Verify FFmpeg installation
ffmpeg -version
```

#### Option 3: AI Features Installation (Phase 3)

For advanced AI features (transcription, computer vision, YouTube optimization):

```bash
# Install AI dependencies (optional but recommended)
pip install -r requirements-ai.txt

# Or install specific AI packages as needed:
pip install faster-whisper  # For AI transcription (4x faster than openai-whisper)
pip install ultralytics     # For YOLO object detection
pip install opencv-python   # For computer vision features
pip install mediapipe       # For pose/face detection (optional)
```

**Note**: AI features will gracefully fall back with helpful error messages if dependencies are missing. Install only what you need!


### Running the Server

```bash
# With uv (recommended)
uv run server.py

# Or with traditional python
python server.py

# Or with specific transport
python -c "from server import mcp; mcp.run(transport='stdio')"
```

## 🔧 Client Configuration

### Claude Desktop (Recommended Configuration)

Add to your `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "VideoAudioServer": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/video-audio-mcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

**Alternative (using Python directly):**
```json
{
  "mcpServers": {
    "VideoAudioServer": {
      "command": "python",
      "args": ["/path/to/video-audio-mcp/server.py"]
    }
  }
}
```

### Cursor IDE (Recommended Configuration)

1. Open Cursor Settings: `File → Preferences → Cursor Settings → MCP`
2. Click "Add New Server"
3. Configure:
   - **Name**: `VideoAudioServer`
   - **Type**: `command`
   - **Command**: `uv --directory /path/to/your/video-audio-mcp run server.py`

**Alternative configuration:**
   - **Command**: `/path/to/python /path/to/video-audio-mcp/server.py`

### Windsurf

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "VideoAudioServer": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/video-audio-mcp",
        "run",
        "server.py"
      ],
      "env": {}
    }
  }
}
```

### Why Use uv?

The `uv` command is recommended because it:
- **Automatically manages dependencies** without needing to activate virtual environments
- **Faster installation** and dependency resolution
- **Better isolation** - each project gets its own environment automatically
- **More reliable** - handles Python version and dependency conflicts better
- **Modern tooling** - the future of Python package management

### Using NPX (Alternative)

For easier distribution, you can also run via npx if packaged:

```json
{
  "mcpServers": {
    "VideoAudioServer": {
      "command": "npx",
      "args": ["-y", "video-audio-mcp-server"]
    }
  }
}
```

## 📖 Usage Examples

### Basic Video Editing

```
"Can you convert this MP4 file to MOV format?"
→ Uses: convert_video_format

"Trim the video from 30 seconds to 2 minutes"
→ Uses: trim_video

"Extract the audio from this video as MP3"
→ Uses: extract_audio_from_video
```

### Advanced Editing Workflows

```
"Create a highlight reel by concatenating these 3 clips with fade transitions"
→ Uses: concatenate_videos with transition effects

"Add my logo watermark to the top-right corner of this video"
→ Uses: add_image_overlay

"Remove all silent parts from this podcast recording"
→ Uses: remove_silence

"Add subtitles to this video with custom styling"
→ Uses: add_subtitles
```

### 🎨 Enhanced Video Effects Examples

```
"Apply a vintage film look with grain and sepia tones"
→ Uses: apply_video_filters with vintage effect

"Create a smooth liquid transition between these video clips"
→ Uses: apply_video_morphing with liquid effect

"Add animated text that types on screen with a bouncing effect"
→ Uses: create_motion_graphics with animated text

"Remove the green screen and replace with this background video"
→ Uses: apply_chroma_key with advanced lighting

"Create a 3D cube transition between clips"
→ Uses: apply_advanced_transitions with cube effect
```

### 🎵 Enhanced Audio Effects Examples

```
"Add reverb and echo to make the voice sound spacious"
→ Uses: apply_audio_effects with reverb/echo chain

"Mix 4 audio tracks with individual volume and panning controls"
→ Uses: mix_audio_tracks with custom settings

"Create a podcast intro with background music that ducks when I speak"
→ Uses: create_audio_bed with ducking enabled

"Make my voice sound like a robot"
→ Uses: process_voice with robot effect

"Create a 3D audio scene with sounds positioned around the listener"
→ Uses: create_3d_audio_scene with positioned sources
```

### 📊 Audio Visualization Examples

```
"Create a music video with spectrum analyzer visualization"
→ Uses: create_audio_visualization with spectrum type

"Generate a lyric video with particle background effects"
→ Uses: create_lyric_visualization with particles

"Make a podcast visualization with animated waveforms"
→ Uses: create_audio_visualization with waveform type
```

### 🔄 Video Manipulation Examples (Phase 2A)

```
"Rotate this video 90 degrees clockwise and flip it horizontally"
→ Uses: rotate_and_flip_video

"Fix the orientation of this phone video automatically"
→ Uses: auto_rotate_video  

"Create picture-in-picture with the speaker in bottom right corner"
→ Uses: create_picture_in_picture

"Add multiple talking heads in each corner of the screen"
→ Uses: create_multi_pip with corners layout

"Mirror this video vertically to create a reflection effect"
→ Uses: flip_mirror_video with vertical option
```

### 🎞️ Frame & Time Examples (Phase 2A)

```
"Extract one frame every 5 seconds from this video"
→ Uses: extract_frames with interval mode

"Generate 10 smart thumbnails showing the best moments"
→ Uses: generate_smart_thumbnails with scene analysis

"Create a thumbnail grid showing video highlights"
→ Uses: create_thumbnail_grid from extracted thumbnails

"Reverse this video to create a rewind effect"
→ Uses: reverse_video

"Make a boomerang loop that plays forward then backward 3 times"
→ Uses: create_boomerang_effect

"Extract frames 100-200 as individual images"
→ Uses: extract_frame_sequence
```

### 🔧 Video Restoration Examples (Phase 2A)

```
"Remove noise from this old film footage while preserving grain"
→ Uses: denoise_video_advanced with film_grain profile

"Clean up digital camera noise from this low-light video"
→ Uses: denoise_video with nlmeans method

"Batch process these 50 videos to remove compression artifacts"
→ Uses: batch_denoise_videos with compression_artifacts profile
```

### 📐 Layout & Composition Examples (Phase 2B)

```
"Create a split-screen comparison with these two videos side by side"
→ Uses: create_split_screen with horizontal layout

"Make a 2x2 grid showing all four camera angles simultaneously"
→ Uses: create_video_grid with quad layout

"Crop this video to focus on the center subject in a square format"
→ Uses: crop_video with center_square preset

"Create a 10x speed timelapse of this construction footage"
→ Uses: create_timelapse with speed_factor=10

"Make slow motion of this action sequence at quarter speed"
→ Uses: create_slow_motion with slow_factor=4 and optical flow interpolation
```

### ✨ Quality & Enhancement Examples (Phase 2C)

```
"Upscale this 720p video to 4K resolution with AI enhancement"
→ Uses: upscale_video with target_resolution="3840x2160" and enhance_quality=True

"Apply warm color grading to give this video a cozy feeling"
→ Uses: color_correction with correction_type="warm"

"Automatically enhance this video quality - it looks dull and shaky"
→ Uses: auto_enhance_video with enhancement_level="medium" and stabilize=True

"Fix the camera shake in this handheld footage"
→ Uses: stabilize_shaky_video with vidstab method

"Remove the green screen and replace with this beach background"
→ Uses: remove_background with method="chroma" and replacement_background

"Enhance all videos in this folder with consistent settings"
→ Uses: batch_enhance_videos with custom enhancement settings
```

### 🚀 Advanced Features Examples (Phase 2D)

```
"Create a slideshow from these vacation photos with fade transitions"
→ Uses: create_slideshow with transition_type="fade" and background music

"Convert this 10-second video clip into an optimized GIF"
→ Uses: create_gif_from_video with palette optimization

"Process all videos in this directory to convert them to WebM format"
→ Uses: batch_process_videos with operation="convert" and format="webm"

"Add motion blur to simulate fast camera movement in this action scene"
→ Uses: add_motion_blur with blur_amount=3.0 and motion_detection=True

"Convert this 360 camera footage to proper equirectangular format"
→ Uses: create_360_video with input_format="dual_fisheye"

"Create a cinemagraph where only the waterfall moves"
→ Uses: create_cinemagraph with motion_area focused on waterfall region
```

### 🤖 AI Transcription Examples (Phase 3A)

```
"Transcribe this podcast episode and generate SRT subtitles"
→ Uses: transcribe_video_whisper with output_format="srt"

"Generate captions for my YouTube video in multiple languages"
→ Uses: transcribe_audio_whisper with language="auto" for detection, then translate

"Batch transcribe all videos in my course directory"
→ Uses: batch_transcribe_videos with JSON output for timestamps

"Create styled subtitles and burn them into the video"
→ Uses: create_styled_subtitles with custom font, color, and positioning
```

### 👁️ Computer Vision Examples (Phase 3B)

```
"Detect all people and objects in this video and draw bounding boxes"
→ Uses: detect_objects_yolo with draw_boxes=True and target_classes=["person"]

"Generate 5 smart thumbnails from my video showing the most interesting moments"
→ Uses: generate_smart_thumbnails_ai with focus_on_objects=True

"Auto-crop this video to always keep the speaker in frame"
→ Uses: auto_crop_to_subject with target_class="person" and smooth_tracking=True

"Find all the cars in this traffic video and export detection data"
→ Uses: detect_objects_yolo with target_classes=["car"] and output_json path
```

### 📺 YouTube Optimization Examples (Phase 3C)

```
"Analyze this video and automatically generate YouTube chapters"
→ Uses: detect_scene_changes + generate_youtube_chapters with transcription integration

"Find the most engaging 60-second clips for YouTube Shorts"
→ Uses: extract_youtube_shorts with use_content_analysis=True

"Analyze which parts of my video have the most action for highlights"
→ Uses: analyze_content_density with detailed motion and complexity scoring

"Create chapters based on my video's transcription and scene changes"
→ Uses: generate_youtube_chapters with both scene_data and transcription_path
```

### 🔗 Integrated Workflow Examples (YouTube Creator Pipeline)

```
"Complete YouTube workflow: transcribe, generate chapters, create Shorts, and thumbnails"
→ Uses: transcribe_video_whisper → generate_youtube_chapters → extract_youtube_shorts → generate_smart_thumbnails_ai

"Optimize my video for accessibility: add subtitles and chapters"
→ Uses: transcribe_video_whisper → create_styled_subtitles → generate_youtube_chapters

"Content analysis pipeline: detect objects, analyze density, extract highlights"
→ Uses: detect_objects_yolo → analyze_content_density → extract_youtube_shorts
```

### Professional Workflows

```
"Convert this 4K video to 1080p, reduce bitrate to 2Mbps, and change to H.265 codec"
→ Uses: convert_video_properties

"Create a social media version: change to 9:16 aspect ratio, add text overlay, and compress"
→ Uses: change_aspect_ratio, add_text_overlay, set_video_bitrate

"Insert B-roll footage at 30 seconds with a fade transition"
→ Uses: add_b_roll
```

## 🎯 Real-World Use Cases

### Content Creation
- **YouTube Videos**: Automated editing, thumbnail generation, format optimization
- **Social Media**: Aspect ratio conversion, text overlays, compression for platforms
- **Podcasts**: Audio extraction, silence removal, format conversion

### Professional Video Production
- **Corporate Videos**: Logo watermarking, subtitle addition, quality standardization
- **Educational Content**: Screen recording processing, chapter markers, accessibility features
- **Marketing Materials**: B-roll integration, transition effects, brand consistency

### Workflow Automation
- **Batch Processing**: Convert entire video libraries to new formats
- **Quality Control**: Standardize video properties across projects
- **Archive Management**: Extract audio for transcription, create preview clips

## 🔍 Tool Reference

### Video Format Conversion

```python
# Convert MP4 to MOV with specific properties
convert_video_properties(
    input_video_path="input.mp4",
    output_video_path="output.mov",
    target_format="mov",
    resolution="1920x1080",
    video_codec="libx264",
    video_bitrate="5M",
    frame_rate=30
)
```

### Text Overlays with Timing

```python
# Add multiple text overlays with different timings
add_text_overlay(
    video_path="input.mp4",
    output_video_path="output.mp4",
    text_elements=[
        {
            "text": "Welcome to our presentation",
            "start_time": "0",
            "end_time": "3",
            "font_size": 48,
            "font_color": "white",
            "x_pos": "center",
            "y_pos": "center"
        },
        {
            "text": "Chapter 1: Introduction",
            "start_time": "5",
            "end_time": "8",
            "font_size": 36,
            "box": True,
            "box_color": "black@0.7"
        }
    ]
)
```

### Advanced Concatenation

```python
# Join videos with crossfade transition
concatenate_videos(
    video_paths=["clip1.mp4", "clip2.mp4"],
    output_video_path="final.mp4",
    transition_effect="dissolve",
    transition_duration=1.5
)
```

## 🛡️ Error Handling

The server includes comprehensive error handling:

- **File Validation**: Checks for file existence before processing
- **Format Support**: Validates supported formats and codecs
- **Graceful Fallbacks**: Attempts codec copying before re-encoding
- **Detailed Logging**: Provides clear error messages for troubleshooting

## 🔧 Troubleshooting

### Common Issues

**FFmpeg not found**
```bash
# Install FFmpeg
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
# Windows: Download from https://ffmpeg.org/
```

**Permission errors**
```bash
# Ensure file permissions
chmod +x server.py
```

**MCP server not connecting**
1. Check file paths in configuration
2. Verify Python environment
3. Test server manually: `python server.py`
4. Check client logs for detailed errors

### Debug Mode

Run with debug logging:
```bash
python server.py --log-level DEBUG
```

## 🧪 Testing

This project includes a comprehensive test suite that validates all video and audio editing functions. The tests ensure reliability and help catch regressions during development.

### Test Coverage

The test suite covers:

- **✅ Core Functions**: All 104 video/audio editing and AI tools
- **🎬 Video Operations**: Format conversion, trimming, resolution changes, codec switching
- **🎵 Audio Processing**: Bitrate adjustment, sample rate changes, channel configuration
- **🎨 Creative Tools**: Text overlays, image watermarks, subtitle burning
- **🔗 Advanced Features**: Video concatenation, B-roll insertion, transitions
- **⚡ Performance**: Speed changes, silence removal, aspect ratio adjustments
- **🛡️ Error Handling**: Invalid inputs, missing files, unsupported formats

### Running Tests

#### Prerequisites for Testing

```bash
# Install test dependencies
pip install pytest

# Ensure FFmpeg is installed and accessible
ffmpeg -version
```

#### Basic Test Execution

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_video_functions.py

# Run specific test function
pytest tests/test_video_functions.py::test_extract_audio
```

#### Advanced Test Options

```bash
# Run tests with detailed output and no capture
pytest tests/ -v -s

# Run tests and stop on first failure
pytest tests/ -x

# Run tests with coverage report
pytest tests/ --cov=server

# Run only failed tests from last run
pytest tests/ --lf
```

### Test Environment Setup

The test suite automatically creates:

- **Sample Files**: Test videos, audio files, and images
- **Output Directory**: `tests/test_outputs/` for generated files
- **Temporary Files**: B-roll clips and transition test materials

```bash
# Test files are created in:
tests/
├── test_outputs/          # Generated test results
├── sample_files/          # Auto-generated sample media
├── test_video_functions.py # Main test suite
└── sample.mp4            # Primary test video (if available)
```

### Sample Test Output

```bash
$ pytest tests/test_video_functions.py -v

tests/test_video_functions.py::test_health_check PASSED
tests/test_video_functions.py::test_extract_audio PASSED
tests/test_video_functions.py::test_trim_video PASSED
tests/test_video_functions.py::test_convert_audio_properties PASSED
tests/test_video_functions.py::test_convert_video_properties PASSED
tests/test_video_functions.py::test_add_text_overlay PASSED
tests/test_video_functions.py::test_add_subtitles PASSED
tests/test_video_functions.py::test_concatenate_videos PASSED
tests/test_video_functions.py::test_add_b_roll PASSED
tests/test_video_functions.py::test_add_basic_transitions PASSED
tests/test_video_functions.py::test_concatenate_videos_with_xfade PASSED

========================= 25 passed in 45.2s =========================
```

### Test Categories

#### 🎯 **Core Functionality Tests**
- Video format conversion and property changes
- Audio extraction and processing
- File trimming and basic operations

#### 🎨 **Creative Feature Tests**
- Text overlay positioning and timing
- Image watermark placement and opacity
- Subtitle burning with custom styling

#### 🔗 **Advanced Editing Tests**
- Multi-video concatenation with transitions
- B-roll insertion with various positions
- Speed changes and silence removal

#### 🛡️ **Error Handling Tests**
- Invalid file paths and missing files
- Unsupported formats and codecs
- Edge cases and boundary conditions

### Writing Custom Tests

To add new tests for additional functionality:

```python
def test_new_feature():
    """Test description"""
    # Setup
    input_file = "path/to/test/file.mp4"
    output_file = os.path.join(OUTPUT_DIR, "test_output.mp4")
    
    # Execute
    result = your_new_function(input_file, output_file, parameters)
    
    # Validate
    assert "success" in result.lower()
    assert os.path.exists(output_file)
    
    # Optional: Validate output properties
    duration = get_media_duration(output_file)
    assert duration > 0
```

### Continuous Integration

The test suite is designed to work in CI/CD environments:

```yaml
# Example GitHub Actions workflow
- name: Install FFmpeg
  run: sudo apt-get install ffmpeg

- name: Install dependencies
  run: pip install -r requirements.txt pytest

- name: Run tests
  run: pytest tests/ -v
```

### Performance Testing

Some tests include performance validation:

- **Duration Checks**: Verify output video lengths match expectations
- **Quality Validation**: Ensure format conversions maintain quality
- **File Size Monitoring**: Check compression and bitrate changes

### Test Data Management

- **Automatic Cleanup**: Tests clean up temporary files
- **Sample Generation**: Creates test media files as needed
- **Deterministic Results**: Tests produce consistent, reproducible results

> **💡 Tip**: Run tests after any changes to ensure functionality remains intact. The comprehensive test suite catches most issues before they reach production.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/misbahsy/video-audio-mcp.git
cd video-audio-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) framework
- Powered by [FFmpeg](https://ffmpeg.org/) for media processing
- Inspired by the [Model Context Protocol](https://modelcontextprotocol.io/) specification

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/misbahsy/video-audio-mcp/issues)


---

**Made with ❤️ for the MCP community**
