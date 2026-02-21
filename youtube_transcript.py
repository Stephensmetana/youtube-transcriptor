#!/usr/bin/env python3
"""
YouTube Transcript Downloader
Usage: python youtube_transcript.py <youtube_url> [--output <filename>]

Dependencies: pip install youtube-transcript-api
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

try:
    from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
except ImportError:
    print("Missing dependency. Install it with:\n  pip install youtube-transcript-api")
    sys.exit(1)


def extract_video_id(url: str) -> str:
    """Extract the YouTube video ID from various URL formats."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?]|$)",  # Standard and shortened URLs
        r"youtu\.be\/([0-9A-Za-z_-]{11})",            # youtu.be short URLs
        r"embed\/([0-9A-Za-z_-]{11})",                 # Embed URLs
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract a valid YouTube video ID from: {url}")


# English language codes to try first (manual then auto-generated)
_ENGLISH_CODES = ["en", "en-US", "en-GB", "en-CA", "en-AU", "en-IE", "en-IN"]


def fetch_video_title(video_id: str) -> str:
    """Fetch the video title from the YouTube watch page."""
    if requests is None:
        return video_id
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        # Try <title> tag first: "Video Title - YouTube"
        m = re.search(r"<title>(.+?) - YouTube</title>", resp.text)
        if m:
            return m.group(1)
        # Fallback: look for "title" in ytInitialData JSON
        m = re.search(r'"title":\s*{\s*"runs":\s*\[\s*{\s*"text":\s*"([^"]+)"', resp.text)
        if m:
            return m.group(1)
    except Exception:
        pass
    return video_id


def sanitize_filename(title: str) -> str:
    """Replace whitespace with underscores and strip characters invalid in filenames.

    Non-ASCII characters are first transliterated to their closest ASCII
    equivalent (e.g. François → Francois) so filenames stay pure ASCII and
    never cause JSON encoding issues when used in editor tool calls.
    """
    # Decode common HTML entities
    title = title.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
    # Transliterate Unicode → ASCII (François → Francois, etc.)
    title = unicodedata.normalize("NFKD", title)
    title = title.encode("ascii", "ignore").decode("ascii")
    # Replace whitespace runs with a single underscore
    title = re.sub(r"\s+", "_", title)
    # Remove characters that are not alphanumeric, underscore, hyphen, or dot
    title = re.sub(r"[^\w\-_.]", "", title)
    # Collapse multiple underscores
    title = re.sub(r"_+", "_", title)
    return title.strip("_") or "transcript"


def _pick_transcript(transcript_list, preferred_languages):
    """Choose the best transcript from a TranscriptList."""
    all_codes = [t.language_code for t in transcript_list]

    # 1. Try caller-specified preferences
    if preferred_languages:
        try:
            return transcript_list.find_transcript(preferred_languages)
        except NoTranscriptFound:
            pass

    # 2. Try English (manual first, then auto-generated)
    try:
        return transcript_list.find_manually_created_transcript(_ENGLISH_CODES)
    except NoTranscriptFound:
        pass
    try:
        return transcript_list.find_generated_transcript(_ENGLISH_CODES)
    except NoTranscriptFound:
        pass

    # 3. Fall back to any available transcript (manual preferred)
    try:
        return transcript_list.find_manually_created_transcript(all_codes)
    except NoTranscriptFound:
        pass
    try:
        return transcript_list.find_generated_transcript(all_codes)
    except NoTranscriptFound:
        pass

    return next(iter(transcript_list))


