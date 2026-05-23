
import subprocess
from pathlib import Path
df

def cut_windows(src_url_or_path, windows: list[tuple[str, str, str]], work_dir: Path, label_prefix: str = "manual") -> list[Path]:
    """
    Cuts multiple clip segments from a video source (URL or local file) using specified time windows.

    - If `src_url_or_path` is a URL, it uses yt-dlp to download the specified sections.
    - If `src_url_or_path` is a local file, it uses ffmpeg to cut the sections.

    windows: list of tuples in the form [(start_time, end_time, label), ...]
    Returns a list of Paths to the cut clips.
    """
    output_paths = []

    for index, (start, end, label) in enumerate(windows, start=1):
        # Define output file name and sidecar text
        slug = f"{label_prefix}_{index}_{label.replace(' ', '_')}"
        output_video_path = work_dir / f"resources/clips/{slug}.mp4"
        sidecar_path = work_dir / f"resources/clips/{slug}.source.txt"

        # Check if the source is a URL or a local path
        if src_url_or_path.startswith("http"):
            # Using yt-dlp to download and cut sections
            command = [
                "yt-dlp", src_url_or_path,
                "--download-sections", f"*{start}-{end}",
                "--output", str(output_video_path),
                "--force-keyframes-at-cuts"
            ]
        else:
            # Using ffmpeg for local files
            command = [
                "ffmpeg", "-i", src_url_or_path,
                "-ss", start, "-to", end,
                "-c:v", "libx264", "-c:a", "aac",
                "-movflags", "+faststart",
                str(output_video_path)
            ]

        # Execute the command
        subprocess.run(command, check=True)

        # Check if clip was created and meets size requirement
        if output_video_path.exists() and output_video_path.stat().st_size > 50 * 1024:  # More than 50 KB
            output_paths.append(output_video_path)

            # Write sidecar info
            with open(sidecar_path, "w") as f:
                f.write(
                    f"tier=manual\nurl={src_url_or_path}\nstart={start}\n"
                    f"end={end}\nlabel={label}\nfetched_at={datetime.now().isoformat()}\n"
                    f"license=user_specified\n"
                )

    return output_paths
