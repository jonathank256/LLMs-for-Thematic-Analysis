# USING THE COMMAND LINE. This is a bit tricky. Essentially, enter: "python3 0_linguistic_proto.py" first. This is how
# you call this script where you are reading this. Following this, enter the file path to the input that you want to use (raw data).
# This script is set up to, by default, assume your data will be in the folder "participant-interviews", and so you do not need to enter
#. As an example, to get a verbalization interview for expert3, you would add "verbalization-interview/expert_3.txt". Lastly, 
# the last thing to add is the location that you want the LLM data to be saved. The tracking (prompts, as well as the data itself)
# is handled by the script. As an example, if you wanted to add the data to the mean-utterance folder in a file called "test3.txt", you
# would add mean-utterance/test3.txt. Your choice of folder should reflect the type of test you are asking the llm to do.
# 
# Overall example: python3 0_linguistic_proto.py verbalization_interview/expert_4.txt mean-utterance/test3.txt


# CHANGE THE SYSTEM PROMPT HERE. This defines the LLM's role, meaning you give it context as to what its task is. This is
# also where you establish potential rules, and specify an output format for the file, though the format will always be txt.
SYSTEM_PROMPT = "You are a linguistic analyst conducting a linguistic mean length of utterances on a dataset. Report the average number of words per utterence accurately."


# CHANGE THE USER PROMPT HERE. This will consist of the information you want to feed the LLM immediately before the data,
# as this prompt will appear directly above the data, like this:
# You are conducting {test} on {participant data}. Your job is to ...
# ...
# Participant: This is the fun part?
# Researcher #1: Yeah.
# ... more data
# We have found a short task description, then instructions, is the best thing to include here, but you can mess with this
# as you see fit. 
USER_PROMPT = "Report the mean length of utterances of the following dataset. Ensure the output is just a standard .txt"


# this is where you can change the model type. Models include gpt-4o-mini, gpt-4o, and gpt-5o, with 
# gpt-4o-mini being the cheapest and "worst", and gpt-5o being the most expensive and the "best"
MODEL = "gpt-4o"

# generics, file stuff and dfs
import os
import datetime
import sys
from dotenv import load_dotenv

# the llm!
from openai import OpenAI

# for environmental vars and wd stuff
from pathlib import Path

# set working directory to parent of script
script_dir = Path(__file__).resolve().parent
os.chdir(script_dir)

user_prompt = USER_PROMPT
system_prompt = SYSTEM_PROMPT

input_file = sys.argv[1]

if len(sys.argv) > 2:
    output_file = Path(f"0-linguistic-data/{sys.argv[2]}")
else:
    print("No output input. Data will only appear in the terminal.")

load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")


client = OpenAI(api_key=api_key)

def main():
    full_file_path = f"participant-interviews/{input_file}"

    if not os.path.isfile(full_file_path):
        print("File does not exist.")
    else:
        with open(full_file_path, "r", encoding="utf-8") as f:
            full_text = f.read()
            
        # Remove empty lines and strip whitespace from each line
        lines = full_text.splitlines()
        non_empty_lines = [line.strip() for line in lines if line.strip() != '']
        cleaned_text = user_prompt + "\n" + "\n".join(non_empty_lines)

        # call the LLM on linguistic data as part of user prompt
        llm_response = llm_prompt(cleaned_text) 
        print(llm_response)

        # write to the 0-linguistic-data folder 
        if len(sys.argv) > 2:
            
            output_file.parent.mkdir(parents=True, exist_ok=True)
            Path('0-linguistic-data/past_results').mkdir(parents=True, exist_ok=True)
            Path('0-linguistic-data/linguistic-prompts').mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(llm_response)

            date = datetime.datetime.now()

            with open('0-linguistic-data/past_results/result_timeline.txt', 'a') as new:
                new.write(f'\n\t{date}\n{MODEL}\n\n{input_file[11:]}:\n{llm_response}')

            with open('0-linguistic-data/linguistic-prompts/Prompts.txt', 'a') as file:
                file.write(f'\n\t{date}\n{MODEL}\n\n{input_file[11:]}:\nUser Prompt:\n"{user_prompt}"\nSystem Prompt:\n"{system_prompt}"')

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