def fetch_transcript(video_id: str, languages: list[str] = None):
    """
    Fetch the transcript for a YouTube video.
    Returns (transcript_entries, language_name, language_code).
    """
    # Try several API shapes to support different installed versions.
    # 1) Class method `list_transcripts` (newer API)
    list_transcripts_fn = getattr(YouTubeTranscriptApi, "list_transcripts", None)
    if callable(list_transcripts_fn):
        transcript_list = list_transcripts_fn(video_id)
        transcript = _pick_transcript(transcript_list, languages)
        entries = transcript.fetch()
        return entries, getattr(transcript, "language", "unknown"), getattr(transcript, "language_code", "unknown")

    # 2) Instance methods `list` / `fetch` (older API variant present in some installs)
    try:
        api = YouTubeTranscriptApi()
    except Exception:
        api = None

    if api is not None and hasattr(api, "list"):
        transcript_list = api.list(video_id)
        transcript = _pick_transcript(transcript_list, languages)
        entries = transcript.fetch()
        return entries, getattr(transcript, "language", "unknown"), getattr(transcript, "language_code", "unknown")

    # 3) Final fallback: some installs expose a convenience `fetch` function on an instance
    if api is not None and hasattr(api, "fetch"):
        try:
            if languages:
                fetched = api.fetch(video_id, languages=languages)
                lang_code = languages[0] if isinstance(languages, (list, tuple)) and languages else "unknown"
            else:
                fetched = api.fetch(video_id)
                lang_code = "unknown"
            entries = list(fetched)
            return entries, lang_code, lang_code
        except (NoTranscriptFound, TranscriptsDisabled):
            raise

    # If none of the above methods are available, raise a clear error
    raise RuntimeError("Installed youtube-transcript-api package has an unsupported API shape")


def format_transcript(entries, include_timestamps: bool = True) -> str:
    """Format transcript entries into a readable text block.

    Supports both dict-style entries (older API) and dataclass-style
    FetchedTranscriptSnippet entries (youtube-transcript-api >= 1.x).
    """
    lines = []
    for entry in entries:
        # Support both dict and attribute-based entries
        if hasattr(entry, "text"):
            text = entry.text.strip()
            start = entry.start
        else:
            text = entry["text"].strip()
            start = entry["start"]
        if not text:
            continue
        if include_timestamps:
            minutes = int(start // 60)
            seconds = int(start % 60)
            lines.append(f"[{minutes:02d}:{seconds:02d}] {text}")
        else:
            lines.append(text)
    return "\n".join(lines)


def save_transcript(content: str, output_path: Path) -> None:
    # Ensure parent directory exists (supports custom paths and default `transcripts/` dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(f"Transcript saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Download a YouTube video transcript to a text file."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: <video_id>_transcript.txt)",
        default=None,
    )
    parser.add_argument(
        "--no-timestamps",
        action="store_true",
        help="Omit timestamps from the output",
    )
    parser.add_argument(
        "--language", "-l",
        nargs="+",
        help="Preferred language code(s) for the transcript, e.g. --language en es",
        default=None,
    )
    args = parser.parse_args()

    # Extract video ID
    try:
        video_id = extract_video_id(args.url)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Fetching transcript for video ID: {video_id}")

    # Fetch transcript
    try:
        entries, language, language_code = fetch_transcript(video_id, args.language)
    except TranscriptsDisabled:
        print("Error: Transcripts are disabled for this video.")
        sys.exit(1)
    except NoTranscriptFound:
        print("Error: No transcript found for this video.")
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        sys.exit(1)

    print(f"Found transcript in: {language} ({len(entries)} segments)")

    # Format transcript
    content = format_transcript(entries, include_timestamps=not args.no_timestamps)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Fetch and sanitize the video title for the filename
        print("Fetching video title...")
        raw_title = fetch_video_title(video_id)
        safe_title = sanitize_filename(raw_title)
        # Determine if the transcript is English
        is_english = language_code.split("-")[0].lower() == "en"
        # Save default transcripts into the `transcripts/` folder when no output is provided
        transcripts_dir = Path("transcripts")
        transcripts_dir.mkdir(parents=True, exist_ok=True)
        if is_english:
            output_path = transcripts_dir / f"{safe_title}.txt"
        else:
            output_path = transcripts_dir / f"{safe_title}_{language_code}.txt"

    # Save to file
    save_transcript(content, output_path)
    print(f"Done! ({len(content.splitlines())} lines)")


if __name__ == "__main__":
    main()
