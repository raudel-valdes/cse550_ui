from flask import Flask, flash, render_template, url_for, request, jsonify, redirect, send_from_directory
from werkzeug.utils import secure_filename
import xmlrpc.client
import os

UPLOAD_FOLDER = './uploaded_images'
PROCESSED_FOLDER = './processed_images'
TEMPLATES_FOLDER = './static'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['TEMPLATES_FOLDER'] = TEMPLATES_FOLDER

@app.route('/')
def index():
    return render_template('interface.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_type(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower()

@app.route('/uploadImage', methods=['GET','POST'])
def uploadImage():
    if request.method == 'POST':
        if 'file' in request.files:
            flash('No file part')
            file = request.files['file']

            if file.filename != '':
                flash('No selected file')

                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    return redirect(url_for('sendImage', filename=filename))

    return "Error"
    
@app.route('/sendImage/<filename>')
def sendImage(filename):
    fileType = file_type(filename)
    serverMethods = xmlrpc.client.ServerProxy('http://ec2-34-224-62-1.compute-1.amazonaws.com:8080')

    imageToProcessFilePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(imageToProcessFilePath, "rb") as handle:
        binary_data = xmlrpc.client.Binary(handle.read())
        filterList = ["noise","contrast"]
        imageData = serverMethods.processImage(binary_data, fileType, filterList).data

    processedImageFilePath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    with open(processedImageFilePath, "wb") as handle:
        handle.write(imageData)

    displayProcessedImgFilePath = os.path.join(app.config['TEMPLATES_FOLDER'], filename)
    with open(displayProcessedImgFilePath, "wb") as handle:
        handle.write(imageData)

    print(displayProcessedImgFilePath)
    return render_template('interface.html', filename = filename)

@app.route('/static/<filename>')
def displayFile(filename):
    return send_from_directory(TEMPLATES_FOLDER, filename)

# @app.context_processor
# def override_url_for():
#     return dict(url_for=dated_url_for)

# def dated_url_for(endpoint, **values):
#     if endpoint == 'static':
#         filename = values.get('filename', None)
#         if filename:
#             file_path = os.path.join(app.root_path,
#                                  endpoint, filename)
#             values['q'] = int(os.stat(file_path).st_mtime)
#     return url_for(endpoint, **values)

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

app.debug = True
app.run()