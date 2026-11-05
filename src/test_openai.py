
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load the API key from the .env file
load_dotenv()

# Check whether the API key exists
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OpenAI API key not found. Please check your .env file."
    )

print("API key detected.")
print("Connecting to OpenAI...")

# Initialise the language model
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# Send a test question to the model
response = llm.invoke(
    "Explain in two sentences what a sole proprietorship is in Singapore."
)

# Display the response
print("\nOpenAI response:")
print(response.content)
