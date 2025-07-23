from flask import Flask, send_from_directory, jsonify, render_template_string
import os
import re
from datetime import datetime

app = Flask(__name__)

# Define folders and corresponding filename prefixes
FOLDERS = [
    {"name": "misc/ChatGPT", "prefix": "roosters"},
    {"name": "misc/gemini", "prefix": "gemini"},
    {"name": "misc/artguru", "prefix": "artguru"},
    {"name": "misc/grok NSFW", "prefix": "grok"},
    {"name": "calendar/ChatGPT NSFW", "prefix": "roosters"},
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

BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')

def extract_date(filename, prefix):
    pattern = re.compile(rf'{re.escape(prefix)}_(\d{{8}})_.*\.(png|jpg|jpeg|webp)$', re.IGNORECASE)
    m = pattern.match(filename)
    if m:
        return datetime.strptime(m.group(1), "%Y%m%d")
    return None

@app.route('/')
def index():
    return render_template_string(r'''
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8" />
      <title>Multi-folder Rooster Viewer</title>
      <style>
        body {
          margin: 0;
          padding: 0;
          height: 100vh;
          display: flex;
          font-family: sans-serif;
          background-color: black;
          color: white;
          user-select: none;
          overflow: hidden;
        }

        #content {
          display: flex;
          flex: 1;
          height: 100vh;
        }

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
          width: 280px;
          display: flex;
          flex-direction: column;
          justify-content: flex-start;
          padding: 20px;
          gap: 20px;
          background-color: #111;
          box-sizing: border-box;
        }

        #folderName {
          font-size: 20px;
          margin-bottom: 10px;
        }

        #dateDisplay {
          font-size: 24px;
          font-family: monospace;
          min-width: 130px;
          user-select: none;
          color: white;
        }

        button {
          padding: 12px 16px;
          font-size: 16px;
          background-color: #222;
          color: white;
          border: none;
          border-radius: 5px;
          cursor: pointer;
          transition: background-color 0.3s;
          width: 100%;
        }

        button:hover:enabled {
          background-color: #555;
        }

        button:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }
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

          <button onclick="prevImage()">⬅ Left</button>
          <button onclick="nextImage()">Right ➡</button>

          <button onclick="prevFolder()" id="prevFolderBtn">⬆ Up (Prev Folder)</button>
          <button onclick="nextFolder()" id="nextFolderBtn">Down ⬇ (Next Folder)</button>
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
              updateFolderName();
            }
          });

        function updateFolderName() {
          document.getElementById("folderName").textContent = "Folder: " + folders[currentFolderIndex].name;
        }

        function showImage(folderIdx, imageIdx) {
          const folder = folders[folderIdx];
          if (!folder || folder.files.length === 0) return;
          document.getElementById("roosterImage").src = folder.name + '/' + folder.files[imageIdx];
          currentFolderIndex = folderIdx;
          currentImageIndex = imageIdx;
          updateFolderName();

          const dateMatch = folder.files[imageIdx].match(/(\d{4})(\d{2})(\d{2})/);
          document.getElementById("dateDisplay").textContent = dateMatch ? `${dateMatch[1]}-${dateMatch[2]}-${dateMatch[3]}` : "";

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
          return folder.files.findIndex(f => f.includes(dateStr));
        }

        function nextFolder() {
          const currFile = folders[currentFolderIndex].files[currentImageIndex];
          const dateStr = currFile.match(/\d{8}/)[0];
          for (let offset = 1; offset < folders.length; offset++) {
            let idx = (currentFolderIndex + offset) % folders.length;
            let matchIdx = findExactDateIndex(folders[idx], dateStr);
            if (matchIdx !== -1) {
              showImage(idx, matchIdx);
              return;
            }
          }
        }

        function prevFolder() {
          const currFile = folders[currentFolderIndex].files[currentImageIndex];
          const dateStr = currFile.match(/\d{8}/)[0];
          for (let offset = 1; offset < folders.length; offset++) {
            let idx = (currentFolderIndex - offset + folders.length) % folders.length;
            let matchIdx = findExactDateIndex(folders[idx], dateStr);
            if (matchIdx !== -1) {
              showImage(idx, matchIdx);
              return;
            }
          }
        }

        function hasExactDate(folder, dateStr) {
          return folder.files.some(f => f.includes(dateStr));
        }

        function updateFolderButtons() {
          const currFile = folders[currentFolderIndex].files[currentImageIndex];
          const dateStr = currFile.match(/\d{8}/)[0];

          let hasNext = false, hasPrev = false;
          for (let offset = 1; offset < folders.length; offset++) {
            if (hasExactDate(folders[(currentFolderIndex + offset) % folders.length], dateStr)) {
              hasNext = true; break;
            }
          }
          for (let offset = 1; offset < folders.length; offset++) {
            if (hasExactDate(folders[(currentFolderIndex - offset + folders.length) % folders.length], dateStr)) {
              hasPrev = true; break;
            }
          }

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
        pattern = re.compile(rf'{re.escape(prefix)}_\d{{8}}_.*\.(png|jpg|jpeg|webp)$', re.IGNORECASE)
        filtered_files = [f for f in files if pattern.match(f)]
        filtered_files.sort(key=lambda x: extract_date(x, prefix) or datetime.min)
        result.append({
            "name": folder["name"],
            "prefix": prefix,
            "files": filtered_files
        })
    return jsonify(result)

@app.route('/<path:folder>/<filename>')
def serve_file(folder, filename):
    folder_path = os.path.join(BASE_PATH, folder)
    return send_from_directory(folder_path, filename)

if __name__ == '__main__':
    app.run(debug=True)

