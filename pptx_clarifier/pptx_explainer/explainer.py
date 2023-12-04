import asyncio
import os
from datetime import datetime

import openai.error
from sqlalchemy.orm import Session

from pptx_clarifier.pptx_explainer import explainer_logger as logger
from pptx_clarifier.pptx_explainer.pptx_explainer import clarify
from pptx_clarifier.db import engine
from pptx_clarifier.db.models import Upload


def scan_db(session):
    """
    Scan the database for files with status "started".

    Parameters:
    - session: SQLAlchemy session object.

    Returns:
    - List of Upload objects with status "started".
    """
    uploads = session.query(Upload).filter_by(status="started").all()
    return uploads


def error_handler(upload, session, error: Exception):
    """
    Handle errors during the processing of an upload.

    Parameters:
    - upload: Upload object.
    - session: SQLAlchemy session object.
    - error: Exception object representing the encountered error.
    """
    logger.error(f"Error processing {upload.filename}: {error}")

    # Remove the uploaded file
    upload_path = str(upload.get_upload_path)
    os.remove(upload.get_upload_path())
    logger.info(f"Removed {upload.get_upload_path}")

    # Update the status in the database to "failed"
    upload.status = "failed"
    session.commit()
    session.close()


async def explainer():
    """
    Continuously scan the database for files with status "started" and process them.

    This function runs in an infinite loop, scanning for new uploads, processing them,
    and updating their status in the database.
    """
    while True:
        session = Session(bind=engine)

        # Scan the uploads directory for files with status "started"
        unprocessed_uploads = scan_db(session)

        for upload in unprocessed_uploads:
            try:
                # Update the status in the database to "processing"
                upload.status = "processing"
                session.commit()
                logger.info(f"Processing {upload.filename}")

                # Call the clarify function to process the upload
                await clarify(upload, session)

                logger.info(f"Finished processing {upload.filename}")

                # Update the status in the database to "finished"
                upload.status = "finished"
                upload.finish_time = datetime.now()
                session.commit()
                session.close()

            except FileNotFoundError as file_not_found_error:
                error_handler(upload, session, file_not_found_error)
                return
            except ValueError as value_error:
                error_handler(upload, session, value_error)
                return
            except openai.error.OpenAIError as openai_error:
                error_handler(upload, session, openai_error)
                return
            except Exception as e:
                # Log any other unexpected errors
                logger.error(f"Error: {e}")
                session.close()

        # Wait for 5 seconds before scanning for new uploads
        await asyncio.sleep(5)


if __name__ == "__main__":
    # Run the explainer function using asyncio
    asyncio.run(explainer())
