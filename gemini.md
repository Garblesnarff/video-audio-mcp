# Gemini Project Context: Video & Audio Editing MCP Server

## 1. Project Purpose & Goal

This project is a Model Context Protocol (MCP) server designed to provide a comprehensive suite of video and audio editing capabilities to an AI assistant. It leverages the power of FFmpeg to perform a wide range of operations, from basic trimming and format conversion to more advanced tasks like adding overlays, transitions, and inserting B-roll footage.

The primary goal is to enable an AI assistant to understand and execute complex, multi-step video and audio editing commands given in natural language.

## 2. Tech Stack

- **Core Language**: Python (>=3.8)
- **Media Processing**: `ffmpeg` (via the `ffmpeg-python` wrapper)
- **Server Framework**: `mcp` (specifically `FastMCP`)
- **Package Management**: `uv` is recommended, but `pip` with `pyproject.toml` and `requirements.txt` is also supported.
- **Testing**: `pytest`

## 3. Key Files & Structure (Modularized)

The project now follows a highly modular structure, with each tool function residing in its own dedicated file within categorized subdirectories. This design optimizes for clarity and ease of navigation, especially for AI models.

- `server.py`: The main entry point of the application. It initializes the `FastMCP` server and dynamically registers all tool functions imported from the `mcp_tools` package.
- `mcp_tools/`: This directory contains all the tool functions, organized into subdirectories by category.
  - `mcp_tools/__init__.py`: This file acts as the central aggregator, importing every individual tool function from its respective file and exposing them via the `ALL_TOOLS` list.
  - `mcp_tools/utils.py`: Contains shared helper functions used across multiple tools (e.g., media probing, time parsing, ffmpeg fallback execution).
  - `mcp_tools/audio_processing/`: Contains individual files for each audio-related tool.
    - `extract_audio_from_video.py`
    - `convert_audio_properties.py`
    - `convert_audio_format.py`
    - `set_audio_bitrate.py`
    - `set_audio_sample_rate.py`
    - `set_audio_channels.py`
    - `set_video_audio_track_codec.py`
    - `set_video_audio_track_bitrate.py`
    - `set_video_audio_track_sample_rate.py`
    - `set_video_audio_track_channels.py`
    - `remove_silence.py`
    - `generate_audio_waveform.py` (New Feature)
    - `normalize_audio.py` (New Feature)
  - `mcp_tools/video_processing/`: Contains individual files for each video-related tool.
    - `convert_video_properties.py`
    - `change_aspect_ratio.py`
    - `convert_video_format.py`
    - `set_video_resolution.py`
    - `set_video_codec.py`
    - `set_video_bitrate.py`
    - `set_video_frame_rate.py`
    - `correct_colors.py` (New Feature)
    - `stabilize_video.py` (New Feature)
  - `mcp_tools/editing/`: Contains individual files for video editing and composition tools.
    - `trim_video.py`
    - `create_video_from_images.py`
    - `concatenate_videos.py`
    - `change_video_speed.py`
    - `add_b_roll.py`
    - `add_basic_transitions.py`
    - `split_video_by_scenes.py` (New Feature)
  - `mcp_tools/overlays/`: Contains individual files for overlay-related tools.
    - `add_subtitles.py`
    - `add_text_overlay.py`
    - `add_image_overlay.py`
- `README.md`: Provides extensive documentation, including a full list of tools, setup instructions for various clients (Claude Desktop, Cursor), and usage examples.
- `pyproject.toml`: The primary file for managing project dependencies.
- `requirements.txt`: A secondary dependency file, mainly for reference.
- `tests/`: Contains the test suite.
  - `test_video_functions.py`: The main test file, containing tests for many of the editing tools.
  - `sample_files/`: Contains sample media used for testing.

## 4. Conventions & Patterns

- **Tool Definition**: Each tool function is defined in its own Python file and is designed to be registered with the `FastMCP` server.
- **Docstrings**: Every tool has a detailed docstring explaining its purpose, arguments, and return values. These docstrings are critical for AI assistant understanding and tool usage.
- **Error Handling**: Tools include robust `try...except` blocks to catch `ffmpeg.Error` and other exceptions, returning informative error messages.
- **Efficiency Fallbacks**: Where applicable, tools attempt to perform operations by copying codecs (`c='copy'`) for speed. If this fails, they fall back to re-encoding the media.
- **Modular Imports**: Functions import only what they need from `ffmpeg` and local `mcp_tools.utils` helpers, promoting clear dependencies.
- **Testing**: The project uses `pytest` for testing. Tests are located in the `tests/` directory and are designed to be run from the project root.

## 5. New Features Implemented

In addition to the existing capabilities, the following new features have been added:

- **`normalize_audio`**: Automatically adjusts audio to a target loudness level (EBU R128) using a two-pass `loudnorm` process, ensuring consistent audio levels.
- **`stabilize_video`**: Reduces camera shake and motion blur in videos using FFmpeg's `vidstabdetect` and `vidstabtransform` filters.
- **`split_video_by_scenes`**: Automatically detects scene changes in a video and splits it into separate clips, useful for content segmentation.
- **`correct_colors`**: Allows adjustment of video brightness, contrast, saturation, and gamma for improved visual quality.
- **`generate_audio_waveform`**: Creates a visual image representation of an audio file's waveform, useful for quick audio analysis or visual elements.

## 6. How to Run & Test

**To Run the Server:**

```bash
# Using uv (recommended)
uv run server.py

# Using Python
python server.py
```

**To Run Tests:**

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/
```
