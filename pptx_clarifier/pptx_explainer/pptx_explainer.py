import argparse
import asyncio
import json
from datetime import datetime

from sqlalchemy.orm import Session

from pptx_clarifier.db import engine
from pptx_clarifier.db.models import Upload
from pptx_clarifier.pptx_explainer import initial_prompt, explainer_logger as logger
from pptx_clarifier.pptx_explainer.openai_interactor import interact
from pptx_clarifier.pptx_explainer.presentation_parser import open_presentation, parse_slide


def create_slide_prompt(index, slide):
    """
    Prepares a slide prompt for the AI.

    Args:
        index (int): Index of the slide.
        slide (slide): Slide to be parsed.

    Returns:
        str: The prompt for the AI.
    """
    # Prepare the message input for the current slide
    parsed_slide = parse_slide(slide)
    slide_prompt = json.dumps({f"Slide-{index}": parsed_slide})

    # Return the message to the AI
    return slide_prompt


async def process_presentation(upload, session):
    """
    Opens a presentation and parses its slides to OpenAI chat prompts.
    Each prompt is sent to the AI asynchronously.

    Args:
        upload: Path to the presentation file.
        session: The database session.

    Returns:
        list: List of all responses from the AI.
    """
    messages = [{"role": "system", "content": initial_prompt}]

    # Open the presentation
    presentation = open_presentation(upload.get_upload_path())
    responses = {}
    upload.status = "pending"
    session.commit()

    # Parse each slide to prompt and send it to the AI asynchronously
    for index, slide in enumerate(presentation.slides, start=1):
        try:
            prompt = create_slide_prompt(index, slide)

            if prompt is None:
                responses[f"Slide {index}"] = "No text to clarify"
                
            else:
                res = await interact(prompt, messages)
                responses[f"Slide {index}"] = res

        except ConnectionError as connection_error:
            logger.error(connection_error)
            responses[f"Slide {index}"] = f"Could not clarify slide {index}"

    return responses


async def clarify(upload, session):
    """
    Generates explanations for a PowerPoint presentation and saves it to a JSON file.

    Args:
        upload : The uploaded presentation file object.
        session: The database session.

    Raises:
        PathError: If the path does not exist.
        ValueError: If the path is not a pptx file.
        Exception: If an error occurs while parsing the presentation.
    """
    logger.info(f'Clarifying {upload.filename}')
    explanations = await process_presentation(upload, session)

    with open(str(upload.get_output_path()), "w") as file:
        json.dump(explanations, file)

    logger.info(f'Finished clarifying {upload.filename}')


if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Script to clarify pptx files.')

    # Add an argument for the file path
    parser.add_argument('file_path', nargs=1, type=str, help='Path to the pptx file')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Extract the file path from the arguments
    file_path = args.file_path[0]

    # Check if the file path argument is missing
    if not file_path:
        parser.error('Please provide a path to the pptx file.')

    try:
        upload_file = Upload(upload_time=datetime.now(), filename=file_path, status="processing")
        # Call the function to process the file
        asyncio.run(clarify(upload_file))
    except Exception as e:
        print(e)
