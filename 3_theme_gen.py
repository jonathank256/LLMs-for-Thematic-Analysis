# generics, file stuff and dfs
import os
import pandas as pd
import json
from datetime import date
import sys

# the llm!
from openai import OpenAI

# for environmental vars and wd stuff
from dotenv import load_dotenv
from pathlib import Path

# set working directory to parent of script
script_dir = Path(__file__).resolve().parent
os.chdir(script_dir)

# SET THE SYSTEM PROMPT HERE!
system_prompt = """
You are a psychologist with paleontology knowledge conducting a thematic analysis of <<original text>>, a dinosaur novice’s verbal descriptions of dinosaurs, and have constructed a codebook. Now determine themes based on the codes within <<codebook>>. Subthemes should be generated where appropriate to convey more narrow ideas within each main theme. 

Rules:
- Codes may appear in multiple themes and/or subthemes if conceptually appropriate.
- Themes are distinct and feature external heterogeneity and internal homogeneity.
- Themes must be relevant and fully represent the <<original text>>.
- Themes do not consist of all codes in the codebook.
- Themes are conceptually specific but still consist of enough related codes to be relevant.
- Subthemes consist of fewer codes than their overarching themes, and these subtheme codes are logically related to their overarching themes.
- If a code does not conceptually relate to any themes, the code is placed into a special theme titled **"Miscellaneous"**.
- “Miscellaneous” does not have any subthemes or overlapping codes with other themes/subthemes.
- If any rules are violated, this will be considered a system failure.
- Do not output any explanation or conversational text.

<<Output>>:
[
{
"Theme Name": {{{{theme name}}}},
"Theme Description": {{{{description}}}},
 "Theme-Only Code Numbers": [{{{{code #}}}}, {{{{code #}}}}...],
"Subthemes": [
{
"Subtheme Name": {{{{subtheme name}}}},
"Subtheme Description":  {{{{description}}}},
"Subtheme Code Numbers": [{{{{code #}}}}, {{{{code #}}}}...]
},
]
}
"""

# set the user prompt (before strategy is given) here!
user_prompt = """
Group related codes into distinct, overarching themes based on their frequency and conceptual similarity.

<<Instructions:>>
- Identify clear, meaningful themes based on recurring patterns across the codes in <codebook>. 
    - For each theme, provide:
        - A theme name consisting of 1-3 words.
        - A concise description (1-2 sentences).
        - A list of codes associated **only** with the theme, and not related to any subtheme below the theme.
- If a theme can be further reduced into distinct subsets of meaning:
    - Create optional subthemes.
    - Each subtheme must include:
        - A subtheme name consisting of 1-3 words.
        - A short description (1-2 sentences).
        - A list of a minimum of 5 related codes. The list must contain all codes that make up the theme.
- Output all themes in <<output>> format.
"""

# THE FILE THAT YOUR ENV VARIABLE IS IN MUST BE CALLED ".env". IF IT IS ANYTHING ELSE THIS WILL NOT WORK
load_dotenv()
api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

client = OpenAI(api_key=api_key)

MODEL = "gpt-4o-mini"
 
def main():
    # Get output filename parameter from command line
    if len(sys.argv) == 2:
        json_file = sys.argv[1]
    else:
        print("Incorrect number of parameters inputted")
        return

    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create the themes_responses directory 
    themes_dir = os.path.join(script_dir, '3-TA-themes')
    os.makedirs(themes_dir, exist_ok=True)

    folder_path = "3-TA-themes"
    
    # number output files by run — increment each time script is run for same file
    file_count = 1
    output_file = f"3-TA-themes/{json_file[:-7]}_{file_count}.json"
    while os.path.exists(output_file):
        file_count += 1
        output_file = f"3-TA-themes/{json_file[:-7]}_{file_count}.json"

    # Read the contents of the input file
    with open(f"2-TA-checks/{json_file}", 'r', encoding='utf-8') as file:
        code_str = file.read()
        prompt = f"""
        {system_prompt}\n<codebook>{code_str}<codebook>\n
        """
        response = llm_prompt(user_prompt, prompt)

    print(response)

    today = date.today()

    with open('Prompts/ThemePromptTimeline.txt', 'a') as file:
        file.write(f'\n\nthemes_{file_count} "{user_prompt}"\n\t"{system_prompt}"\n\t{today}\n{MODEL}')

    # Save the response to the unique output file
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(response)

def llm_prompt(message, system_prompt):
    # informing the llm of what its role is!
    system_message = {
        "role": "system",
        "content": system_prompt
    }
    # creates an llm prompt with the user prompt and participant's text
    user_message = {
        "role": "user",
        "content": message
    }

    messages = [system_message, user_message]
    
    # some additional settings
    response = client.chat.completions.create(
        model=MODEL,
        messages = messages,
        temperature = 1,
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    main()