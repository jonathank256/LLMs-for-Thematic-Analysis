# LLM-Assisted Thematic Analysis Pipeline

A multi-stage pipeline that uses LLMs to perform inductive qualitative thematic analysis (TA) on interview transcripts, following Braun & Clarke's six-phase TA framework. Originally created for a study on how novices and experts verbally identify and describe dinosaur specimens, but the pipeline itself is domain-agnostic. The prompts can be swapped for use within any qualitative research domain.

Developed as part of research at the University of Victoria's Different Minds Lab (DML), with equal collaboration from myself alongside Abby Hunter and Tove Jensen, and our PI, Jim Tanaka. 

## Why this exists

Manual thematic analysis is slow and labor-intensive, especially the initial coding pass across many transcripts. This pipeline uses LLMs to accelerate the mechanical parts of TA (extraction, structuring) while keeping a human-in-the-loop verification step at every stage. Most importantly, the LLM never gets the final say on codes and themes, and steps can be edited or rerun.

## How it maps to Braun & Clarke's 6 phases

| Phase | Braun & Clarke (2006) | This pipeline |
|---|---|---|
| 1 | Familiarizing yourself with the data | Manual transcript review (not scripted) |
| 2 | Generating initial codes | **Stage 1** — `1_TA.py` |
| 2b | Verifying initial codes | **Stage 2** — `2_TA_check.py` |
| 3 | Searching for themes | **Stage 3** — `3_theme_gen.py` |
| 4 | Reviewing themes | **Stage 4** — `4_theme_verify.py` |
| 5–6 | Defining/naming themes, producing the report | Manual (final researcher pass) |

## Pipeline stages

```
participant-interviews/         raw transcripts (not committed — see Data & Privacy)
        │
        ▼
1_TA.py            ── inductive code extraction ──────────────►  1-TA-codes/
        │
        ▼
2_TA_check.py       ── verifies/refines the codebook ─────────►  2-TA-checks/
        │                against the original transcript
        ▼
3_theme_gen.py      ── groups codes into themes/subthemes ────►  3-TA-themes/
        │
        ▼
4_theme_verify.py   ── validates/refines themes against ──────►  4-theme-checks/
                         the codebook and original text
```

Each stage calls the OpenAI API with a stage-specific system/user prompt, writes its output as structured JSON, and logs the prompt + response pair to a timestamped file under `Prompts/` for full traceability of what prompt produced what output.
**Stages 1 and 3 can be rerun** to iterate on codes and themes. This process is intended to always keep a human-in-the-loop, and can be thought of as a collaboration between the person running the pipeline and the LLM, rather than as a single-shot output. 

There's also `0_linguistic_proto.py`, an early exploratory script that used an LLM to estimate mean length of utterance (MLU) on a transcript. This was kept as a record of the earlier prototyping phase, and is not a part of the main 4-stage pipeline. `code_numbering.py` is a small utility for consistently re-numbering codes across files.

## Setup

```bash
git clone https://github.com/jonathank256/LLMs-for-Thematic-Analysis.git    
cd LLMs-for-Thematic-Analysis    
python3 -m venv venv    
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows
pip install -r requirements.txt    
```

Create a `.env` file in the project root with your OpenAI API key:
```
API_KEY=your-openai-api-key-here    
```

## Usage

Run stages in order. Stage 1 and 2 process every file in their input folder automatically; Stage 3 and 4 take specific filenames as arguments.

```bash    
python3 1_TA.py    
python3 2_TA_check.py    
python3 3_theme_gen.py <codebook_filename.txt>    
python3 4_theme_verify.py <theme_filename.json> <codebook_filename.txt>    
```

Each script writes its output to the corresponding numbered folder and appends a prompt/response record under `Prompts/`.    

## Data & privacy

Raw interview transcripts (`participant-interviews/`) are **not included** in this repository. What you'll find in `1-TA-codes/` through `4-theme-checks/` is derived, de-identified output: extracted codes, verified codebooks, and themes. Some of this data has already been presented at academic conferences as part of this research.

## Known limitations

- **Duplicate codes across specimens** are expected and intentional at the coding stage (per TA convention). This is handled in the theme-generation stage, not before, and frequency, as in manual TA, plays a role in theme generation.   
- **LLM output correctness isn't guaranteed** — each generation stage is paired with a verification stage precisely because model output can drift from the source text; the verification steps are load-bearing, not optional.    
- This pipeline automates the mechanical extraction/grouping steps of TA. Phases 1, 5, and 6 (familiarization, defining/naming, and writing up) remain manual and researcher-led, as they should.    

## Acknowledgments

Built as part of research at UVic's Different Minds Lab. Study data has been presented at NOWCAM conferences (2024, 2025).
