---
applyTo: '**'
---

# YouTube Transcriptor — Copilot Agent Instructions

This workspace contains a tool that downloads YouTube transcripts to text files. When a user references a YouTube video (by URL or by asking a question about one), you must use this tool to fetch the transcript and base your answer entirely on it.

---

## When to trigger the transcript tool

Trigger this workflow any time the user:
- Pastes or mentions a YouTube URL (e.g. `https://www.youtube.com/watch?v=...` or `https://youtu.be/...`)
- Asks to summarize, explain, review, quiz, or do anything with a YouTube video
- Asks a question whose answer would come from a video's content

---

## How to run the transcript script

Use the terminal to run the following command, substituting the actual URL:

```bash
source venv/bin/activate && python youtube_transcript.py 'YOUTUBE_URL_HERE'
```

**Example:**
```bash
source venv/bin/activate && python youtube_transcript.py 'https://www.youtube.com/watch?v=wpSqsVHXGIA'
```

The script will print output similar to:
```
Fetching transcript for video ID: wpSqsVHXGIA
Found transcript in: English (United States) (143 segments)
Fetching video title...
Transcript saved to: My_Video_Title.txt
Done! (143 lines)
```

---

## How to find and read the output file

The script prints the output filename on the line starting with `Transcript saved to:`. Read that exact file.

**Rules for the filename:**
- The name is based on the video title with spaces replaced by underscores, special characters removed, and non-ASCII characters transliterated to ASCII (e.g. `François` → `Francois`).
- If the transcript is in English, the file is named `Video_Title.txt`.
- If the transcript is in another language, it is named `Video_Title_{language_code}.txt` (e.g. `Video_Title_bs.txt`).

After the script finishes, read the file:
```
Read the file: My_Video_Title.txt
```

---

## How to answer the user's question

1. **Run the script** to get the transcript.
2. **Read the transcript file** that was saved.
3. **Answer the user's question using only the content of the transcript.**
4. Do **not** use outside knowledge or make up information that is not in the transcript, unless the user explicitly asks you to.
5. If the transcript does not contain enough information to answer the question, say so clearly and offer to search for more information if the user wants.

---

## Example workflows

### Summarize a video
**User:** `Summarize https://www.youtube.com/watch?v=wpSqsVHXGIA`

**You:**
1. Run: `source venv/bin/activate && python youtube_transcript.py 'https://www.youtube.com/watch?v=wpSqsVHXGIA'`
2. Read the output transcript file (filename printed by the script)
3. Write a summary based on the transcript content

---

### Answer a question about a video
**User:** `What tools does the presenter recommend in https://www.youtube.com/watch?v=wpSqsVHXGIA?`

**You:**
1. Run the script for the URL
2. Read the transcript
3. List only the tools actually mentioned in the transcript

---

### Create a tutorial from a video
**User:** `Give me a step-by-step tutorial based on https://youtu.be/wpSqsVHXGIA`

**You:**
1. Run the script for the URL
2. Read the transcript
3. Extract and restructure the steps described in the video into a clear tutorial

---

### Quiz the user on a video
**User:** `Create a quiz from https://www.youtube.com/watch?v=wpSqsVHXGIA`

**You:**
1. Run the script for the URL
2. Read the transcript
3. Write quiz questions and answers drawn entirely from the transcript

---

## Important rules

- **Always run the script first** before attempting to answer anything about a video's content. Do not rely on your training data about the video.
- **Ground every answer in the transcript.** If a fact is not in the transcript, do not assert it.
- **Cite timestamps** from the transcript where relevant to help the user navigate to specific parts of the video.
- If the script fails (e.g. transcripts are disabled), inform the user clearly and suggest they check if captions are available on the video.
- If the saved transcript file is empty or extremely short (indicating missing or partial captions), retry running the script up to a total of 3 attempts. If the transcript is still missing or inadequate after 3 tries, inform the user that it could not be retrieved.