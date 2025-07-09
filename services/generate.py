import os
import dotenv
import json
import re
import asyncio
from datetime import datetime

# Third-party imports
from pydantic import BaseModel
from google import genai
from google.genai import types

# Local imports (assuming prompts are in a separate file named 'prompt.py')
from . import prompt 

# --- Setup ---
dotenv.load_dotenv()  
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file. Please create one.")

client = genai.Client(api_key=GEMINI_API_KEY)


# --- Model Interaction Functions ---

def setup_initial_questions(topic: str) -> list[str]:
    """Generates a list of research branches for a given topic with grounding."""
    
    def try_extract_branches(response_text: str) -> list[str]:
        """Helper function to extract branches from response text"""
        # First try to extract JSON
        json_string = clean_json_from_response(response_text)
        if json_string:
            try:
                data = json.loads(json_string)
                branches = data.get("branches", [])
                if branches:
                    return branches
            except json.JSONDecodeError:
                print("Warning: Found JSON block but failed to parse it")
        
        # If JSON extraction fails, try to parse text manually
        print("Attempting to parse branches from raw text...")
        branches = parse_branches_from_text(response_text)
        if branches:
            return branches
        
        # If all else fails, return empty list
        print("Warning: Could not extract any branches from response")
        return []
    
    # Try different grounding configurations
    try:
        # For Gemini 2.0+ models, use googleSearch
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt.initialPrompt(topic),
            config=config,
        )
        
        print("Response received. Attempting to extract branches...")
        print(f"Raw response (first 500 chars): {response.text[:500]}...")
        
        return try_extract_branches(response.text)
            
    except Exception as e:
        if "Search Grounding is not supported" in str(e):
            print("Search grounding not supported for initial call, trying google_search_retrieval...")
            # Fallback: try google_search_retrieval
            try:
                grounding_tool = types.Tool(
                    google_search_retrieval=types.GoogleSearchRetrieval()
                )
                config = types.GenerateContentConfig(
                    tools=[grounding_tool]
                )
                
                response = client.models.generate_content(
                    model="gemini-2.5-pro",
                    contents=prompt.initialPrompt(topic),
                    config=config,
                )
                
                print("Response received from google_search_retrieval. Attempting to extract branches...")
                print(f"Raw response (first 500 chars): {response.text[:500]}...")
                
                return try_extract_branches(response.text)
                    
            except Exception as e2:
                print(f"google_search_retrieval also failed: {e2}")
                print("Using model without grounding...")
                # Final fallback: no grounding
                response = client.models.generate_content(
                    model="gemini-2.5-pro",
                    contents=prompt.initialPrompt(topic),
                )
                
                print("Response received without grounding. Attempting to extract branches...")
                print(f"Raw response (first 500 chars): {response.text[:500]}...")
                
                return try_extract_branches(response.text)
        else:
            raise e

def parse_branches_from_text(text: str) -> list[str]:
    """
    Attempts to parse branches from raw text if JSON extraction fails.
    Looks for numbered lists, bullet points, or other patterns.
    """
    branches = []
    
    # Try to find lines that look like branches
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Look for patterns like "1. Branch:", "Branch 1:", "- Branch:", etc.
        patterns = [
            r'^\d+\.\s*(.+)',  # "1. Something"
            r'^Branch\s*\d+:\s*(.+)',  # "Branch 1: Something"
            r'^-\s*(.+)',  # "- Something"
            r'^\*\s*(.+)',  # "* Something"
            r'^•\s*(.+)',  # "• Something"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                branch = match.group(1).strip()
                # Clean up quotes if present
                branch = branch.strip('"\'')
                if branch and len(branch) > 10:  # Reasonable length filter
                    branches.append(branch)
                break
    
    # If we still don't have branches, try a more aggressive approach
    if not branches:
        # Look for any line that contains question-like content
        for line in lines:
            line = line.strip()
            if len(line) > 20 and ('?' in line or 'analyze' in line.lower() or 'research' in line.lower()):
                branches.append(line)
    
    return branches[:15]  # Limit to 15 branches max

async def analyze_branch_ai_async(branch: str) -> tuple[str, str]:
    """
    Analyzes a single research branch using Google Search grounding asynchronously.
    Returns a tuple of (branch_name, raw_text_response) for later cleaning.
    """
    # Try different grounding configurations based on model version
    try:
        # For Gemini 2.0+ models, use googleSearch
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )
        
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash",
            contents=prompt.analyzePrompt(branch),
            config=config,
        )
        return branch, response.text
        
    except Exception as e:
        if "Search Grounding is not supported" in str(e):
            # Fallback: try without grounding
            print(f"  --> Search grounding not supported, using model without grounding for branch: '{branch}'")
            response = await asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt.analyzePrompt(branch),
            )
            return branch, response.text
        else:
            # Try the older google_search_retrieval format
            try:
                grounding_tool = types.Tool(
                    google_search_retrieval=types.GoogleSearchRetrieval()
                )
                config = types.GenerateContentConfig(
                    tools=[grounding_tool]
                )
                
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model="gemini-2.5-flash",
                    contents=prompt.analyzePrompt(branch),
                    config=config,
                )
                return branch, response.text
            except Exception:
                # Final fallback: no grounding
                print(f"  --> Both grounding methods failed, using model without grounding for branch: '{branch}'")
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model="gemini-2.5-flash",
                    contents=prompt.analyzePrompt(branch),
                )
                return branch, response.text

