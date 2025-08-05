from flask import Flask, send_from_directory, jsonify, render_template_string
import os
import re
from datetime import datetime

app = Flask(__name__, static_folder='static')
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

FOLDERS = [
    {"name": "misc/ChatGPT", "prefix": "roosters"},
    {"name": "misc/gemini", "prefix": "gemini"},
    {"name": "misc/artguru", "prefix": "artguru"},
    {"name": "misc/grok NSFW", "prefix": "grok"},
    {"name": "calendar/ChatGPT NSFW", "prefix": "calendar"},
    {"name": "calendar/gemini NSFW", "prefix": "gemini"},
    {"name": "calendar/artguru", "prefix": "artguru"},
    {"name": "calendar/grok NSFW", "prefix": "grok"},
    {"name": "fixed prompts/prompt1/ChatGPT", "prefix": "roosters"},
    {"name": "fixed prompts/prompt1/gemini", "prefix": "gemini"},
    {"name": "fixed prompts/prompt1/artguru", "prefix": "artguru"},
    {"name": "fixed prompts/prompt1/grok", "prefix": "grok"},
    {"name": "fixed prompts/prompt2/ChatGPT", "prefix": "roosters"},
    {"name": "fixed prompts/prompt2/gemini", "prefix": "gemini"},
    {"name": "fixed prompts/prompt2/artguru", "prefix": "artguru"},
    {"name": "fixed prompts/prompt2/grok", "prefix": "grok"}
]

def extract_date(filename, prefix):
    pattern = re.compile(rf'{re.escape(prefix)}_(\d{{8}})_.*\.(png|jpg|jpeg|webp)$', re.IGNORECASE)
    m = pattern.match(filename)
    if m:
        return datetime.strptime(m.group(1), "%Y%m%d")
    return None

