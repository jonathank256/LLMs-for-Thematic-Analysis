import os
import json
import sys
from datetime import date

# the llm!
from openai import OpenAI

# for environmental vars and wd stuff
from dotenv import load_dotenv
from pathlib import Path

# set working directory to parent of script
script_dir = Path(__file__).resolve().parent
os.chdir(script_dir)

load_dotenv()
api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

client = OpenAI(api_key=api_key)

MODEL = "gpt-4o-mini"

original_text = "2-TA-checks/novice_codes.txt"

# SET PROMPTS HERE
user_prompt = """
Check whether the codes in <<codebook>> represent the subthemes/themes in <<themes>>, and whether the themes represent the overall meaning of the codebook.

Instructions:
1) If any invalid themes or subthemes are identified, remove or change them within <<themes>> to restore validity.
2) If any themes/subthemes are **too similar** in meaning and can be combined into a single theme/subtheme, concatenate the themes or subthemes.
3) If any themes or subthemes feature too much variability and should be broken into 2 or more themes or subthemes, split into 2 or more themes/subthemes that represent distinct meanings.
4) Check whether any important themes are present in the codebook that have not already been represented as themes. If any are found, create and add a new theme to <<themes>> in <<input/output>> format. 

Output your final version of themes with your corrections in <<input/output>> format. 
"""

system_prompt = """
You are an analyst whose job is to verify the work of a psychologist with paleontology knowledge who is conducting a thematic analysis of <<original text>>, which is a participant’s description of various dinosaurs. The psychologist has constructed themes using their codebook <<codebook>>. You must refine and validate these previously-generated themes <<themes>>, which are in <<input/output>> format. 

<<Rules>>:
- **Do NOT** change/remove codes from their respective theme/subtheme if they are relevant. 
- Only change a theme/subtheme if it is incorrect or unrepresentative of the codebook <<codebook>>.
- Do not output any conversational text.
- If you must create or change any themes/subthemes, they must adhere to <<Theme Structure>>.
- Codes can appear in multiple themes and/or subthemes if conceptually appropriate.
- Themes are distinct and feature external heterogeneity and internal homogeneity.
- Themes are relevant and important to <<original text>>.
- Themes do not encompass all codes within the codebook.
- Subthemes consist of fewer codes than their overarching themes, and these subtheme codes are logically related to their overarching themes.
- If a code does not conceptually relate to any themes, the code is placed into a special theme titled **"Miscellaneous"**.
- “Miscellaneous” does not have any subthemes or overlapping codes with other themes/subthemes.
- If you violate these rules in any sense, we will treat this as a system failure.

<<Theme Structure>>:
- For each theme, provide:
    a) A theme name consisting of 1-3 words.
    b) A concise description (1-2 sentences).
    c) A list of codes directly associated **only** with the theme and not conceptually related to any subtheme of the theme.
- If a theme can be further reduced into distinct subsets of meaning, create subthemes (optional, only if warranted):
    - Each subtheme must include:
        a) A subtheme name consisting of 1-3 words.
        b) A concise description (1-2 sentences).
        c) A list of a minimum of 5 related codes. The list must contain all codes that make up the theme.


<<Input/Output>>:
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


def main():
    
    if len(sys.argv) <= 2:
        print("Usage: python 4_theme_check.py <theme_json_file> <codebook_txt_file>")
        return
    
    # Step 3 output file (theme JSON)
    json_file = sys.argv[1]

    # Codebook / original text file
    original_text = sys.argv[2]

    with open(original_text, "r", encoding="utf-8") as f:
        codebook = f.read()
    
    with open(f"3-TA-themes/{json_file}", "r", encoding="utf-8") as f:
        data = json.load(f)

    # call the LLM on participant interview as portion of user prompt
    prompt = f"""
        {user_prompt}: <<original text>> = {original_text}, <<codebook>> = {codebook}, <<themes>> = {data}
        """
    response = llm_prompt(prompt, system_prompt)
    print(response)
    
    # count the files for naming convention
    file_count = 1
    folder_path = "4-theme-checks"
    os.makedirs(folder_path, exist_ok=True)  # ensure folder exists

    # increment output file number if file with same base name exists
    base_name = json_file[:-7]  # remove .json
    for entry in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, entry)) and entry.startswith(base_name):
            file_count += 1 

    # write to the 4-theme-checks folder in valid .json format (as a list)
    with open(f"{folder_path}/{base_name}_{file_count}.json", "w", encoding="utf-8") as file:
        file.write(response)


    today = date.today()

    with open('Prompts/ThemeChecksTimeline.txt', 'a') as file:
        file.write(f'\n\nresponses_{file_count} "User Prompt:\n{user_prompt}"\n\tSystem Prompt\n"{system_prompt}"\n\t{today}\n{MODEL}')


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