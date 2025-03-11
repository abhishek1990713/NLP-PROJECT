from django.contrib import admin
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
import pandas as pd
ffrom ultralytics import YOLO
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
            padding: 10px;
            text-align: left;
            word-wrap: break-word;
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
