import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from prompts import TEACHING_RESPONSE_PROMPT
from questions import QUESTIONS

# Load environment variables from the .env file
load_dotenv(override=True)

# Check that the OpenAI API key exists
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY was not found. "
        "Add it to your .env file before running this script."
    )

# Create the OpenAI client
client = OpenAI(api_key=api_key)

# Identify the project root folder
project_root = Path(__file__).resolve().parent.parent

# Define the output dataset path
output_file = project_root / "data" / "sft_dataset.jsonl"
with open(output_file, "w", encoding="utf-8") as file:
     for question in QUESTIONS:
        try:
            # Insert the question into the teaching prompt    
            formatted_prompt = TEACHING_RESPONSE_PROMPT.format(
            question=question
            )

            # Send the prompt to GPT
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": formatted_prompt,
                    }
                ],
            )


            # Extract the generated teaching response
            teaching_response = response.choices[0].message.content

            if not teaching_response:
                raise ValueError("GPT returned an empty response.")


            # Create one supervised fine-tuning example
            training_example = {
                "messages": [
                    {
                        "role": "user",
                        "content": question,
                    },
                    {
                        "role": "assistant",
                        "content": teaching_response,
                    },
                ]
            }


            # Make sure the data folder exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Save one JSON object as one line in the JSONL file
            file.write(
                json.dumps(training_example, ensure_ascii=False) + "\n"
            )

        except Exception as e:
            print(f"✗ {question}")
            print(f"Error: {e}")
