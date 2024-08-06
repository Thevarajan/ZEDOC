from flask import Blueprint, render_template, redirect, request, current_app, send_file, jsonify
from .models import save_file_to_local, get_uploaded_files, generate_text, delete_file1, voice
import os, asyncio
import base64

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return redirect("/login")

@views.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' in request.files:
            saved_filename = save_file_to_local(current_app)
            if saved_filename:
                return 'File uploaded successfully'

    return render_template('new_manager.html')

@views.route('/file_list')
def file_list():
    folder_path = current_app.config['UPLOAD_FOLDER']
    files = get_uploaded_files(folder_path)
    return render_template('new_file_list.html', files=files)

@views.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    folder_path = 'uploads'
    return send_file(os.path.join(folder_path, filename), as_attachment=True)

@views.route('/process', methods=['GET', 'POST'])
def process_text():
    if request.method == 'POST':
        user_text = request.form['user_text']
        out1 = generate_text(user_text)
        return render_template('new_chat.html', text=out1)
    else:
        return render_template('new_chat.html', text="")

@views.route('/delete/<filename>', methods=['GET'])
def delete_file(filename):
    del1=delete_file1(filename)
    return del1

@views.route('/open/<filename>', methods=['GET', 'POST'])
def open_file(filename):
    folder_path = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(folder_path, filename)

    try:
        file_extension = os.path.splitext(filename)[1].lower()

        if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
            with open(file_path, 'rb') as file:
                file_contents = base64.b64encode(file.read()).decode('utf-8')
            return render_template('open_file.html', filename=filename, contents=file_contents)

        try:
            if request.method == 'POST':
                new_content = request.form['file_content']
                with open(file_path, 'w') as file:
                    file.write(new_content)
                return redirect('/file_list')

            with open(file_path, 'r') as file:
                file_contents = file.read()

            return render_template('open_file.html', filename=filename, contents=file_contents)
        except FileNotFoundError:
            return "File not found", 404
    except FileNotFoundError:
        return "File not found", 404

@views.route('/voice', methods=['GET', 'POST'])
def process_text1():
    if request.method == 'POST':
        try:
            user_text = voice()
            out1 = generate_text(user_text)
            return render_template('new_chat.html', text=out1)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)  # Log the error
            return render_template('new_chat.html', text=error_message)
    else:
        return render_template('new_chat.html', text="")

