# Gemini API Setup Guide

## Why Gemini?

Gemini API is now the primary AI engine for Pixie because it:

- ✅ **Natively supports images** - No need for separate vision models
- ✅ **Handles documents** - PDFs, text files, code files
- ✅ **Processes text** - Fast and accurate responses
- ✅ **All in one API** - No switching between models
- ✅ **Free tier available** - 15 requests per minute free

## Get Your API Key

1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy your API key

## Configure Pixie

1. Open `.env` file in the project root
2. Replace `your_gemini_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=AIzaSy...your_actual_key_here
   ```
3. Save the file

## What Works Now

### Text Messages

Just type and chat normally - works instantly!

### Images

Send images in 3 ways:

1. **Drag & drop** into the chat window
2. **Click the + button** to browse for images
3. **Type the file path** in your message

Supported formats: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.ico`

### Documents

Send documents the same way as images:

1. **Drag & drop** document files
2. **Click the + button** to browse
3. **Type the file path** in your message

Supported formats: `.txt`, `.md`, `.pdf`, `.json`, `.xml`, `.csv`, `.py`, `.js`, `.html`, `.css`, etc.

## Example Usage

**Analyze an image:**

```
What's in this image?
[attach image.jpg]
```

**Read a document:**

```
Summarize this document
[attach report.pdf]
```

**Multiple files:**

```
Compare these two images
[attach photo1.jpg]
[attach photo2.jpg]
```

## Troubleshooting

### "GEMINI_API_KEY not found"

- Make sure you added your API key to `.env`
- Check there are no extra spaces
- Restart the application

### "Rate limit exceeded"

- Free tier: 15 requests/minute
- Wait a minute and try again
- Or upgrade to paid tier

### Images not working

- Check file format is supported
- Make sure file path is correct
- Try a smaller image (< 4MB recommended)

## Models Used

- **gemini-1.5-flash** - Fast, supports text + images + documents
- Automatically switches based on your input

## Fallback to Groq

If Gemini fails, Pixie can still use Groq for text-only responses. Your Groq API key is still configured as backup.
