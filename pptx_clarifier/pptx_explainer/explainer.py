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
    # Scan the Database for files with status "started"
    uploads = session.query(Upload).filter_by(status="started").all()
    return uploads


def error_handler(upload,session, error: Exception):

    logger.error(f"Error processing {upload.filename}: {error}")
    upload_path = str(upload.get_upload_path)
    os.remove(upload.get_upload_path())
    logger.info(f"Removed {upload.get_upload_path}")
    upload.status = "failed"
    session.commit()
    session.close()


async def explainer():
    while True:
        session = Session(bind=engine)
        # Scan the uploads directory for files
        unprocessed_uploads = scan_db(session)
        for upload in unprocessed_uploads:
            try:
                upload.status = "processing"
                session.commit()
                logger.info(f"Processing {upload.filename}")
                await clarify(upload,session)
                logger.info(f"Finished processing {upload.filename}")
                upload.status = "finished"
                upload.finish_time = datetime.now()
                session.commit()
                session.close()
            except FileNotFoundError as file_not_found_error:
                error_handler(upload, file_not_found_error)
                return
            except ValueError as value_error:
                error_handler(upload, value_error)
                return
            except openai.error.OpenAIError as openai_error:
                error_handler(upload, openai_error)
                return
            except Exception as e:
                logger.error(f"Error: {e}")
                session.close()
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(explainer())
