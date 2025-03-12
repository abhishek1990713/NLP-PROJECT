98from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("", views.index,name ='homes'),
    path("detect-object/", views.detect_objects, name='detect_objects'),




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
            height: 100vh;
            margin: 0;
            position: relative;
        }

        #logo {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 120px;
            height: auto;
        }

        #uploadContainer {
            background-color: aliceblue;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            width: 50%;
            min-width: 280px;
            margin: auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        input[type="file"] {
            flex: 1;
            padding: 10px;
        }

        button {
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

        /* Output section styling */
        #resultsContainer {
            display: flex;
            flex-direction: row;
            justify-content: center;
            align-items: flex-start;
            margin-top: 20px;
            width: 95%;
            height: 70vh;
        }

        #imageContainer {
            flex: 1;
            padding: 10px;
            text-align: center;
        }

        #imageContainer img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        #textContainer {
            flex: 2;
            padding: 10px;
            overflow-y: auto;
            max-height: 70vh;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            border: 1px solid black;
            padding: 10px;
            text-align: left;
            word-wrap: break-word;
            overflow-x: auto;
            white-space: pre-wrap;
        }

        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>

    <img src="citilogo2.png" alt="Website Logo" id="logo">

    <h1>PASSPORT KYC INFO</h1>

    <!-- Upload Section -->
    <div id="uploadContainer">
        <input type="file" id="files" name="files" multiple>
        <button id="uploadBtn">Upload and Process</button>
    </div>

    <!-- Results Section -->
    <h2>Uploaded Files and Results:</h2>
    <div id="resultsContainer">
        <div id="imageContainer"></div>
        <div id="textContainer"></div>
    </div>

    <script>
        const uploadBtn = document.getElementById('uploadBtn');
        const fileInput = document.getElementById('files');
        const imageContainer = document.getElementById('imageContainer');
        const textContainer = document.getElementById('textContainer');

        uploadBtn.addEventListener('click', async () => {
            if (fileInput.files.length === 0) {
                alert("Please select a file first.");
                return;
            }

            const formData = new FormData();
            for (let file of fileInput.files) {
                formData.append("files", file);
            }

            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData
            });

            const result = await response.text();

            // Clear previous content
            imageContainer.innerHTML = '';
            textContainer.innerHTML = '';

            // Append the result to the results container
            textContainer.innerHTML = result;
            fileInput.value = ""; // Reset file input
        });
    </script>

</body>
</html>

