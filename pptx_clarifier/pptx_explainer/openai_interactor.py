import argparse
import asyncio
import os

import openai
from dotenv import load_dotenv

from pptx_clarifier.pptx_explainer import explainer_logger as logger

load_dotenv()
apikey = os.getenv("OPENAI_API_KEY")

print(apikey)
openai.api_key = os.getenv("OPENAI_API_KEY")
# Set the maximum number of retries
max_retries = 3
# Set the timeout value (in seconds)
timeout = 100


async def retry_on_exception(attempt, exception):
    if attempt < max_retries:
        logger.warning(
            f"Request failed: {exception}\n trying again (attempt {attempt + 1} of {max_retries}).")
        await asyncio.sleep(attempt * 2)
    else:
        logger.error("Maximum number of retries reached. Abort.")
        raise ConnectionError("Maximum number of retries reached. Abort.")


async def interact(prompt: str, messages=None):
    """Interacts with the AI and returns the response

    Args:
        prompt (str): prompt to be sent to the AI
        messages (list, optional): list of messages to be sent to the AI. Defaults to None.

    Returns:
        str: response from the AI
    """
    # Create a list to store the messages
    if messages is None:
        messages = []
    ai_response = {}
    messages.append({"role": "user", "content": prompt})
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Sending prompt to the AI (prompt: {prompt})")
            # Add the message to the conversation and send it to the AI
            conversation = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
                request_timeout=timeout
            )
            ai_response = conversation["choices"][-1]
            # Check if the AI has finished processing the message
            if ai_response['finish_reason'] == "stop":
                messages.append(
                    {"role": "assistant", "content": ai_response["message"]["content"]})
                break

        # Handle exceptions that indicate a recoverable error
        except openai.error.APIError as api_error_exception:
            await retry_on_exception(attempt, api_error_exception)
        except openai.error.ServiceUnavailableError as service_error_exception:
            await retry_on_exception(attempt, service_error_exception)
        except openai.error.Timeout as timeout_exception:
            await retry_on_exception(attempt, timeout_exception)
    return ai_response["message"]["content"]


if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Script to interact with openai api.')

    # Add an argument for the file path
    parser.add_argument('prompt', nargs=1, type=str, help='Prompt string to send to the AI')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Extract the file path from the arguments
    prompt_arg = args.file_path

    # Check if the file path argument is missing
    if not prompt_arg:
        parser.error('Please provide a prompt string.')

    try:
        # Call the function to process the file
        asyncio.run(interact(prompt_arg))
    except Exception as e:
        print(e)
