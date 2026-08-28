import os
import datetime

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

MODEL = "gpt-5"

# SET PROMPTS HERE
user_prompt = """
You are performing inductive thematic analysis on participant responses. Your task is to extract *only* what is directly and explicitly present in the participant’s verbalization. Your job is to identify any relevant codes that exist within the text, while explaining your step-by-step process. 

Every time you identify a code within <participant>, follow the <instructions> below.
<<Instructions>>:
1. Generate short **Code Name** summarizing the participant's main ideas within <participant>. **Code Name** must be 1-3 words long.
2. Write a **Code Description** which is a meaningful description of each code identified.
3. Select an **Exact Quote**:  
   - You must **copy an exact substring** from the area in <participant> where you extracted the code.  
4. Number and format the identified code with its description and quote in <<JSON Output Format>>.

Once you are confident you have identified all relevant and important codes, output all codes as <<JSON Output Format>>.
"""

system_prompt = """
You are an analyst whose job is to verify that the codebook produced by a psychologist with paleontology knowledge for qualitative thematic analysis is valid and free of error. You will verify that all codes in the codebook are correct. You will make sure that each **Code Name** best represents its corresponding quote.

<<Rules>>:
- All codes in the codebook must exist within the input text.
-Each code’s name must be concise and best represent the code
- Each code’s quote must capture the code’s meaning. The relationship between the code and its quote must be apparent without the original text.
- A code’s description must be clear, concise and representative of the code.
- If a code is correct and its quote or description cannot be improved upon, the output code must be identical to the original input code.

<<Input Codebook Format>>:
[
 { 
   "Code #": "{{{{code name}}}}",
   "Description": "{{{{description}}}}",
   "Quote": "{{{{quote}}}}"
 }
…
]

<<JSON Output Format>>:
[
 {
   "Code #": "{{{{code name}}}}",
   "Description": "{{{{description}}}}",
   "Quote": "{{{{quote}}}}"
 }
…
] 
"""


def main():
    
    input_path = "1-TA-codes"

    Path("2-TA-checks/past_results").mkdir(parents=True, exist_ok=True)
    Path("Prompts").mkdir(parents=True, exist_ok=True)

    for file in os.listdir(input_path):
        file_path = os.path.join(input_path, file)

        if file.startswith("."):
            continue

        if os.path.isfile(file_path):      
            with open(file_path, "r", encoding="utf-8") as f:
                data = f.read()

            # assume the text file is inside participant-interviews
            with open(f"participant-interviews/{file}", "r", encoding="utf-8") as t:
                interview_text = t.read()

            # call the LLM on participant interview as portion of user prompt
            prompt = f"""
            {user_prompt}

            <<original text>>:
            {interview_text}

            <<codebook>>:
            {data}
            """
            response = llm_prompt(prompt, system_prompt)

            # write to the 2-TA-check folder in valid .json format (as a list)
            with open(f"2-TA-checks/{file}", "w", encoding="utf-8") as file:
                file.write(response)

            date = datetime.datetime.now()

            with open('2-TA-checks/past_results/result_timeline.txt', 'a') as new:
                new.write(f'\n\t{date}\n{MODEL}\n\n{file.name[12:]}:\n{response}')

    with open('Prompts/Prompts2.txt', 'a') as file:
        file.write(f'\n\n{file.name[12:]} "User Prompt:\n{user_prompt}"\n\tSystem Prompt\n"{system_prompt}"\n\t{date}\n{MODEL}')

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