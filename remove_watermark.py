"""
Remove Watermark Tool - Gemini Notebook Logo Remover
=====================================================
Trims the last 3.1 seconds from video files to remove
the Gemini Notebook watermark/logo that appears at the end.

Usage:
  - Drag and drop video files or folders onto the .bat launcher
  - Or run: python remove_watermark.py <file_or_folder> [file_or_folder ...]
  
Output is saved to an 'output' subfolder, preserving directory structure.
"""

import subprocess
import sys
import os
import io
import json
from pathlib import Path
from datetime import datetime

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    os.system("")  # Enable ANSI escape codes on Windows

# ============================================================
# CONFIGURATION
# ============================================================
TRIM_SECONDS = 3.1          # Seconds to cut from the end
OUTPUT_FOLDER = "output"    # Output subfolder name
VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov", ".webm",
    ".flv", ".wmv", ".m4v", ".ts", ".mts"
}

# ============================================================
# COLORS FOR CONSOLE OUTPUT
# ============================================================
class Colors:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"


def print_banner():
    """Print a styled banner."""
    print(f"""
{Colors.CYAN}{Colors.BOLD}+==================================================+
|         Remove Watermark Tool                    |
|     Gemini Notebook Logo Remover (3.1s trim)     |
+==================================================+{Colors.RESET}
""")


def get_video_duration(filepath: str) -> float:
    """Get the duration of a video file in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                str(filepath)
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except Exception as e:
        print(f"  {Colors.RED}[X] Error reading duration: {e}{Colors.RESET}")
        return -1


def trim_video(input_path: str, output_path: str, trim_seconds: float) -> bool:
    """
    Trim the last `trim_seconds` from a video file.
    Uses stream copy (no re-encoding) for maximum speed and quality.
    """
    duration = get_video_duration(input_path)
    if duration <= 0:
        print(f"  {Colors.RED}[X] Could not determine video duration.{Colors.RESET}")
        return False

    if duration <= trim_seconds:
        print(f"  {Colors.RED}[X] Video is too short ({duration:.1f}s <= {trim_seconds}s). Skipping.{Colors.RESET}")
        return False

    new_duration = duration - trim_seconds

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"  {Colors.BLUE}Original: {duration:.2f}s -> Trimmed: {new_duration:.2f}s (cutting {trim_seconds}s){Colors.RESET}")

    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",                          # Overwrite output
                "-i", str(input_path),         # Input file
                "-t", str(new_duration),       # Duration to keep
                "-c", "copy",                  # Stream copy (no re-encoding)
                "-avoid_negative_ts", "make_zero",
                str(output_path)
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )

        if result.returncode == 0 and os.path.exists(output_path):
            input_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            print(f"  {Colors.GREEN}[OK] Saved: {output_path}{Colors.RESET}")
            print(f"  {Colors.CYAN}  Size: {input_size / 1024 / 1024:.1f} MB -> {output_size / 1024 / 1024:.1f} MB{Colors.RESET}")
            return True
        else:
            error_msg = result.stderr.strip().split("\n")[-1] if result.stderr else "Unknown error"
            print(f"  {Colors.RED}[X] FFmpeg error: {error_msg}{Colors.RESET}")
            return False

    except FileNotFoundError:
        print(f"  {Colors.RED}[X] FFmpeg not found! Make sure ffmpeg is installed and in PATH.{Colors.RESET}")
        return False
    except Exception as e:
        print(f"  {Colors.RED}[X] Error: {e}{Colors.RESET}")
        return False


def collect_videos(paths: list[str]) -> list[tuple[str, str]]:
    """
    Collect all video files from the given paths (files and/or directories).
    Returns list of (input_path, output_path) tuples.
    """
    videos = []

    for path_str in paths:
        path = Path(path_str.strip().strip('"'))

        if path.is_file():
            if path.suffix.lower() in VIDEO_EXTENSIONS:
                # Output goes to 'output' subfolder relative to the file's parent
                output_dir = path.parent / OUTPUT_FOLDER
                output_path = output_dir / path.name
                videos.append((str(path), str(output_path)))
            else:
                print(f"{Colors.YELLOW}[!] Skipping non-video file: {path.name}{Colors.RESET}")

        elif path.is_dir():
            # Recursively find all video files
            base_dir = path
            for root, dirs, files in os.walk(base_dir):
                for file in sorted(files):
                    filepath = Path(root) / file
                    if filepath.suffix.lower() in VIDEO_EXTENSIONS:
                        # Preserve relative directory structure in output
                        rel_path = filepath.relative_to(base_dir)
                        output_path = base_dir / OUTPUT_FOLDER / rel_path
                        videos.append((str(filepath), str(output_path)))
        else:
            print(f"{Colors.RED}[X] Path not found: {path_str}{Colors.RESET}")

    return videos


def main():
    print_banner()

    # Get input paths from command line arguments
    if len(sys.argv) < 2:
        print(f"{Colors.YELLOW}Usage: Drag and drop video files or folders onto the .bat launcher{Colors.RESET}")
        print(f"{Colors.YELLOW}   Or: python remove_watermark.py <file_or_folder> [file_or_folder ...]{Colors.RESET}")
        print()
        input(f"{Colors.CYAN}Press Enter to exit...{Colors.RESET}")
        sys.exit(1)

    paths = sys.argv[1:]

    # Collect all video files
    print(f"{Colors.BOLD}Scanning for videos...{Colors.RESET}")
    videos = collect_videos(paths)

    if not videos:
        print(f"\n{Colors.YELLOW}[!] No video files found!{Colors.RESET}")
        print(f"  Supported formats: {', '.join(sorted(VIDEO_EXTENSIONS))}")
        input(f"\n{Colors.CYAN}Press Enter to exit...{Colors.RESET}")
        sys.exit(0)

    print(f"{Colors.GREEN}   Found {len(videos)} video(s) to process{Colors.RESET}\n")

    # Process each video
    success_count = 0
    fail_count = 0
    start_time = datetime.now()

    for i, (input_path, output_path) in enumerate(videos, 1):
        filename = os.path.basename(input_path)
        print(f"{Colors.BOLD}[{i}/{len(videos)}] {Colors.MAGENTA}{filename}{Colors.RESET}")

        if trim_video(input_path, output_path, TRIM_SECONDS):
            success_count += 1
        else:
            fail_count += 1
        print()

    # Summary
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"{Colors.CYAN}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD} Summary:{Colors.RESET}")
    print(f"   {Colors.GREEN}[OK] Success: {success_count}{Colors.RESET}")
    if fail_count > 0:
        print(f"   {Colors.RED}[X]  Failed:  {fail_count}{Colors.RESET}")
    print(f"   {Colors.BLUE}Time: {elapsed:.1f}s{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 50}{Colors.RESET}")
    print()
    input(f"{Colors.CYAN}Press Enter to exit...{Colors.RESET}")


if __name__ == "__main__":
    main()
