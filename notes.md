# Run bot - python3 -m bot.bot (from Telegram_bot directory)

# Gmail Tool - 

Sure! You can build a tool for reading and writing emails using **Gmail API** in Python, alongside LangGraph for orchestrating the actions (read and write). I'll break it down into manageable parts. Here's the overall workflow for this tool:

1. **Read Action**:
   - Check today’s date using Python’s `datetime` module.
   - Fetch unread emails for the day from Gmail using Gmail API.
   - Summarize the emails and highlight important content.
   
2. **Write Action**:
   - Take a list of email IDs and a context message.
   - Draft and send an email via Gmail API.

I'll walk you through each part.

---

### Prerequisites

- **Gmail API Setup**: You’ll need to set up **OAuth 2.0** credentials to access Gmail API. If you haven't set it up, follow the steps in the [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart).
  
- **Required Libraries**:
   - Install the required libraries:
   ```bash
   pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
   pip install langgraph
   ```

### 1. **Gmail API Client**

We'll start by creating a helper class to interact with the Gmail API.

#### Step 1.1: Gmail API Client Setup

```python
import os
import base64
import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

class GmailAPI:
    def __init__(self):
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate and create the Gmail API service."""
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        # Build the Gmail API client
        self.service = build('gmail', 'v1', credentials=creds)

    def get_today_emails(self):
        """Fetch emails from today."""
        today = datetime.date.today().strftime('%Y/%m/%d')
        try:
            results = self.service.users().messages().list(userId='me', q=f"after:{today}").execute()
            messages = results.get('messages', [])
            emails = []
            if not messages:
                return "No new emails."
            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                snippet = msg['snippet']  # Get the email snippet (summary)
                emails.append(snippet)
            return emails
        except HttpError as error:
            return f"An error occurred: {error}"

    def send_email(self, to_emails, subject, body):
        """Send email to list of recipients."""
        try:
            message = self.create_message("me", to_emails, subject, body)
            send_message = self.service.users().messages().send(userId="me", body=message).execute()
            return f"Message sent to {to_emails}"
        except HttpError as error:
            return f"An error occurred: {error}"

    def create_message(self, sender, to, subject, body):
        """Create a message for sending."""
        message = MIMEText(body)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}
```

#### Step 1.2: Handling Email Content

- The `get_today_emails()` function filters emails from today based on the current date, extracts snippets, and returns them.
- The `send_email()` function drafts an email and sends it to the provided recipients.
  
### 2. **LangGraph Integration: Read and Write Actions**

Now, let's integrate the email actions into a **LangGraph node** to allow the agent to choose between `read` and `write` actions.

#### Step 2.1: Create LangGraph Nodes for Read and Write Actions

```python
from langgraph import Node
import datetime
from email.mime.text import MIMEText

# Define actions for reading and writing emails
def read_emails_action() -> str:
    """Reads all the emails from today, summarizes them, and highlights important info."""
    gmail_api = GmailAPI()
    emails = gmail_api.get_today_emails()
    
    if isinstance(emails, str):  # If it's an error message
        return emails

    # Summarize the emails (basic version, can be improved)
    email_summary = "\n".join(emails)
    # Highlight important emails
    important_emails = [email for email in emails if 'important' in email.lower()]
    
    return f"Email Summary:\n{email_summary}\n\nImportant Emails:\n{', '.join(important_emails)}"

def write_email_action(recipients: list, subject: str, body: str) -> str:
    """Writes and sends an email to the specified recipients."""
    gmail_api = GmailAPI()
    result = gmail_api.send_email(recipients, subject, body)
    return result

# Create LangGraph nodes for actions
read_node = Node(func=read_emails_action, name="Read Emails")
write_node = Node(func=write_email_action, name="Write Email")
```

#### Step 2.2: Create LangGraph Graph

You can create a **LangGraph graph** that includes these two actions, and the agent can decide which action to take.

```python
from langgraph import Graph

# Initialize the Graph
graph = Graph()

# Add the read and write nodes to the graph
graph.add_node(read_node)
graph.add_node(write_node)

# Function to interact with the tool
def perform_action(action: str, *args):
    if action == "read":
        return graph.run()  # Executes read_emails_action
    elif action == "write":
        if len(args) < 3:
            return "Error: Write action requires recipients, subject, and body."
        recipients, subject, body = args
        return graph.run(recipients=recipients, subject=subject, body=body)  # Executes write_email_action
    else:
        return "Invalid action. Please choose either 'read' or 'write'."

# Example usage
# Perform a read action (fetch today's emails)
print(perform_action('read'))

# Perform a write action (send an email)
recipients = ["example@example.com"]
subject = "Meeting Update"
body = "Hello, just a quick update about the meeting tomorrow."
print(perform_action('write', recipients, subject, body))
```

### 3. **Using the Tool**

Now, you can use the `perform_action` function to decide whether to read or write emails based on user input:

- **Read Emails**: The `read` action fetches and summarizes today's emails, highlighting any important content.
- **Write Emails**: The `write` action takes a list of email IDs, a subject, and a body and sends an email to the recipients.

### Example Interaction:

1. **Read Emails**: 
   ```python
   print(perform_action('read'))
   ```

   Output:
   ```
   Email Summary:
   "Today's email about project updates..."
   Important Emails: "Meeting tomorrow"
   ```

2. **Write Emails**: 
   ```python
   recipients = ["example@example.com"]
   subject = "Meeting Update"
   body = "Hello, just a quick update about the meeting tomorrow."
   print(perform_action('write', recipients, subject, body))
   ```

   Output:
   ```
   Message sent to ['example@example.com']
   ```

---

### Conclusion

This tool is now capable of:

- **Reading Emails**: It checks for today's emails, summarizes them, and highlights important content.
- **Writing Emails**: It drafts and sends an email to the provided recipients.

This is a simple implementation, and you can extend it to handle more complex use cases like categorizing emails, improving the summarization (e.g., by using a language model), or enhancing error handling. 

If you need more specific features (like using AI to summarize or highlight more effectively), I can help you extend this further. Let me know if you'd like to dive deeper!


# Directory Structure
Telegram_Agent/
│── bot.py                  # Main entry point for the Telegram bot
│── .env                    # Environment variables (API keys)
│── requirements.txt         # Dependencies list
│── README.md               # Documentation
│
├───config/
│   │── settings.py          # Loads environment variables & configuration
│
├───agent/
│   │── __init__.py          # Makes this a Python module
│   │── langraph_agent.py    # Defines Langraph AI Agent logic
│   │── memory.py            # Handles context & memory for conversations
│   │── tools/
│       │── __init__.py          # Makes this a Python module
│       │── google_calendar.py          
│       │── calling_tool.py          
│       │── gmail.py             
│
├───handlers/
│   │── __init__.py          # Makes this a Python module
│   │── commands.py          # Handles Telegram commands (e.g., /start)
│   │── messages.py          # Handles text messages
│   │── media.py             # Handles images, voice, and videos
│
├───logs/
│   │── bot.log              # Stores logs for debugging
│
├───tests/
│   │── test_agent.py        # Unit tests for Langraph agent
│   │── test_bot.py          # Unit tests for Telegram bot
│
└───deployment/
│    │── docker-compose.yml   # Docker setup for deployment
│    │── deploy.sh            # Script to deploy the bot on a cloud server