import os
import re
import json
import yt_dlp
import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, error
import ollama

# ----------------------
# Config
# ----------------------
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
OLLAMA_MODEL = "gemma3:4b"

# ----------------------
# Legalize file names
# ----------------------
def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|｜]', '', name)
    return name.strip()

# ----------------------
# 1. Download audio
# ----------------------
def download_audio(url, title_artist=None):
    info = None
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)

    if info is None:
        raise RuntimeError("yt-dlp failed to fetch video info.")

    raw_title = info.get('title', 'unknown')

    if title_artist:
        song, artist = title_artist
        safe_filename = sanitize_filename(f"{song} ({artist})")
    else:
        safe_filename = sanitize_filename(raw_title)

    mp3_file = os.path.join(DOWNLOAD_DIR, f"{safe_filename}.mp3")
    temp_file_template = os.path.join(DOWNLOAD_DIR, f"{safe_filename}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': temp_file_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': False,
        'ignoreerrors': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # Cleanup leftover original file
    downloaded_ext = info.get('ext')
    temp_file_path = os.path.join(DOWNLOAD_DIR, f"{safe_filename}.{downloaded_ext}")
    if os.path.exists(temp_file_path) and temp_file_path != mp3_file:
        os.remove(temp_file_path)

    return raw_title, mp3_file, info

# ----------------------
# 2. Clean title/artist using Ollama
# ----------------------
def clean_yt_title(title):
    prompt = f"""
You are a music metadata assistant.
Given the YouTube video title below, extract the most probable song title and artist.
Return in JSON format like: {{ "title": "...", "artist": "..." }}

YouTube title: {title}
"""
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{'role': 'user', 'content': prompt}]
    )

    text_output = response['message']['content'].strip()
    text_output = re.sub(r'^```json\s*', '', text_output, flags=re.IGNORECASE)
    text_output = re.sub(r'```$', '', text_output)

    try:
        data = json.loads(text_output)
    except json.JSONDecodeError:
        data = {'title': title, 'artist': ''}

    return data.get('title', title), data.get('artist', '')

# ----------------------
# 3. Fetch MusicBrainz metadata
# ----------------------
def fetch_musicbrainz_metadata(song, artist):
    query = f"{song} {artist}"
    url = f"https://musicbrainz.org/ws/2/recording/?query={query}&fmt=json"
    try:
        r = requests.get(url, headers={'User-Agent': 'SmartMP3/1.0'})
        data = r.json()
        recordings = data.get('recordings', [])
        if recordings:
            rec = recordings[0]
            album = rec['releases'][0]['title'] if rec.get('releases') else ''
            year = rec['releases'][0]['date'].split('-')[0] if rec.get('releases') and 'date' in rec['releases'][0] else ''
            return album, year
    except Exception as e:
        print("MusicBrainz fetch failed:", e)
    return '', ''

# ----------------------
# 4. Download and save thumbnail
# ----------------------
def download_thumbnail(cover_url, title, artist):
    """Download thumbnail and return the local file path"""
    if not cover_url:
        return None
    
    try:
        img_response = requests.get(cover_url)
        img_response.raise_for_status()
        img_data = img_response.content
        
        # Save thumbnail as separate file
        thumb_file = os.path.join(DOWNLOAD_DIR, sanitize_filename(f"{title} ({artist})") + ".jpg")
        with open(thumb_file, 'wb') as f:
            f.write(img_data)
        
        return thumb_file
    except Exception as e:
        print(f"Failed to download thumbnail: {e}")
        return None

# ----------------------
# 5. Tag MP3 + embed thumbnail from local file
# ----------------------
def tag_mp3(filepath, title, artist, album='', year='', thumb_file=None):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"MP3 file not found: {filepath}")

    # Basic tags
    audio = EasyID3(filepath)
    audio['title'] = title
    audio['artist'] = artist
    if album:
        audio['album'] = album
    if year:
        audio['date'] = year
    audio.save()

    # Embed album art from local thumbnail file
    if thumb_file and os.path.exists(thumb_file):
        try:
            with open(thumb_file, 'rb') as f:
                img_data = f.read()
            
            try:
                audio_id3 = ID3(filepath)
            except error.ID3NoHeaderError:
                audio_id3 = ID3()

            audio_id3.delall('APIC')  # Remove old covers
            audio_id3.add(
                APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=img_data
                )
            )
            audio_id3.save(filepath)
            print(f"✓ Album art embedded successfully from: {thumb_file}")
        except Exception as e:
            print("Failed to embed cover art:", e)

# ----------------------
# 6. Full pipeline
# ----------------------
def smartmp3_pipeline(url):
    print("[1] Downloading audio...")
    raw_title, _, info = download_audio(url)

    print(f"[2] Cleaning title/artist with {OLLAMA_MODEL}...")
    title, artist = clean_yt_title(raw_title)
    print(f"[3] Fetched clean metadata: {title} - {artist}")

    print("[4] Downloading MP3 with proper filename...")
    _, mp3_file, info = download_audio(url, title_artist=(title, artist))

    print("[5] Fetching MusicBrainz info...")
    album, year = fetch_musicbrainz_metadata(title, artist)
    print(f"[6] Album/Year: {album}/{year}")

    print("[7] Downloading thumbnail...")
    cover_url = info.get('thumbnails', [{}])[-1].get('url') if info.get('thumbnails') else None
    thumb_file = download_thumbnail(cover_url, title, artist)
    
    if thumb_file:
        print(f"✓ Thumbnail saved: {thumb_file}")
    else:
        print("⚠ No thumbnail available or download failed")

    print("[8] Tagging MP3 and embedding thumbnail...")
    tag_mp3(mp3_file, title, artist, album, year, thumb_file)

    print(f"[9] Done! MP3 saved: {mp3_file}")

# ----------------------
# Run
# ----------------------
if __name__ == "__main__":
    yt_url = input("Enter YouTube URL: ").strip()
    smartmp3_pipeline(yt_url)