"""According to the question we need to create a python file to run Garak and ."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from uuid import uuid4
import importlib.metadata
from dotenv import load_dotenv
import csv

#load_dotenv(Path(__file__).resolve().parent / ".env")
def save_findings_csv(prefix, run_dir):
    hitlog = Path(str(prefix) + ".hitlog.jsonl")
    csv_file = run_dir / "successful_jailbreaks.csv"

    fields = ["attempt_id", "probe", "detector","score", "prompt", "output", "review_status"]
    with csv_file.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        if not hitlog.exists():
            print(f"No hitlog found. Created CSV with headers: {csv_file}")
            return
        
        with hitlog.open(encoding="utf-8") as log:

            for number, line in enumerate(log, start=1):
                if not line.strip():
                    continue

                try:
                    hit = json.loads(line)
                except json.JSONDecodeError:
                    print(f"Skipping invalid hitlog line {number}")
                    continue

                row = {}

                for field in fields:
                    value = hit.get(field, "")
                    if isinstance(value, dict):
                        value = value.get("text", json.dumps(value))
                    elif isinstance(value, list):
                        value = json.dumps(value)

                    if isinstance(value, str):
                        if value.lstrip().startswith(("=", "+", "-", "@")):
                            value = "'" + value
                    
                    row[field] = value
                    row["review_status"] = "requires_review"
                    writer.writerow(row)
        print(f"Findings saved to: {csv_file}")
                             
def main():

    #We are giving this part since we need to provide CLI arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target-type', required=True, help='e.g. huggingface')
    parser.add_argument('--target-name', required=True, help='Hugging Face model ID or open ai model')
    parser.add_argument('--probes', default='lmrc.Profanity', help='Comma-separated Garak probe names')
    parser.add_argument('--generations', type=int, default=1)
    parser.add_argument('--threshold', type=float, default=0.5)
    parser.add_argument('--output-dir', type=Path, default=Path(r"C:\Users\Lenovo\Documents\RedTeamResults"))
    args = parser.parse_args()

    # check if the cli arguments are in-line and correct
    if args.generations < 1 or args.threshold < 0 or args.threshold > 1:
        parser.error('generations must be positive and threshold must be between 0 and 1')
    
    if args.target_type.startswith('openai') and not os.environ.get('OPENAI_API_KEY'):
        parser.error('Set OPENAI_API_KEY in the terminal environment first')

    try:
        version = importlib.metadata.version('garak')
    except importlib.metadata.PackageNotFoundError:
        parser.error('Install dependencies: python -m pip install -r requirements.txt')
        
    #please note that due to laptop configuration we are going for Openai API key.
       
    run_dir = args.output_dir.resolve() / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:8])
    run_dir.mkdir(parents=True)
    prefix = run_dir / 'scan'

    garak_args = ['--target_type', args.target_type, '--target_name', args.target_name,
                  '--probes', args.probes, '--generations', str(args.generations),
                  '--eval_threshold', str(args.threshold), '--report_prefix', str(prefix)]

    metadata = dict(run_id=run_dir.name, started_at=datetime.now(timezone.utc).isoformat(),
                    garak_version=version, target_type=args.target_type,
                    target_name=args.target_name, probes=args.probes,
                    generations=args.generations, threshold=args.threshold,
                    state='running', garak_arguments=garak_args)
    
    manifest = run_dir / 'manifest.json'
    manifest.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    # worker = 'from garak.cli import main; import sys; main(sys.argv[1:])'
    print(f'Run directory: {run_dir}', flush=True)
    try:
        with (run_dir / 'console.log').open('w', encoding='utf-8') as log:
            '''
            proc = subprocess.Popen([sys.executable, '-u', '-c', worker, *garak_args],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, encoding='utf-8', errors='replace')
            '''
            proc = subprocess.Popen([sys.executable, "-X", "utf8", "-u", "-m", "garak", *garak_args],
    stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",errors="replace")
         
            try:
                for line in proc.stdout:
                    print(line, end='')
                    log.write(line)
                    log.flush()
                code = proc.wait()
            except BaseException:
                proc.terminate()
                proc.wait()
                raise
        metadata['exit_code'] = code
        metadata['state'] = 'completed' if code == 0 else 'failed'
    except BaseException:
        metadata['state'] = 'interrupted_or_failed'
        raise
    finally:
        metadata['finished_at'] = datetime.now(timezone.utc).isoformat()
        manifest.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        report = prefix.with_suffix('.report.jsonl')
        save_findings_csv(prefix, run_dir)
        if report.exists():
            raise SystemExit(code)
            
        
if __name__ == '__main__':
    main()


  
  
