import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, make_response
from sqlalchemy.orm import sessionmaker, Session

from pptx_clarifier.pptx_clarifier_api import api_logger as logger
from pptx_clarifier.db import engine
from pptx_clarifier.db.models import User, Upload

load_dotenv()

app = Flask(__name__)


def process_file(uploaded_file, email):
    """
    Process the uploaded file and save it to the uploads folder.
    Args:
        uploaded_file: The original file name.
        email: The email address of the user who uploaded the file.

    Returns:
        The UUID of the uploaded file.
    """

    user = None
    session = Session(bind=engine)
    if email:
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(email=email)
            session.add(user)
            session.commit()
    upload = Upload(filename=uploaded_file.filename, upload_time=datetime.now(), status="started")
    session.add(upload)
    session.commit()
    if user:
        upload.user_id = user.id
        session.add(upload)
        user.uploads.append(upload)
        session.commit()

    else:
        session.add(upload)
        session.commit()

    # Save the uploaded file with the new name
    uploaded_file.save(upload.get_upload_path())
    session.close()
    return upload.uid


@app.post('/upload')
def save_file():
    """
    Upload a file to the server.

    Returns:
        A JSON object containing the UUID of the uploaded file.
    """

    uploaded_file = request.files['file']
    email = request.form.get('email')

    file_uuid = process_file(uploaded_file, email)
    logger.info(f"file uploaded with uid: {file_uuid}")
    return make_response({"file_uuid": file_uuid, "message": "file uploaded successfully"}, 200)


@app.get('/upload')
def upload_file():
    return "<form action=\"\" method=\"post\" enctype=\"multipart/form-data\">" \
           "<input type=\"file\" name=\"file\" />" \
           "<input type=\"submit\" value=\"Upload\" />" \
           "</form>"


@app.get('/status')
def get_status():
    """
    Get the status of the uploaded file. If the file is processed, return the explanation.

    Returns:
        A JSON object containing the status of the uploaded file.
    """

    upload = None
    session = Session(bind=engine)

    # Get the UUID of the uploaded file from the query string
    file_uuid = request.args.get('uuid')

    email = request.args.get('email')
    filename = request.args.get('filename')

    if file_uuid:
        upload = session.query(Upload).filter_by(uid=file_uuid).first()

    elif email and filename:
        user = session.query(User).filter_by(email=email).first()
        if user:
            upload = session.query(Upload).filter_by(user=user, filename=filename).first()

    if not upload:
        return make_response({"status": "not found"}, 404)

    explanation = upload.explanation()
    # initialize the response body
    response_body = {
        "filename": upload.filename,
        "timestamp": upload.upload_time,
        "explanation": explanation,
        "status": upload.status
    }

    return make_response(response_body, 200)


if __name__ == "__main__":
    app.run()
