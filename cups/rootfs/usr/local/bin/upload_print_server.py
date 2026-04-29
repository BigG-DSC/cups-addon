#!/usr/bin/env python3

import os
import subprocess
import tempfile
from flask import Flask, request, render_template_string

app = Flask(__name__)
MAX_UPLOAD_MB = 30
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>CUPS Upload & Print</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 760px; margin: 24px auto; padding: 0 16px; }
    .box { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-top: 16px; }
    .ok { color: #096b2f; }
    .err { color: #a12222; }
    input, select, button { font-size: 14px; margin: 8px 0; }
  </style>
</head>
<body>
  <h1>CUPS Upload & Print</h1>
  <p>Upload a document and print it via CUPS.</p>
  <div class="box">
    <form method="post" enctype="multipart/form-data">
      <label>Printer:</label><br>
      <select name="printer" required>
        {% for p in printers %}
          <option value="{{ p }}" {% if p == selected_printer %}selected{% endif %}>{{ p }}</option>
        {% endfor %}
      </select><br>
      <label>Document (PDF, TXT, image...):</label><br>
      <input type="file" name="document" required><br>
      <button type="submit">Upload and Print</button>
    </form>
  </div>
  {% if message %}
    <p class="{{ 'ok' if success else 'err' }}">{{ message }}</p>
  {% endif %}
</body>
</html>
"""


def list_printers():
    result = subprocess.run(
        ["lpstat", "-a"],
        check=False,
        capture_output=True,
        text=True,
    )
    printers = []
    for line in result.stdout.splitlines():
        parts = line.strip().split()
        if parts:
            printers.append(parts[0])
    return printers


def default_printer():
    result = subprocess.run(
        ["lpstat", "-d"],
        check=False,
        capture_output=True,
        text=True,
    )
    text = result.stdout.strip()
    if ": " in text:
        return text.split(": ", 1)[1].strip()
    return ""


@app.route("/", methods=["GET", "POST"])
def upload_and_print():
    printers = list_printers()
    selected = default_printer() or (printers[0] if printers else "")
    message = ""
    success = False

    if request.method == "POST":
        printer = request.form.get("printer", "").strip()
        file = request.files.get("document")

        if not printer:
            message = "Please select a printer."
        elif not file or not file.filename:
            message = "Please upload a file."
        else:
            selected = printer
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="/tmp") as tmp:
                tmp_path = tmp.name
                file.save(tmp_path)
            try:
                run = subprocess.run(
                    ["lp", "-d", printer, tmp_path],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if run.returncode == 0:
                    success = True
                    message = f"Print sent to '{printer}'. {run.stdout.strip()}"
                else:
                    message = f"Printing failed: {run.stderr.strip() or run.stdout.strip()}"
            finally:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    return render_template_string(
        PAGE,
        printers=printers,
        selected_printer=selected,
        message=message,
        success=success,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8099, debug=False)
