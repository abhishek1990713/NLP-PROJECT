98from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("", views.index,name ='homes'),
    path("detect-object/", views.detect_objects, name='detect_objects'),
    path('run_app/',views.run_app, name="run_app")
]


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
            margin: 0;
            padding: 0;
        }

        #logo {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 100px;
            height: auto;
        }

        /* Upload Section */
        #uploadContainer {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
            gap: 20px;
        }

        #fileInput {
            padding: 10px;
            background: white;
            border-radius: 5px;
            border: 1px solid #ccc;
        }

        #uploadBtn {
            padding: 10px 20px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        #uploadBtn:hover {
            background-color: #0056b3;
        }

        /* Output Section */
        #outputContainer {
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            width: 90%;
            margin-left: auto;
            margin-right: auto;
        }

        #imageContainer {
            width: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        #imageContainer img {
            max-width: 100%;
            max-height: 400px;
            border-radius: 5px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        }

        #textContainer {
            width: 50%;
            overflow: auto;
            max-height: 400px;
            padding: 10px;
            border-left: 1px solid #ccc;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }

        th, td {
            border: 1px solid black;
            padding: 10px;
            word-wrap: break-word;
            max-width: 300px;
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
        <input type="file" id="fileInput" multiple>
        <button id="uploadBtn">Upload and Process</button>
    </div>

    <h2>Uploaded Files and Results:</h2>

    <!-- Output Section -->
    <div id="outputContainer">
        <!-- Image will be displayed here -->
        <div id="imageContainer"></div>

        <!-- OCR Data Table will be displayed here -->
        <div id="textContainer"></div>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const uploadBtn = document.getElementById('uploadBtn');
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

            const result = await response.json(); // Assuming backend returns JSON

            // Clear previous content
            imageContainer.innerHTML = '';
            textContainer.innerHTML = '';

            // Display only the large uploaded image (No small image inside table)
            const file = fileInput.files[0];
            const reader = new FileReader();
            reader.onload = function (e) {
                imageContainer.innerHTML = `<img src="${e.target.result}" alt="Uploaded Image">`;
            };
            reader.readAsDataURL(file);

            // Convert JSON data into a table format
            let tableHTML = `<table><tr><th>Field</th><th>Value</th></tr>`;
            for (const key in result) {
                if (key !== "image") {  // Ensure "image" is not added to the table
                    tableHTML += `<tr><td>${key}</td><td>${result[key]}</td></tr>`;
                }
            }
            tableHTML += `</table>`;

            // Display table in textContainer
            textContainer.innerHTML = tableHTML;
            fileInput.value = ""; // Reset file input
        });
    </script>

</body>
</html>


