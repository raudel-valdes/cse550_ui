from flask import Flask, flash, render_template, url_for, request, jsonify, redirect, send_from_directory
from werkzeug.utils import secure_filename
import xmlrpc.client
import os

UPLOAD_FOLDER = './uploaded_images'
PROCESSED_FOLDER = './processed_images'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

@app.route('/uploadImage')
def index():
    return render_template('Interface.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_type(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('sendImage', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''                                 
@app.route('/sendImage/<filename>')
def sendImage(filename):
    fileType = file_type(filename)
    serverMethods = xmlrpc.client.ServerProxy('http://ec2-34-224-62-1.compute-1.amazonaws.com:8080')

    imageToProcessFilePath = app.config['UPLOAD_FOLDER'] + '/' + filename
    with open(imageToProcessFilePath, "rb") as handle:
        binary_data = xmlrpc.client.Binary(handle.read())
        filterList = ["noise","contrast"]
        imageData = serverMethods.processImage(binary_data, fileType, filterList).data

    processedImageFilePath = app.config['PROCESSED_FOLDER'] + '/' + filename
    with open(processedImageFilePath, "wb") as handle:
        handle.write(imageData)

    return ("Sucess")

if __name__ == "__main__":
    app.run(debug=True)