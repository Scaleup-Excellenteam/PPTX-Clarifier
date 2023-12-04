# PPTX Clarifier

PPTX Clarifier is a system for clarifying PowerPoint presentations using AI. It consists of several components, including a web API, a client for interacting with the AI, and an explainer for processing presentations.

## Components

### 1. Web API

The web API allows users to upload PowerPoint presentations for clarification and check the status of the clarification process. It is built using Flask.

#### Installation

```bash
pip install -r requirements.txt
```

#### Usage
Run the web API using the following command:

```bash
python pptx_clarifier/pptx_clarifier_api/web_api.py
```

### 2. Client
   The client provides a simple interface for interacting with the web API. 
   It allows users to upload presentations and check the status of their clarification.

#### Installation

```bash
pip install -r requirements.txt
```

#### Usage

```bash
from pptx_clarifier.client import upload, status

# Example: Upload a presentation
file_uuid = upload("path/to/presentation.pptx")
print(f"File uploaded successfully. UUID: {file_uuid}")

# Example: Check the status of a presentation
file_uuid = "12345678-1234-5678-1234-567812345678"
file_status = status(file_uuid)
print(file_status)
```

### 3. Explainer
   The explainer is a background process that continuously scans the database 
   for presentations with the status "started" and processes them for clarification.

#### Installation

```bash
pip install -r requirements.txt
```

#### Usage

```bash
python pptx_clarifier/pptx_explainer/explainer.py
```

#### Database

The system uses SQLite as the database. The database file is located
at <b>pptx_clarifier/db/pptx_clarifier.db.</b>

#### Initialize Database

```bash
python pptx_clarifier/db/start_db.py
```

#### Logging
The system utilizes logging for better tracking of operations.
Log files are stored in the logs directory.

#### Configuration
Ensure you have the necessary environment variables set in a .env file:

```env
OPENAI_API_KEY=your_openai_api_key
```