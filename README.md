# YouTube Transcriptor

Download the transcript of any YouTube video as a plain-text file — with timestamps, English-first language selection, and a clean title-based filename.

---

## Features

- Fetches the **English transcript** automatically (manual captions preferred over auto-generated)
- Falls back to any available language if English is not present
- Names the output file after the **video title** (spaces → underscores, special characters removed)
- Appends the language code as a suffix when the transcript is not English, e.g. `My_Video_bs.txt`
- Optional timestamps, custom output path, and preferred language flags

---

## Requirements

- Python 3.8+
- [`youtube-transcript-api`](https://github.com/jdepoix/youtube-transcript-api)
- [`requests`](https://pypi.org/project/requests/)

---

## Installation

### Using the install script (recommended)

```bash
bash install_requirements.sh
```

This will:
1. Create a Python virtual environment (`venv/`) in the project directory
2. Activate it
3. Install all dependencies from `requirements.txt`

### Manual install

```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Usage

### Using the run script

The easiest way to run the app is with `run_app.sh`, which handles venv activation automatically:

```bash
bash run_app.sh 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
```

You can pass any arguments that `youtube_transcript.py` accepts:

```bash
bash run_app.sh 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' --no-timestamps
bash run_app.sh 'https://youtu.be/dQw4w9WgXcQ' --output my_transcript.txt
bash run_app.sh 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' --language fr es
```

### Direct Python usage

```bash
source venv/bin/activate

# Basic — saves to <Video_Title>.txt
python youtube_transcript.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

# Custom output file
python youtube_transcript.py 'https://youtu.be/dQw4w9WgXcQ' --output transcript.txt

# No timestamps
python youtube_transcript.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' --no-timestamps

# Prefer a specific language (falls back if unavailable)
python youtube_transcript.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' --language fr es en
```

### CLI reference

| Argument | Description |
|---|---|
| `url` | YouTube video URL (required) |
| `--output`, `-o` | Output filename (default: derived from video title) |
| `--no-timestamps` | Omit `[MM:SS]` timestamps from output |
| `--language`, `-l` | Preferred language code(s), e.g. `en fr es` |

---

## Output filename format

| Situation | Filename |
|---|---|
| English transcript available | `Rick_Astley_Never_Gonna_Give_You_Up.txt` |
| Non-English only (e.g. Bosnian) | `Some_Video_Title_bs.txt` |
| `--output` flag provided | whatever you specified |

---

## Using with an LLM in VS Code (GitHub Copilot)

This project includes a Copilot instructions file (`.github/copilot-instructions.md`) that teaches the VS Code Copilot agent how to use this tool.

Once the instructions file is in place, you can ask Copilot questions about any YouTube video directly in chat:

**Example prompts:**

```
Summarize https://www.youtube.com/watch?v=dQw4w9WgXcQ
```
```
Give me a step-by-step tutorial from this video: https://youtu.be/dQw4w9WgXcQ
```
```
What are the main points discussed in https://www.youtube.com/watch?v=dQw4w9WgXcQ ?
```
```
Create a quiz based on the content of https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Copilot will:
1. Run the transcript script against the URL
2. Read the saved transcript file
3. Answer your question using **only the content of the transcript**

> The LLM will not invent information or pull from outside sources unless you explicitly ask it to.

See [`.github/copilot-instructions.md`](.github/copilot-instructions.md) for the full agent instructions.


**Example Input & Output:**
Input (Using GPT-5 Mini)
```
Summarize https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Output
```
Summary

Core message: A speaker repeatedly promises commitment and reassurance — they will never give the listener up, let them down, run around, desert them, make them cry, say goodbye, or lie and hurt them.
Context: The verses explain they've known each other a long time, both understand the situation and "the game," and the speaker wants to declare their feelings and make the listener understand.
Notable chorus timestamps: chorus starts at [00:43], repeats at [01:25], [02:41], and later.
```


## Did you just get Rickrolled in a Github readme? 
Yes