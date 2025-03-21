from flask import Flask, request, jsonify, Response
import yt_dlp
import requests

app = Flask(__name__)

@app.route('/info')
def get_info():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    try:
        # 🟢 Noembed لجلب العنوان والصورة
        noembed = requests.get(f'https://noembed.com/embed?url={url}').json()
        title = noembed.get('title')
        thumbnail = noembed.get('thumbnail_url')

        # 🟢 yt_dlp لجلب الجودات والمدة
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info['formats']:
            formats.append({
                'format_id': f.get('format_id'),
                'ext': f.get('ext'),
                'resolution': f.get('resolution') or f"{f.get('height', '')}p",
                'filesize': f.get('filesize') or 0,
                'format_note': f.get('format_note') or '',
                'audio_quality': f.get('audio_quality') or '',
            })

        return jsonify({
            'title': title,
            'thumbnail': thumbnail,
            'duration': info.get('duration'),
            'formats': formats
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download')
def download():
    url = request.args.get('url')
    format_id = request.args.get('format')
    if not url or not format_id:
        return jsonify({'error': 'Missing URL or format'}), 400

    def generate():
        ydl_opts = {
            'quiet': True,
            'format': format_id,
            'outtmpl': '-',
            'noplaylist': True,
            'cookiesfrombrowser': ('chrome',),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
            ydl.download([url])
            # ملاحظة: البث المباشر للملف يتطلب معالجة إضافية وقد تحتاج لملف مؤقت أو بث مباشر عبر ffmpeg

    return jsonify({'error': 'Streaming not implemented in this version'}), 501

@app.route('/')
def home():
    return '🎉 API is running! Use /info?url=VIDEO_URL'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
