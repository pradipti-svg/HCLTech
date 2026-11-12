This project has been created as a part of assignment given by HCLTech.
The file test.py runs Garak, against a target language model, capture execution logs, preserve native scan evidence, and export detector-flagged findings to CSV.
It supports an OpenAI API target or a compatible Hugging Face target through Garak's generator plugins.

HCL_task/
|-- test.py           # Argument parsing, scan execution, logging and CSV export
|-- .env              # Optional key storage; loading is currently commented out
|-- venv/             # Optional Python virtual environment
|--requirement.txt    # Python package that are currently present


Architecture:
---------------
Command-line arguments ---> Validate settings and create a unique run directory ---> Start a separate process: python -X utf8 -u -m garak ---> Garak probe -> adversarial prompts -> generator -> target model --> responses -> detectors -> scores --->native report and hitlog files --->save_findings_csv() -> CSV

Configure the OpenAI key
-----------------------------
In case, you have OPENAI API

Windows
setx  OPENAI_API_KEY "YOUR_API_KEY"
Test-Path Env:OPENAI_API_KEY

The check prints `True` when the variable exists without displaying its value. The child Garak process inherits the environment.
The project also has .env file  where the values for the OPEN_AI can be placed, but needs to be ignored in the 'gitignore' file

OPENAI has been used here to include the provision for LLM API this same can be acheived by Anthropic as well.

to check this: python test.py --target-type openai --target-name YOUR_MODEL_ID  --probes dan.Dan_11_0   --generations 1 --threshold 0.5 --output-dir "C:\Users\Lenovo\Documents\RedTeamResults"

Note: While running test with OPENAI models it has been found that GARAK could not register models like gpt mini 4.0, it has been treating the model as a chat model.

Running test on Hugging face
-----------------------------

python test.py  --target-type huggingface.Pipeline --target-name Qwen/Qwen2.5-0.5B-Instruct --probes dan.Dan_11_0   --generations 1  --threshold 0.5 --output-dir "C:\Users\Lenovo\Documents\RedTeamResults"


Command-line options
--------------------------

Option -- Required/default -- Meaning 
 `--target-type` -- Required -- Garak generator, such as `openai` or `huggingface.Pipeline` 
 `--target-name` -- Required -- API model ID or Hugging Face model ID 
 `--probes` -- `dan.Dan_11_0` -- Selected probe or comma-separated probe names 
 `--generations` -- `1` -- Requested responses per attack prompt; must be at least 1 
 `--threshold` --`0.5` -- Detector-score evaluation threshold; accepted range is 0 to 1 
 `--output-dir` -- `C:\Users\Lenovo\Documents\RedTeamResults` -- Parent folder for scan results



Output and logging
------------------------------
The script creates a subfolder named with a UTC timestamp and a random eight-character identifier:

results/
└── <UTC timestamp>-<random ID>/
    ├── manifest.json
    ├── console.log
    ├── scan.report.jsonl
    ├── scan.hitlog.jsonl            # May be absent when there are no detector hits
    ├── scan.report.html             # If Garak's HTML generation succeeds
    └── successful_jailbreaks.csv

File -- Purpose 
`manifest.json` -- Run ID, UTC timestamps, Garak version, target, probes, generations, threshold, arguments and process status 
`console.log`   -- Combined stdout/stderr from Garak; printed to the terminal and flushed to disk 
`scan.report.jsonl` -- Original Garak scan records, including available attempt/output/evaluation evidence 
`scan.hitlog.jsonl` -- Garak's detector-flagged records when generated 
`scan.report.html` -- Native HTML summary when generated 
`successful_jailbreaks.csv` -- CSV derived from the native hitlog by the embedded export function


DISCLAIMER
--------------------------------
This project is intended for authorized AI security assignment , education, and defensive testing. 
Test only models, endpoints that you own or have explicit permission to assess, and follow the provider's terms and applicable laws. 
Agree on the testing scope, request volume, and spending limits before running scans.
Adversarial prompts and model responses may contain harmful or sensitive material; restrict access to logs, remove secrets before sharing evidence, and retain results only as needed. 
Do not use this project to obtain unauthorized access, expose private information, or facilitate harm.
Treat detector hits as findings requiring validation, report confirmed vulnerabilities responsibly to the appropriate owner, and document limitations. 
A scan with no detected failures does not certify that a model is safe or secure.

Note: .env file has not been provided here
