# Security policy

## Reporting a vulnerability

Please report security issues privately with **Report a vulnerability** on this repository's **Security** tab. Don't open a public issue.

Include what you found, how to reproduce it and what an attacker could do with it. Don't include real credentials, private video or personal data. We'll acknowledge the report within three business days and keep you updated until it's resolved.

We support the latest commit on `main`.

## What the tools do

These skills send no telemetry. Network use is limited to the following:

- **Hooks** (`analyze.py`, `readability.py`) runs on your machine. It reads the video you point it at through ffmpeg and ffprobe, and writes a report to the output folder. The optional `faster-whisper` transcription may download its model the first time you use it.
- **Topics** (`scout.py`) reads public sources: YouTube through `yt-dlp`, Google Trends and Wikipedia. Those services see the searches and links you give it. It needs no account or API key.

## What to watch for

- **Videos are untrusted input.** They are decoded by your ffmpeg, so keep it up to date.
- **Agents read what the tools collect.** Transcripts, on-screen text and YouTube comments are data for the agent to weigh, and they should never be followed as instructions.

Reports about these are especially useful: command injection through a file name or caption, writing outside the output folder, and skill text that could lead an agent to act on instructions found in a video or a comment.
