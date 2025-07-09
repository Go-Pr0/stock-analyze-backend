from datetime import datetime
current_date = datetime.now().strftime("%Y-%m-%d")
def initialPrompt(topic):
    return f"""
You are a strategic research planner with access to current web search capabilities. Your task is to break down a complex topic into distinct, manageable research branches while leveraging the most current information available.

Company/topic to analyze: the {topic} company & future outlook for it

FIRST: For research into a company topics always at least look at these topics
- Recent developments and news
- Technical specifications or features
- Regulatory or legal aspects
- Other branches of the company
- Competitive landscape 
- General outlook of the market they're in
- Expert opinions and analyses
- Industry reports and studies
- Other items related to the topic

THEN: Based on your research findings, generate at least 10-15 focused research branches or subtopics. Each branch must be a clear, concise question or area of investigation that allows for a narrow, well-defined scope. The branches should cover different facets of the topic to form a comprehensive overview when combined.

Use the initial sources you found to inform the creation of these branches - they should reflect current, relevant aspects of the topic that warrant deeper investigation.

IMPORTANT FORMATTING RULES:
- Format the subtopics in such a way that it doesn't imply any bias
- Example: "Analyze why the chinese market is slowing down" becomes "analyze the current state of the chinese market in relation to..."
- These questions should each give context you need to answer the main question
- Do NOT include the main question as one of these branches
- Each branch should be focused on a specific aspect or angle

Return the branches in this exact JSON format:
```json
{{
 "branches": [
 "Branch 1: [subtopic based on current research]",
 "Branch 2: [subtopic based on current research]",
 "Branch 3: [subtopic based on current research]",
 ...
 ]
}}
```

Make sure each branch represents a different subject area or perspective related to the main topic, informed by your initial web research.
**Current date for context & querying:** [{current_date}]
"""

def analyzePrompt(branch):
    return f"""
You are a focused research agent. Your task is to conduct in-depth, neutral research on a specific sub-topic or "branch." Use the provided Google Search tool to find verifiable information.

Your research must be strictly limited to the branch provided. Do not investigate other areas.

**Branch to explicitly research using Google Search:** [{branch}]
**Current date for context:** [{current_date}]

Your goal is to gather multiple distinct facts or "findings" related *only* to this branch. Review numerous search results to ensure a comprehensive view. Synthesize what you learn into a list of factual statements.

Return your findings in the following JSON format, enclosed in ```json ... ```. Do not add any other text, explanation, or conversational filler outside the JSON block.

```json
{{
"findings": ["finding 1", "finding 2", "finding 3", "...", "finding N"]
}}

All findings should be literally stated by the sources. Each finding should contain a date for when it happened.

It's key that you keep a critical look on things.
"""

def findingsPrompt(topic: str, findings_list: list[str]):
    formatted_findings = "\n".join(f"- {finding}" for finding in findings_list)
    full_prompt = f"""
    You are a senior research analyst. You have been provided with a series of raw data points and findings from various research branches. Your job is to synthesize these disparate findings into a single, coherent, and objective report.

    The main company of the research report is:
    {topic}

    Instructions:
    Based only on the extensive analysis provided below, generate the final report. You must:

    Structure the information logically.
    Identify key themes and draw connections between different findings.
    Present the information in a clear, professional narrative.
    Maintain a completely neutral and objective tone.
    Format the report for easy reading using necessary formatting: ## for headings, ** for bold, * for bullets, and \n for line breaks. 
    Do not use <br></br>
    The final output must be in this exact JSON format:
    {{
    "full_report": "The full, synthesized report text goes here."
    }}

    --- START OF RAW FINDINGS (USE ONLY THIS INFORMATION) ---
    {formatted_findings}
    --- END OF RAW FINDINGS ---

    Proceed with generating the comprehensive report based exclusively on the provided findings. Make sure to incoporate a user friendly format like specified.
    Remember the topic you need to answer/elaborate on: {topic}
    Present a chronological report, starting in the past, and working your way to the present, noting the key occurences in a neutral/objective tone.
    Focus on formatting it in good paragraphs & a good format.
    """
    return full_prompt

def get_global_competitor_prompt(ticker: str):
    return f"""
Find the top 5 direct competitors of the company with ticker symbol {ticker}.

You must return ONLY the ticker symbols of the competing companies, nothing else. 
Focus on companies that are in the same industry/sector and compete directly.
Only include publicly traded companies with valid stock ticker symbols.

Return the results in this exact JSON format:
```json
{{
 "global_competitors": [
   "TICKER1",
   "TICKER2", 
   "TICKER3"
 ],
 "national_competitors": [
   "TICKER1",
   "TICKER2", 
   "TICKER3"
 ]
}}
```
They must be in the same industry/sector.

Base your results off of what you find on the web. Get the official ticker supported by yahoo finance and only use that.
You must google the exact stocks as well with yahoo finance to get this.
The tickers national and global tickers are allowed to match if absolutely necessary.

Do not include any explanation, analysis, or additional text. Just the JSON with ticker symbols.
"""
