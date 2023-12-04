import asyncio
import os
import sys
import threading

from pptx_clarifier import logger
from pptx_clarifier.client.client import upload, status
from pptx_clarifier.db import start_db
from pptx_clarifier.pptx_clarifier_api import web_api
from pptx_clarifier.pptx_explainer import explainer

# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.realpath(__name__)))

# __all__ list to specify the symbols to be imported when using wildcard import
__all__ = ['client', 'explainer', 'web_api', 'logger']

def main():
    # Initialize the database
    start_db()

    # Run the explainer component using asyncio
    asyncio.run(explainer.explainer())

if __name__ == '__main__':
    # Initialize the database
    start_db()

    # Create and start two threads for running the web API and the main function
    thread1 = threading.Thread(target=web_api.app.run, args=[])
    thread2 = threading.Thread(target=main, args=[])

    # Start the threads
    thread1.start()
    thread2.start()

    # Wait for both threads to finish
    thread1.join()
    thread2.join()
