import face_recognition
from PIL import Image, ImageDraw
from flask import Flask, render_template, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['PROCESSED_FOLDER'] = os.path.join(os.getcwd(), 'identify')


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        test_image = face_recognition.load_image_file(
            f'./uploads/{f.filename}')

        # Find faces in test image
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
            draw.rectangle(((left, bottom - text_height - 10), (right,
                                                                bottom)), fill=(255, 255, 0), outline=(255, 255, 0))
            draw.text((left + 6, bottom - text_height - 5),
                      name, fill=(0, 0, 0))

        del draw

        # Display image
        # pil_image.show()

        # Save image
        pil_image.save(f'identify/identify{f.filename}')
        result = f'identify{f.filename}'
        return render_template('index.html', result=result)


@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)


if __name__ == '__main__':
    image_of_bill = face_recognition.load_image_file('./img/known/Teddy.jpeg')
    bill_face_encoding = face_recognition.face_encodings(image_of_bill)[0]

    image_of_steve = face_recognition.load_image_file(
        './img/known/Steve Jobs.jpg')
    steve_face_encoding = face_recognition.face_encodings(image_of_steve)[0]

    image_of_elon = face_recognition.load_image_file(
        './img/known/Elon Musk.jpg')
    elon_face_encoding = face_recognition.face_encodings(image_of_elon)[0]

    #  Create arrays of encodings and names
    known_face_encodings = [
        bill_face_encoding,
        steve_face_encoding,
        elon_face_encoding
    ]

    known_face_names = [
        "Teddy",
        "Steve Jobs",
        "Elon Musk"
    ]
    app.run(debug=True)