def structure_findings(topic: str, findings: list[str]) -> str:
    """
    Takes a list of all findings and synthesizes them into a single report.
    """
    class Result(BaseModel):
        full_report: str

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt.findingsPrompt(topic, findings),
        config={
            "response_mime_type": "application/json",
            "response_schema": Result,
        },
    )
    return response.parsed.full_report

def clean_json_from_response(raw_text: str) -> str | None:
    """
    Extracts a JSON string from within ```json ... ``` blocks in raw model output.
    """
    # Try to find ```json blocks first
    match = re.search(r"```json\s*(.*?)\s*```", raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Try to find generic ``` blocks
    match = re.search(r"```\s*(.*?)\s*```", raw_text, re.DOTALL)
    if match:
        content = match.group(1).strip()
        # Check if it looks like JSON
        if content.startswith('{') and content.endswith('}'):
            return content
    
    # Try to find JSON-like structures without code blocks
    match = re.search(r'(\{[^}]*"branches"[^}]*\})', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    return None

def clean_html_formatting(text: str) -> str:
    """
    Removes HTML-like formatting from text that the AI sometimes outputs.
    """
    # Replace common HTML-like tags with spaces
    html_patterns = [
        r'<br\s*/?>', r'<br>', r'</br>',
        r'<p\s*/?>', r'<p>', r'</p>',
        r'<div\s*/?>', r'<div>', r'</div>',
        r'<span\s*/?>', r'<span>', r'</span>',
        r'<strong\s*/?>', r'<strong>', r'</strong>',
        r'<b\s*/?>', r'<b>', r'</b>',
        r'<i\s*/?>', r'<i>', r'</i>',
        r'<em\s*/?>', r'<em>', r'</em>',
        r'<ul\s*/?>', r'<ul>', r'</ul>',
        r'<ol\s*/?>', r'<ol>', r'</ol>',
        r'<li\s*/?>', r'<li>', r'</li>',
        r'<h[1-6]\s*/?>', r'<h[1-6]>', r'</h[1-6]>',
        r'<a\s[^>]*>', r'<a>', r'</a>',
        r'<img\s[^>]*/?>', r'<img>', r'</img>',
    ]
    
    cleaned_text = text
    for pattern in html_patterns:
        cleaned_text = re.sub(pattern, ' ', cleaned_text, flags=re.IGNORECASE)
    
    # Clean up multiple spaces
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    return cleaned_text.strip()

async def analyze_all_branches_async(topics: list[str]) -> list[str]:
    """
    Analyzes all branches concurrently and returns all findings.
    """
    print(f"\n[2/3] Analyzing all {len(topics)} branches in parallel. This may take a while...")
    
    # Create tasks for all branches
    tasks = [analyze_branch_ai_async(branch) for branch in topics]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_findings = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"  --> Error analyzing branch [{i+1}/{len(topics)}]: {result}")
            continue
            
        branch, raw_response_text = result
        print(f"  -> Completed branch [{i+1}/{len(topics)}]: '{branch}'...")
        
        try:
            json_string = clean_json_from_response(raw_response_text)
            
            if json_string:
                data = json.loads(json_string)
                findings = data.get("findings", [])
                if findings:
                    print(f"  --> Found {len(findings)} new data points.")
                    all_findings.extend(findings)
                else:
                    print("  --> Warning: No findings were returned for this branch.")
            else:
                print(f"  --> Error: Could not find a valid JSON block in the response for branch: '{branch}'")
                print(f"  --> Response preview: {raw_response_text[:200]}...")
        except json.JSONDecodeError:
            print(f"  --> Error: Failed to decode JSON for branch '{branch}'. The model's response might be malformed.")
        except Exception as e:
            print(f"  --> An unexpected error occurred during analysis of branch '{branch}': {e}")
    
    return all_findings

# --- Main Execution Block ---

async def main():
    while True:
        try:
            topic = str(input('Name of the company for analysis: '))
            if topic.strip():
                break
            else:
                print('Input cannot be empty. Please enter a topic.')
                continue
        except (ValueError, EOFError):
            print('\nYou must enter a valid string!')
            continue
    
    print(f"\n[1/3] Generating initial research branches for: '{topic}'...")
    try:
        topics = setup_initial_questions(topic)
        if topics:
            print(f"-> Success! Found {len(topics)} branches to investigate.")
            for i, branch in enumerate(topics, 1):
                print(f"  {i}. {branch}")
        else:
            print("-> No branches were generated. This might be due to API issues or response format problems.")
            return
    except Exception as e:
        print(f"An error occurred while generating branches: {e}")
        return

    # Analyze all branches asynchronously
    all_findings = await analyze_all_branches_async(topics)
    
    if not all_findings:
        print("\nNo findings were collected. Cannot generate a final report. Exiting.")
        return
        
    print(f"\n[3/3] All branches analyzed. Compiling the final report from {len(all_findings)} total findings...")
    try:
        final_report_text = structure_findings(topic, all_findings)

        print("\n" + "="*25 + " FINAL RESEARCH REPORT " + "="*25)
        print(f"\nTopic: {topic}\n")
        print(final_report_text)
        print("\n" + "="*29 + " END OF REPORT " + "="*29)

    except Exception as e:
        print(f"A critical error occurred while generating the final report: {e}")

if __name__ == "__main__":
    asyncio.run(main())