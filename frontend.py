import face_recognition
from PIL import Image, ImageDraw
from flask import Flask, render_template, request, url_for, send_from_directory, redirect
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['PROCESSED_FOLDER'] = os.path.join(os.getcwd(), 'identify')


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route("/register", methods=['POST'])
def register():
    if request.method == 'POST':
        f = request.files['file']
        name = request.form['text']
        if(f.filename == "" or name == ""):
            return redirect("/")
        filename, file_extension = os.path.splitext(f.filename)
        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'img', 'known',
                                 secure_filename(name + file_extension))
        f.save(file_path)

        new_face_image = face_recognition.load_image_file(file_path)
        new_face_encoding = face_recognition.face_encodings(new_face_image)[0]

        known_face_encodings.append(new_face_encoding)
        known_face_names.append(name)

    return redirect('/')


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        f = request.files['file']
        if(f.filename == ""):
            return redirect("/")
        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        test_image = face_recognition.load_image_file(file_path)
        face_locations = face_recognition.face_locations(test_image)
        face_encodings = face_recognition.face_encodings(
            test_image, face_locations)
        # Convert to PIL format
        pil_image = Image.fromarray(test_image)
        # Create a ImageDraw instance
        draw = ImageDraw.Draw(pil_image)
        # Loop through faces in test image
        for(top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding)
            name = "Unknown Person"
            # If match
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
            # Draw box
            draw.rectangle(((left, top), (right, bottom)),
                           outline=(255, 255, 0))
            # Draw label
            text_width, text_height = draw.textsize(name)
            draw.rectangle(((left, bottom - text_height - 10),
                            (right, bottom)), fill=(255, 255, 0), outline=(255, 255, 0))
            draw.text((left + 6, bottom - text_height - 5),
                      name, fill=(0, 0, 0))

        del draw
        # Save image
        pil_image.save(f'identify/identify{f.filename}')
        result = f'identify{f.filename}'
        return render_template('home.html', result=result)


@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)


if __name__ == '__main__':

    known_face_encodings = []
    known_face_names = []
    directory = os.path.join(os.getcwd(), 'img', 'known')
    print(os.listdir(directory))
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        face_image = face_recognition.load_image_file(filepath)
        face_encoding = face_recognition.face_encodings(face_image)[0]

        filename, file_extension = os.path.splitext(filename)

        known_face_encodings.append(face_encoding)
        known_face_names.append(filename)

    app.run(debug=True)
