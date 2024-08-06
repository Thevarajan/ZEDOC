from flask_uploads import UploadSet, configure_uploads, TEXT, UploadNotAllowed
from flask import request, redirect, flash, url_for
from werkzeug.utils import secure_filename
import os
import requests
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import time

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

text_files = UploadSet("text", TEXT)

mycursor = None


def set_app(app, mydb):
    global mycursor
    configure_uploads(app, (text_files,))
    mycursor = mydb.cursor()


def db_login(username, password):
    sql_login = ("SELECT * FROM login WHERE l_name=%s AND pass=%s")
    sql_logval = (username, password)
    mycursor.execute(sql_login, sql_logval)
    logresult = mycursor.fetchone()

    if logresult:
        user_id = logresult[0]
        return user_id
    else:
        return None


def db_signup(username, age, password):
    sql_signup = "INSERT INTO login (l_name, age, pass) VALUES (%s, %s, %s)"
    sql_signval = (username, age, password)
    mycursor.execute(sql_signup, sql_signval)
    mycursor.connection.commit()


def save_file_to_local(app, user_id=None):
    try:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            sql_insert = "INSERT INTO uploaded_files (user_id, file_name, file_path) VALUES (%s, %s, %s)"
            sql_values = (user_id, filename, file_path)
            mycursor.execute(sql_insert, sql_values)
            mycursor.connection.commit()

            return filename
        else:
            return "Invalid file format or no file provided."
    except UploadNotAllowed:
        return "File format not allowed."
    except Exception as e:
        print("Error while saving file to the local drive:", str(e))
        return None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_uploaded_files(folder_path):
    try:
        files = os.listdir(folder_path)
        return files
    except Exception as e:
        print("Error while getting the list of uploaded files:", str(e))
        return []


def generate_text(user_text):
    genai.configure(api_key="AIzaSyDOzWCcgTv2MPKd5OMqbHL2pgfJpSnCod0")
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]
    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    convo = model.start_chat(history=[])
    convo.send_message(user_text)
    return convo.last.text


def delete_file1(filename):
    folder_path = 'website\\uploads'
    file_path = os.path.join(folder_path, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'File "{filename}" deleted', 'success')

        sql_delete = "DELETE FROM uploaded_files WHERE file_name = %s "
        sql_values1 = (filename)
        mycursor.execute(sql_delete, sql_values1)
        mycursor.connection.commit()
    else:
        flash(f'File "{filename}" not found', 'danger')
    return redirect(url_for('views.file_list'))


def voice():
    # instantiating the Recognizer and Microphone classes
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    terminate = False
    while not terminate:
        try:
            # Setting up the text-to-speech engine
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[1].id)
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1.0)

            with mic as source:
                engine.say('Listening')
                engine.runAndWait()
                print("Listening...")

                # Converting speech-to-text
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                recognizer.dynamic_energy_threshold = True
                audio = recognizer.listen(source, 3, 10)
                audioText = recognizer.recognize_google(audio)
                print(audioText)
                audioText = audioText.lower()
                if audioText is not None:
                    terminate = True

        except sr.UnknownValueError:
            output = "Unable to recognize speech"
            print(output)
            engine.say(output)
            time.sleep(0.5)
            engine.say("retry")
            engine.runAndWait()
            terminate = False

        except sr.WaitTimeoutError:
            output = "You took too long"
            print(output)
            engine.say(output)
            time.sleep(0.5)
            engine.say("retry")
            engine.runAndWait()
            terminate = False

    return audioText
