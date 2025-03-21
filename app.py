from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/info', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': 'best',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info.get('formats', []):
                if f.get('filesize'):
                    formats.append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'quality': f.get('format_note'),
                        'filesize': f.get('filesize'),
                        'url': f.get('url')
                    })
            result = {
                'title': info.get('title'),
                'duration': info.get('duration'),
                'thumbnail': info.get('thumbnail'),
                'formats': formats
            }
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return 'YouTube Info API is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)