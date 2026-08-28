# generics, file stuff and dfs
import os
import datetime
import sys

# the llm!
from openai import OpenAI

# for environmental vars and wd stuff
from dotenv import load_dotenv
from pathlib import Path

# set working directory to parent of script
script_dir = Path(__file__).resolve().parent
os.chdir(script_dir)

MODEL = "gpt-5"

# SET THE SYSTEM PROMPT HERE!
system_prompt = """You are a psychologist with paleontology knowledge conducting a qualitative thematic analysis of a conversation between a participant and researchers about the participant’s verbal descriptions of four distinct dinosaurs.

<<Rules>>:
- Design your thematic analysis codes to be understood by those with a background in dinosaur knowledge.
- Your task is **extraction only**, not interpretation.
- You may extract duplicate codes where necessary.
- Number each code you identify from 1 to <total number of codes>.
- You may identify any number of codes, as long as you have reported every important code that exists within <participant>.
- **Do not** generate any irrelevant or vague codes.
- **Do not** invent or infer any codes not explicitly stated in the participant's text.
- **Do not** reference general knowledge, even if it seems relevant to the topic.
- **Do not** improve, correct, or guess what the participant meant.
- **Do not** generate any codes existing within <researcher_1> or <researcher_2>.
- **Do not** paraphrase, summarize, or alter the participant's quotes in <quote> output.
- **Code Name** must be simple, concise and best describe the code.
- **Do not** include information about the order that dinosaur stimuli are shown(ex. First dinosaur, dinosaur 4)
- If any rules are violated, this will be treated as a system failure.
- We are following Braun & Clarke’s 6 steps of TA. Do not generate themes yet.

<<Input Text>>:
Participant Text:
<participant>
{{{{participant_text}}}}
</participant>

Researcher #1 Text:
<researcher_1>
{{{{researcher_1_text}}}}
</researcher_1>

Researcher #2 Text:
<researcher_2>
{{{{researcher_2_text}}}}
</researcher_2>

<<JSON Output Format>>:
[
 {
   "Code 1": "{{{{code name}}}}",
   "Description": "{{{{description}}}}",
   "Quote": "{{{{quote}}}}"
 },
]
"""

# set the user prompt (before strategy is given) here!
user_prompt = """You are performing inductive thematic analysis on participant responses. Your task is to extract *only* what is directly and explicitly present in the participant’s verbalization. Your job is to identify any relevant codes that exist within the text, while explaining your step-by-step process. 

Every time you identify a code within <participant>, follow the <instructions> below.
<<Instructions>>:
1. Generate short **Code Name** summarizing the participant's main ideas within <participant>. **Code Name** must be 1-3 words long.
2. Write a **Code Description** which is a meaningful description of each code identified.
3. Select an **Exact Quote**:  
   - You must **copy an exact substring** from the area in <participant> where you extracted the code.  
4. Number and format the identified code with its description and quote in <<JSON Output Format>>.

Once you are confident you have identified all relevant and important codes, output all codes as <<JSON Output Format>>.
"""


# THE FILE THAT YOUR ENV VARIABLE IS IN MUST BE CALLED ".env". IF IT IS ANYTHING ELSE THIS WILL NOT WORK
load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

client = OpenAI(api_key=api_key)


def main():

    interviews_path = f"participant-interviews/"

    Path("1-TA-codes/past_results").mkdir(parents=True, exist_ok=True)
    Path("Prompts").mkdir(parents=True, exist_ok=True)
    
    for file in os.listdir(interviews_path):

        file_path = os.path.join(interviews_path, file)

        if file.startswith("."):
            continue

        if os.path.isfile(file_path):
            
            with open(file_path, "r", encoding="utf-8") as f:
                full_text = f.read()
            
            # Remove empty lines and strip whitespace from each line
            lines = full_text.splitlines()
            non_empty_lines = [line.strip() for line in lines if line.strip() != '']
            cleaned_text = user_prompt + "\n" + "\n".join(non_empty_lines)

            # call the LLM on participant interview as portion of user prompt
            llm_response = llm_prompt(cleaned_text) 

            # write to the 1-TA-codes folder in valid .json format (as a list)
            with open(f"1-TA-codes/{file}", "w", encoding="utf-8") as file:
                file.write(llm_response)
            
            date = datetime.datetime.now()

            with open('1-TA-codes/past_results/result_timeline.txt', 'a') as new:
                new.write(f'\n\t{date}\n{MODEL}\n\n{file.name[11:]}:\n{llm_response}')

    with open('Prompts/Prompts1.txt', 'a') as file:
        file.write(f'\n\t{date}\n{MODEL}\n\n{file.name[11:]}:\nUser Prompt:\n"{user_prompt}"\n\tSystem Prompt\n"{system_prompt}"')

def llm_prompt(message):
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