8from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("", views.index,name ='homes'),
    path("detect-object/", views.detect_objects, name='detect_objects'),
    path('run_app/',views.run_app, name="run_app")
]


from ultralytics import YOLO
from PIL import Image
import os
import numpy as np
import logging
import cv2
import pandas as
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import asyncio
from typing import List
from all_passport_app import all_passport  # Import your function

app = FastAPI()

# Ensure the "static" directory exists
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("passport_index_2.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

async def delete_files_after_response(file_paths: List[str]):
    await asyncio.sleep(20)
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/upload/", response_class=HTMLResponse)
async def upload_images(files: List[UploadFile] = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    html_content = """
    <h1>Processing Results</h1>
    <div style="border: 1px solid #ccc; padding: 15px; max-height: 600px; overflow-y: scroll;">
    """

    uploaded_file_paths = []

    for file in files:
        try:
            # Save uploaded file
            image_path = f"static/{file.filename}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_file_paths.append(image_path)

            # Process the image and get the result
            result = all_passport(image_path)
            print(result, '######')  # Debugging output

            # Generate HTML content for results
            html_content += f"""
            <h3>Image: {file.filename}</h3>
            <img src="/static/{file.filename}" alt="{file.filename}" style="max-width: 100%; height: auto;">
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <th style="padding: 12px; background-color: #f2f2f2;">Label</th>
                    <th style="padding: 12px; background-color: #f2f2f2;">Extracted Text</th>
                </tr>
            """

            for row in result:
                label = row[0]
                text_value = row[1]

                # ✅ FIX: Escape "<" characters to display them properly
                text_value = text_value.replace("<", "&lt;")

                html_content += f"""
                <tr>
                    <td style="padding: 12px;">{label}</td>
                    <td style="padding: 12px; word-break: break-word; white-space: pre-wrap;">{text_value}</td>
                </tr>
                """

            html_content += "</table><hr>"

        except Exception as e:
            html_content += f"<h3>Error processing {file.filename}: {str(e)}</h3><hr>"

    html_content += "</div><br><a href='/'>Upload More Images</a>"

    # Schedule file deletion
    background_tasks.add_task(delete_files_after_response, uploaded_file_paths)

    return HTMLResponse(content=html_content)




         <!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PASSPORT KYC INFO</title>
    <style>
        body {
            background-color: rgb(153, 193, 227);
            font-family: Arial, Helvetica, sans-serif;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100vh;
            margin: 0;
            position: relative;
        }

        #logo {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 150px;
            height: auto;
        }

        #uploadContainer {
            background-color: aliceblue;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            width: 50%;
            min-width: 300px;
            margin: auto;
        }

        form {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        input[type="file"] {
            margin-top: 10px;
        }

        button {
            margin-top: 15px;
            padding: 10px 20px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        button:hover {
            background-color: #005663;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            table-layout: auto;
            margin-top: 20px;
        }

        th, td {
            border: 1px solid black;
            padding: 12px;
            text-align: left;
            word-break: break-word;
            overflow-x: auto;
            max-width: 100%;
            white-space: pre-wrap;
        }

        #results {
            border: 1px solid #ccc;
            padding: 10px;
            max-height: 400px;
            overflow-y: scroll;
            margin-top: 20px;
        }
    </style>
</head>

<body>

    <img src="citilogo2.png" alt="Website Logo" id="logo">

    <h1>PASSPORT KYC INFO</h1>

    <div id="uploadContainer">
        <form id="uploadForm" action="/upload/" method="post" enctype="multipart/form-data">
            <label for="files">Select Images (Upload Multiple Images: jpeg, jpg, png, etc...):</label><br><br>
            <input type="file" id="files" name="files" multiple><br><br>
            <button type="submit">Upload and Process</button>
        </form>
    </div>

    <h2>Uploaded Files and Results:</h2>

    <div id="results"></div>

    <script>
        const form = document.getElementById('uploadForm');
        const resultsDiv = document.getElementById('results');

        form.addEventListener('submit', async (event) => {
            event.preventDefault(); // Prevent form submission

            const formData = new FormData(form);

            // Send the file to the server using fetch
            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData
            });

            const result = await response.text();

            // Append the result to the resultsDiv
            resultsDiv.innerHTML += result + '<hr>';

            form.reset(); // Reset the form for the next file
        });
    </script>

</body>
</html>
