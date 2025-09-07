# 🎵 YT2MP3

**An AI-powered YouTube to MP3 converter that actually gets your metadata right!**

![Python](https://img.shields.io/badge/python-v3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

🤖 **AI-Powered Metadata Cleaning** - Uses Ollama (Gemma3:4b) to extract proper song titles and artists from messy YouTube titles

🎵 **High-Quality Audio** - Downloads best available audio and converts to 192kbps MP3

🖼️ **Album Art Embedding** - Automatically downloads and embeds YouTube thumbnails as album covers

📊 **MusicBrainz Integration** - Fetches additional metadata like album names and release years

📁 **Smart File Organization** - Clean, sanitized filenames that work across all operating systems

⚡ **Robust Pipeline** - Handles errors gracefully with fallback options

## 🚀 Quick Start

### Prerequisites

**1. Python 3.11**
Make sure you have Python installed. Check with:
```bash
python --version
```

**2. FFmpeg**
Download and install FFmpeg:
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or equivalent

**3. Ollama**
Download and install [Ollama](https://ollama.com/) and pull the Gemma3 model:
```bash
ollama pull gemma3:4b
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/bdwarker/yt2mp3.git
cd yt2mp3
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the program**
```bash
python main.py
```

## 📖 Usage

Simply run the script and enter a YouTube URL when prompted:

```
Enter YouTube URL: 
```

The program will:
1. 📥 Download the audio from YouTube
2. 🤖 Use AI to clean up the title and extract artist info
3. 🔍 Fetch additional metadata from MusicBrainz
4. 🖼️ Download and embed album artwork
5. 🏷️ Tag the MP3 file with proper metadata
6. 💾 Save everything in the `downloads/` folder

## 🛠️ How It Works

### The Pipeline

```
YouTube URL → yt-dlp → Raw Audio + Metadata
     ↓
AI Cleaning (Ollama/Gemma3) → Clean Title + Artist
     ↓
MusicBrainz API → Album + Year Info
     ↓
Thumbnail Download → Album Art
     ↓
MP3 Tagging → Final Tagged File
```

### Example Transformation

**Before (Raw YouTube title):**
```
"Rick Astley - Never Gonna Give You Up (Official Video) 4K Remaster"
```

**After (AI-cleaned metadata):**
```
Title: Never Gonna Give You Up
Artist: Rick Astley
Album: Whenever You Need Somebody
Year: 1987
```

## 📁 Project Structure

```
yt2mp3/
├── main.py          # Main application
├── requirements.txt     # Python dependencies
├── downloads/          # Output folder (auto-created)
├── README.md          # This file
└── LICENSE            # MIT License
```

## 🔧 Configuration

The following constants can be modified at the top of `main.py`:

- `DOWNLOAD_DIR`: Output directory (default: 'downloads')
- `OLLAMA_MODEL`: AI model to use (recommended: 'gemma3:4b')

## ⚠️ Troubleshooting

**"FFmpeg not found"**
- Make sure FFmpeg is installed and added to your system PATH

**"Ollama model not found"**
- Run `ollama pull gemma3:4b` to download the AI model

**"Permission denied" errors**
- Check if the downloads folder is writable
- On Linux/macOS, you might need to adjust permissions

**Poor metadata extraction**
- The AI occasionally misinterprets titles. The original filename is preserved as a fallback

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The best YouTube downloader
- [Ollama](https://ollama.ai/) - For making local AI simple
- [MusicBrainz](https://musicbrainz.org/) - The open music encyclopedia
- [Mutagen](https://github.com/quodlibet/mutagen) - Audio metadata handling

---

**Made by Mohammed Shaan**

*If this saved you from manually renaming a thousand music files, consider giving it a ⭐!*

---