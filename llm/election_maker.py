from llm.prompts.loader import load_md
from llm.tools import process_election
from config import settings
from google import genai
import argparse, json

MD = load_md("election_maker")

client = genai.Client(api_key=settings.GEMINI_API_KEY)
model = "gemini-2.5-flash"

def call_gemini(user_input: str) -> dict:
    prompt = f""" 
{MD}

USER REQUEST:
{user_input}
"""
    
    response = client.models.generate_content(model=model, contents=prompt)

    if response.text: text = response.text.strip()
    else: raise ValueError("Invalid response")

    try: return json.loads(text)
    except Exception: raise

def run_planner(user_input: str):
    response = call_gemini(user_input)
    election_name = response["election_name"]
    description = response["description"]
    candidates = response["candidates"]
    target_size = response["target_size"]

    process_election(election_name, candidates, int(target_size))

    return {
        "election_name": election_name,
        "description": description,
        "candidates": candidates,
        "target_size": target_size,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str)
    args = parser.parse_args()
    result = run_planner(args.prompt)

    print("\nAGENT OUTPUT:\n")

    print(result["election_name"])
    print(result["description"])