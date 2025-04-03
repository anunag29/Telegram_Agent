from langchain_core.tools import tool
from langchain_community.agent_toolkits import GmailToolkit 
from langchain_community.tools.gmail.utils import build_resource_service, get_gmail_credentials


toolkit = GmailToolkit()

credentials = get_gmail_credentials(
    token_file="token.json",
    scopes=["https://mail.google.com/"],
    client_secrets_file="credentials.json",
)
api_resource = build_resource_service(credentials=credentials)
toolkit = GmailToolkit(api_resource=api_resource)

gmail_tools = toolkit.get_tools()[:3]

# for i, tool in enumerate(gmail_tools):
#     print(f"{i+1} {tool.name}")


# @tool
# def search_gmail_tool(raw_text: str, a: int, b: int = 1) -> int:
#     """
#     Takes two integer values and returns the multiplication of the two integers.

#     Args:
#         a (int) : first integer value
#         b (int) : second integer value (if not provided then default value is 1)

#     Returns:
#         result (int) : returns a integer value that is the multiplication of the both the integers
#     """
#     result = a*b

#     return f"Mulitplication result of {a}x{b} = {result}"