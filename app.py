import os
import sys
import tempfile
import subprocess
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roblox Deobfuscator</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; background: #1e1e2e; color: #cdd6f4; }
        h1 { color: #89b4fa; }
        textarea { width: 100%; padding: 12px; font-family: 'Courier New', monospace; font-size: 14px; background: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 8px; resize: vertical; }
        button { background: #89b4fa; color: #1e1e2e; padding: 12px 30px; border: none; border-radius: 8px; font-weight: bold; font-size: 16px; cursor: pointer; margin-top: 10px; }
        button:hover { background: #b4befe; }
        .output-box { background: #313244; padding: 15px; border-radius: 8px; border-left: 4px solid #a6e3a1; white-space: pre-wrap; word-break: break-all; font-family: 'Courier New', monospace; font-size: 13px; max-height: 500px; overflow-y: auto; }
        .error { border-left-color: #f38ba8; color: #f38ba8; }
        hr { border-color: #45475a; margin: 30px 0; }
        .footer { font-size: 12px; color: #6c7086; }
    </style>
</head>
<body>
    <h1>🧩 Roblox Deobfuscator</h1>
    <p>I-paste ang obfuscated Lua code sa baba, tapos pindutin ang button.</p>
    <form method="POST">
        <textarea name="code" rows="12" placeholder="Paste your obfuscated script here..." required>{{ code if code else '' }}</textarea>
        <br>
        <button type="submit">⚡ Deobfuscate</button>
    </form>
    {% if result %}
        <hr><h2>✅ Deobfuscated Output:</h2>
        <div class="output-box">{{ result }}</div>
    {% endif %}
    {% if error %}
        <hr><h2>❌ Error:</h2>
        <div class="output-box error">{{ error }}</div>
    {% endif %}
    <hr>
    <div class="footer">⚠️ For educational/personal use only. Respect the original author's license.</div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    code = ''
    result = ''
    error = ''

    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        if not code:
            error = 'Walang laman ang code field.'
            return render_template_string(HTML_PAGE, code=code, result=result, error=error)

        # I-save ang input sa temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False, encoding='utf-8') as f:
            f.write(code)
            input_path = f.name

        try:
            # Patakbuhin ang deobfuscator (gaya ng ginagawa sa CLI)
            cmd = [sys.executable, "deobfuscator.py", input_path]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if proc.returncode != 0:
                error = f"Deobfuscation failed.\nSTDERR: {proc.stderr}"
                return render_template_string(HTML_PAGE, code=code, result=result, error=error)

            # Basahin ang generated report file
            report_file = input_path + ".report.txt"
            if os.path.exists(report_file):
                with open(report_file, 'r', encoding='utf-8', errors='ignore') as f:
                    result = f.read()
            else:
                # Fallback: kung walang report, gamitin ang stdout
                result = proc.stdout

        except subprocess.TimeoutExpired:
            error = "⏰ Timeout! Masyadong malaki o kumplikado ang script (limit: 60 seconds)."
        except Exception as e:
            error = f"Server error: {str(e)}"
        finally:
            # Linisin ang temp files
            for path in [input_path, input_path + ".report.txt"]:
                if os.path.exists(path):
                    try: os.remove(path)
                    except: pass

    return render_template_string(HTML_PAGE, code=code, result=result, error=error)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