def load_description_text(folder_type, date_str):
    desc_path = os.path.join(BASE_PATH, 'descriptions', folder_type, f"{date_str}.txt")
    if os.path.exists(desc_path):
        with open(desc_path, encoding='utf-8') as f:
            return f.read()
    return ""

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Rooster Viewer</title>
  <style>
    body {
      margin: 0; padding: 0;
      height: 100vh;
      display: flex;
      font-family: sans-serif;
      background-color: black;
      color: white;
      overflow: hidden;
    }
    #content { display: flex; flex: 1; height: 100vh; }
    #imageContainer {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
      background-color: black;
    }
    #roosterImage {
      max-height: 100vh;
      max-width: 100%;
      object-fit: contain;
      border: 2px solid white;
      background-color: black;
    }
    #sidebar {
      width: 300px;
      display: flex;
      flex-direction: column;
      padding: 20px;
      gap: 20px;
      background-color: #111;
    }
    #folderName { font-size: 18px; }
    #dateDisplay {
      font-size: 22px;
      font-family: monospace;
    }
    #description {
      font-size: 14px;
      line-height: 1.4;
      color: #ccc;
      white-space: pre-wrap;
      max-height: 80vh;
      overflow: auto;
      padding-right: 8px;
    }
    button {
      padding: 12px 16px;
      font-size: 16px;
      background-color: #222;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }
    button:hover:enabled { background-color: #555; }
    button:disabled { opacity: 0.4; }
  </style>
</head>
<body>
  <div id="content">
    <div id="imageContainer">
      <img id="roosterImage" src="" alt="Rooster Image" />
    </div>
    <div id="sidebar">
      <div id="folderName"></div>
      <div id="dateDisplay"></div>
      <div id="description"></div>
      <button onclick="prevImage()">⬅ Left</button>
      <button onclick="nextImage()">Right ➡</button>
      <button onclick="prevFolder()" id="prevFolderBtn">⬆ Prev Folder</button>
      <button onclick="nextFolder()" id="nextFolderBtn">Next Folder ⬇</button>
    </div>
  </div>

  <script>
    let folders = [];
    let currentFolderIndex = 0;
    let currentImageIndex = 0;

    fetch('/list-images')
      .then(res => res.json())
      .then(data => {
        folders = data;
        if (folders.length > 0 && folders[0].files.length > 0) {
          showImage(currentFolderIndex, currentImageIndex);
        }
      });

    function showImage(folderIdx, imageIdx) {
      const folder = folders[folderIdx];
      const fileObj = folder.files[imageIdx];
      const imagePath = folder.name + '/' + fileObj.filename;
      const isNSFW = fileObj.filename.toLowerCase().includes("nsfw");
      const img = document.getElementById("roosterImage");

      if (isNSFW) {
        img.src = "/static/blurred-placeholder.jpg";
        img.style.cursor = "pointer";
        img.onclick = () => {
          img.src = imagePath;
          img.style.cursor = "default";
          img.onclick = null;
        };
      } else {
        img.src = imagePath;
        img.style.cursor = "default";
        img.onclick = null;
      }

      document.getElementById("folderName").textContent = "Folder: " + folder.name;
      document.getElementById("dateDisplay").textContent = fileObj.date;
      document.getElementById("description").textContent = fileObj.description || "(No description)";
      currentFolderIndex = folderIdx;
      currentImageIndex = imageIdx;

      updateFolderButtons();
    }

    function nextImage() {
      const folder = folders[currentFolderIndex];
      if (currentImageIndex < folder.files.length - 1) {
        currentImageIndex++;
        showImage(currentFolderIndex, currentImageIndex);
      }
    }

    function prevImage() {
      if (currentImageIndex > 0) {
        currentImageIndex--;
        showImage(currentFolderIndex, currentImageIndex);
      }
    }

    function findExactDateIndex(folder, dateStr) {
      return folder.files.findIndex(f => f.date === dateStr);
    }

    function nextFolder() {
      const currDate = folders[currentFolderIndex].files[currentImageIndex].date;
      for (let offset = 1; offset < folders.length; offset++) {
        const idx = (currentFolderIndex + offset) % folders.length;
        const matchIdx = findExactDateIndex(folders[idx], currDate);
        if (matchIdx !== -1) {
          showImage(idx, matchIdx);
          return;
        }
      }
    }

    function prevFolder() {
      const currDate = folders[currentFolderIndex].files[currentImageIndex].date;
      for (let offset = 1; offset < folders.length; offset++) {
        const idx = (currentFolderIndex - offset + folders.length) % folders.length;
        const matchIdx = findExactDateIndex(folders[idx], currDate);
        if (matchIdx !== -1) {
          showImage(idx, matchIdx);
          return;
        }
      }
    }

    function updateFolderButtons() {
      const currDate = folders[currentFolderIndex].files[currentImageIndex].date;
      const hasNext = folders.some((folder, i) =>
        i !== currentFolderIndex && folder.files.some(f => f.date === currDate));
      const hasPrev = hasNext;

      document.getElementById('nextFolderBtn').disabled = !hasNext;
      document.getElementById('prevFolderBtn').disabled = !hasPrev;
    }

    document.addEventListener("keydown", function(event) {
      if (["ArrowRight", "ArrowLeft", "ArrowDown", "ArrowUp"].includes(event.key)) event.preventDefault();
      if (event.key === "ArrowRight") nextImage();
      else if (event.key === "ArrowLeft") prevImage();
      else if (event.key === "ArrowDown") nextFolder();
      else if (event.key === "ArrowUp") prevFolder();
    });
  </script>
</body>
</html>
''')

@app.route('/list-images')
def list_images():
    result = []
    for folder in FOLDERS:
        folder_path = os.path.join(BASE_PATH, folder["name"])
        prefix = folder["prefix"]
        try:
            files = os.listdir(folder_path)
        except FileNotFoundError:
            files = []
        pattern = re.compile(rf'{re.escape(prefix)}_(\d{{8}})_.*\.(png|jpg|jpeg|webp)$', re.IGNORECASE)
        filtered_files = [f for f in files if pattern.match(f)]
        filtered_files.sort(key=lambda x: extract_date(x, prefix) or datetime.min)

        entries = []
        for f in filtered_files:
            date = extract_date(f, prefix)
            date_str = date.strftime("%Y%m%d") if date else ""
            folder_type = "calendar" if folder["name"].startswith("calendar") else "misc" if folder["name"].startswith("misc") else None
            desc = load_description_text(folder_type, date_str) if folder_type else ""
            entries.append({
                "filename": f,
                "date": date_str,
                "description": desc
            })

        result.append({
            "name": folder["name"],
            "prefix": prefix,
            "files": entries
        })
    return jsonify(result)

@app.route('/<path:folder>/<filename>')
def serve_file(folder, filename):
    folder_path = os.path.join(BASE_PATH, folder)
    return send_from_directory(folder_path, filename)

if __name__ == '__main__':
    app.run(debug=True)

