from flask import Flask, request, jsonify, Response, render_template
import yt_dlp
import os
import threading
import time

app = Flask(__name__)

# Create a temporary directory for downloads within the application directory
TEMP_DIR = 'temp_downloads'
os.makedirs(TEMP_DIR, exist_ok=True)

# Delay for file cleanup (in seconds)
FILE_CLEANUP_DELAY = 30  # 30 seconds


def delete_file_after_delay(file_path, delay):
    """Delete a file after a specified delay."""
    time.sleep(delay)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted temporary file: {file_path}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # Set download options
        ydl_opts = {
            'outtmpl':
            os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
            'format':
            'bestvideo+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # Convert output to .mp4
            }],
        }

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp4'
            file_name = os.path.basename(file_path)

        # Start a delayed deletion thread
        threading.Thread(target=delete_file_after_delay,
                         args=(file_path, FILE_CLEANUP_DELAY)).start()

        # Stream the file back to the client
        def generate():
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    yield chunk

        response = Response(generate(),
                            content_type='application/octet-stream')
        response.headers[
            'Content-Disposition'] = f'attachment; filename="{file_name}"'

        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
