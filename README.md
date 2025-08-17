<div align="center">
  <img src="icon.svg" alt="Video & Audio Editing MCP Server" width="128" height="128">
</div>

# 🎬 Video & Audio Editing MCP Server

A comprehensive Model Context Protocol (MCP) server that provides powerful video and audio editing capabilities through FFmpeg. This server enables AI assistants to perform professional-grade video editing operations including format conversion, trimming, overlays, transitions, and advanced audio processing.

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

# Install dependencies with uv
uv sync

# Verify FFmpeg installation
ffmpeg -version
```


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

- **✅ Core Functions**: All 30+ video/audio editing tools
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
