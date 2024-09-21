import openai
import os

# Verify environment variables
openai_organization = os.getenv('OPENAI_ORGANIZATION')
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_organization:
    raise Exception("Missing value for OPENAI_ORGANIZATION environment variable.")

if not openai_api_key:
    raise Exception("Missing value for OPENAI_API_KEY environment variable.")

# Set OpenAI credentials
openai.organization = openai_organization
openai.api_key = openai_api_key

def check_openai_endpoint():
    try:
        # Send a simple test request to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5",
            messages=[{"role": "user", "content": "Hello, OpenAI!"}]
        )
        
        # Print the response
        print("OpenAI API is working!")
        print("Response from OpenAI:", response.choices[0].message['content'])
    except Exception as e:
        print(f"Failed to connect to OpenAI API: {e}")

# Run the check
check_openai_endpoint()
