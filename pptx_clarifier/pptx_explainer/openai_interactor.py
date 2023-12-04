import argparse
import asyncio
import os

import openai
from dotenv import load_dotenv

from pptx_clarifier.pptx_explainer import explainer_logger as logger

# Load environment variables from the .env file
load_dotenv()

# Get OpenAI API key from environment variables
apikey = os.getenv("OPENAI_API_KEY")

# Print the API key for verification purposes
print(apikey)

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set the maximum number of retries for API requests
max_retries = 3

# Set the timeout value (in seconds) for API requests
timeout = 100


async def retry_on_exception(attempt, exception):
    """
    Retry logic for handling exceptions during API requests.

    Parameters:
    - attempt: The current attempt number.
    - exception: The exception raised during the API request.
    """
    if attempt < max_retries:
        logger.warning(
            f"Request failed: {exception}\n Trying again (attempt {attempt + 1} of {max_retries}).")
        await asyncio.sleep(attempt * 2)
    else:
        logger.error("Maximum number of retries reached. Abort.")
        raise ConnectionError("Maximum number of retries reached. Abort.")


async def interact(prompt: str, messages=None):
    """
    Interacts with the AI and returns the response.

    Parameters:
    - prompt (str): The prompt to be sent to the AI.
    - messages (list, optional): List of messages to be sent to the AI. Defaults to None.

    Returns:
    - str: Response from the AI.
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
    parser = argparse.ArgumentParser(description='Script to interact with OpenAI API.')

    # Add an argument for the prompt
    parser.add_argument('prompt', nargs=1, type=str, help='Prompt string to send to the AI')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Extract the prompt from the arguments
    prompt_arg = args.prompt[0]

    # Check if the prompt argument is missing
    if not prompt_arg:
        parser.error('Please provide a prompt string.')

    try:
        # Call the function to interact with the AI and print the response
        asyncio.run(interact(prompt_arg))
    except Exception as e:
        print(e)
