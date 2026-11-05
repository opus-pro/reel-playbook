# Contributing to Reel Playbook

Thanks for helping out. A good change here makes the advice more accurate or the tools more reliable.

## What helps most

- **Calibration data:** a flag that fired wrongly, or a problem it missed, with the clip if you can share it.
- **Platform safe-zone updates:** where the app's buttons and captions sit now.
- **Language support** beyond English.
- **Bug reports** with your ffmpeg version, Python version, operating system, the exact command and the error.

For a security problem, follow [SECURITY.md](SECURITY.md) instead of opening an issue.

## Getting set up

You need ffmpeg and ffprobe 6.0 or newer, and Python 3.9 or newer. Then run both test suites:

```bash
python tests/hooks/test_analyze.py
python tests/topics/test_scout.py
```

The Hooks test builds a 36-second video with defects planted at known times, then checks that the analyzer finds each one at the right time. It writes to `tests/out/`, which git ignores.

## Before you open a pull request

- **Keep it small.** One change per pull request.
- **Stay on the standard library.** Video review must work with Python and ffmpeg alone. `faster-whisper` and `yt-dlp` stay optional.
- **Don't rely on one ffmpeg build.** Filters differ between builds. Stock Homebrew ffmpeg has no `drawtext`, for example.
- **Test what you change.** If you add or change a flag, plant that defect in `tests/hooks/make_fixture.py` and expect it in `tests/hooks/test_analyze.py`.
- **Back up what the skills tell people.** A number or a rule needs a source or a measurement, and a rule of thumb should say it is one. Don't promise views.
- **Leave out what isn't yours to share.** No secrets, personal data, or video you don't have the rights to.

If you change the README images, rebuild them with `docs/assets/src/render.sh`.

## Pull requests

Titles look like `fix: stop the crash on ffmpeg without drawtext`: a lowercase type (`feat`, `fix`, `docs`, `test`, `refactor` or `chore`), a colon, then 8 to 70 characters with no period at the end. In the description, say what changed, why, and how you tested it.

## License

By contributing, you agree that your contribution is licensed under the [MIT License](LICENSE).
