from flask import Flask, request, jsonify, send_from_directory
import yt_dlp as youtube_dl
import os
from datetime import datetime, timedelta
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Cleanup old files
def cleanup_old_files():
    """Remove files older than 1 day."""
    now = datetime.now()
    for filename in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if now - file_time > timedelta(days=1):
            os.remove(file_path)
            logger.info(f"Deleted old file: {filename}")

# Home route
@app.route('/')
def home():
    with open('index.html', 'r', encoding='utf-8') as file:
        return file.read()

# Download route
@app.route('/download', methods=['POST'])
def download_reel():
    data = request.json
    reel_link = data.get('link')

    if not reel_link:
        return jsonify({'success': False, 'error': 'No link provided'})

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(reel_link, download=True)
            video_filename = ydl.prepare_filename(info_dict)
            thumbnail_url = info_dict.get('thumbnail')

        cleanup_old_files()

        return jsonify({
            'success': True,
            'downloadLink': f'/downloads/{os.path.basename(video_filename)}',
            'thumbnail': thumbnail_url,
        })
    except Exception as e:
        logger.error(f"Error downloading reel: {e}")
        return jsonify({'success': False, 'error': str(e)})

# Serve downloaded files
@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))