import os
import subprocess
import json
import pandas as pd
import shutil

repos = [
    ("yolov10", "https://github.com/THU-MIG/yolov10.git"),
    ("marker", "https://github.com/datalab-to/marker.git"),
    ("GPT-SoVITS", "https://github.com/RVC-Boss/GPT-SoVITS.git"),
]

top_25_cwe = [
    "CWE-79", "CWE-787", "CWE-89", "CWE-352", "CWE-22", "CWE-125", "CWE-78", "CWE-416", "CWE-862", "CWE-434",
    "CWE-94", "CWE-20", "CWE-77", "CWE-287", "CWE-269", "CWE-502", "CWE-200", "CWE-863", "CWE-918", "CWE-119",
    "CWE-476", "CWE-798", "CWE-190", "CWE-400", "CWE-306"
]  

def run_cmd(cmd, okay_nonzero=False):
    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["LANG"] = "C.UTF-8"
    env["LC_ALL"] = "C.UTF-8"
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
        env=env
    )
    for line in process.stdout:
        print(line, end='')
    process.wait()
    if process.returncode != 0 and not okay_nonzero:
        raise RuntimeError(f"Command failed: {cmd}")



def clone_repos():
    for folder, url in repos:
        if not os.path.isdir(folder):
            print(f"Cloning {url} into ./{folder} ...")
            run_cmd(f"git clone {url} {folder}")
        else:
            print(f"Repo folder {folder} already exists, skipping clone.")

def run_codeql(repo, dbfolder, outfile,
               suite_path="codeql/python/ql/src/codeql-suites/python-security-and-quality.qls"):
    if os.path.isfile(outfile):
        print(f"[SKIP] CodeQL JSON already exists for {repo}, skipping analysis...")
        with open(outfile, encoding="utf-8") as f:
            data = json.load(f)
        return data
    if os.path.isdir(dbfolder):
        shutil.rmtree(dbfolder)
    print(f"Running CodeQL scan on {repo} ...")
    run_cmd(f"codeql database create {dbfolder} --language=python --source-root={repo} --overwrite")
    run_cmd(f"codeql database analyze {dbfolder} {suite_path} --format=sarifv2.1.0 --output={outfile}")
    with open(outfile, encoding="utf-8") as f:
        data = json.load(f)
    findings_count = sum(len(run.get("results", [])) for run in data.get("runs", []))
    print(f"CodeQL: Found {findings_count} results in {repo}")
    return data

def run_bandit(repo, outfile):
    if os.path.isfile(outfile):
        print(f"[SKIP] Bandit JSON already exists for {repo}, skipping analysis...")
        with open(outfile, encoding="utf-8") as f:
            data = json.load(f)
        return data
    print(f"Running Bandit scan on {repo} ...")
    run_cmd(f"bandit -r {repo} -f json -o {outfile}", okay_nonzero=True)
    with open(outfile, encoding="utf-8") as f:
        data = json.load(f)
    print(f"Bandit: Found {len(data.get('results', []))} results in {repo}")
    return data

def run_semgrep(repo, outfile):
    import os
    # If file exists, try to load it and handle any error
    if os.path.isfile(outfile):
        print(f"[SKIP] Semgrep JSON already exists for {repo}, checking validity...")
        try:
            with open(outfile, encoding="utf-8") as f:
                data = json.load(f)
            print(f"Semgrep: Found {len(data.get('results', []))} results in {repo}")
            return data
        except Exception as e:
            print(f"Semgrep JSON for {repo} is invalid or empty, removing and rerunning. Reason: {e}")
            os.remove(outfile)
    # Run scan and create new file if needed
    print(f"Running Semgrep scan on {repo} ...")
    try:
        run_cmd(f"semgrep --config=auto --json --quiet --output {outfile} {repo}")
    except RuntimeError as e:
        print(f"Warning: Semgrep scan failed for {repo}. Continuing without interrupting.")
        return None  # Or return empty dict {} if preferred
    with open(outfile, encoding="utf-8") as f:
        data = json.load(f)
    print(f"Semgrep: Found {len(data.get('results', []))} results in {repo}")
    return data



def parse_codeql(data):
    # Find mapping of ruleId to tags with CWEs
    rules_map = {}
    for run in data.get("runs", []):
        tool = run.get("tool", {})
        driver = tool.get("driver", {})
        for rule in driver.get("rules", []):
            tags = rule.get("properties", {}).get("tags", [])
            rules_map[rule.get("id", "")] = tags

    cwes = {}
    for run in data.get("runs", []):
        for res in run.get("results", []):
            cwe_set = set()
            rule_id = res.get("ruleId", "")
            tags = rules_map.get(rule_id, [])
            for tag in tags:
                if tag.startswith("external/cwe/cwe-"):
                    cwe = "CWE-" + tag.split("external/cwe/cwe-")[1].upper()
                    cwe_set.add(cwe)
            # Fallback to extract from ruleId if plain CWE
            if not cwe_set and "CWE-" in rule_id:
                parts = rule_id.split()
                for part in parts:
                    if part.startswith("CWE-"):
                        cwe_set.add(part)
            for cwe in cwe_set:
                cwes[cwe] = cwes.get(cwe, 0) + 1
    return cwes

def parse_bandit(data):
    cwes = {}
    for res in data.get("results", []):
        cwe = res.get("issue_cwe")
        if cwe:
            if isinstance(cwe, dict) and "id" in cwe:
                cweid = cwe["id"]
            else:
                cweid = cwe
            cwe_id = f"CWE-{cweid}".upper() if not str(cweid).upper().startswith("CWE-") else str(cweid).upper()
            cwes[cwe_id] = cwes.get(cwe_id, 0) + 1
    return cwes

import re

def parse_semgrep(data):
    cwes = {}
    cwe_pattern = re.compile(r"^CWE-\d+$")
    for r in data.get("results", []):
        cwe_list = r.get("extra", {}).get("metadata", {}).get("cwe", [])
        for cwe in cwe_list:
            cwe_id = cwe.split(":")[0].strip()
            if cwe_pattern.match(cwe_id):
                cwes[cwe_id] = cwes.get(cwe_id, 0) + 1
            # else ignore malformed entries
    return cwes


def cwe_row(project, tool, findings):
    return [
        {
            "Project_name": project,
            "Tool_name": tool,
            "CWE_ID": cwe,
            "Number of Findings": count,
            "Is_In_CWE_Top_25?": "Yes" if cwe in top_25_cwe else "No"
        }
        for cwe, count in findings.items()
    ]

import matplotlib.pyplot as plt
import seaborn as sns

def compute_tool_level_coverage(df, top_25_cwe):
    # Get unique CWE sets detected by each tool
    tool_cwes = df.groupby("Tool_name")["CWE_ID"].apply(set).to_dict()

    coverage = {}
    for tool, cwes in tool_cwes.items():
        top25_detected = len([cwe for cwe in cwes if cwe in top_25_cwe])
        coverage_percent = (top25_detected / len(top_25_cwe)) * 100
        coverage[tool] = coverage_percent
        print(f"{tool} Top 25 CWE coverage: {coverage_percent:.2f}% ({top25_detected} of {len(top_25_cwe)})")
    return tool_cwes, coverage

def compute_iou_matrix(tool_cwes):
    tools = list(tool_cwes.keys())
    n = len(tools)
    iou_matrix = pd.DataFrame(index=tools, columns=tools, dtype=float)

    for i in range(n):
        for j in range(n):
            set_i = tool_cwes[tools[i]]
            set_j = tool_cwes[tools[j]]
            intersection = set_i.intersection(set_j)
            union = set_i.union(set_j)
            iou = len(intersection) / len(union) if union else 0.0
            iou_matrix.iloc[i, j] = iou
    return iou_matrix

def plot_coverage(coverage):
    tools = list(coverage.keys())
    values = list(coverage.values())
    plt.figure(figsize=(8,6))
    sns.barplot(x=tools, y=values, palette="viridis")
    plt.title("Top 25 CWE Coverage Percentage by Tool")
    plt.ylabel("Coverage (%)")
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig("coverage.png")
    plt.close()


def plot_iou_matrix(iou_matrix):
    plt.figure(figsize=(8,6))
    sns.heatmap(iou_matrix, annot=True, fmt=".2f", cmap="YlGnBu", square=True)
    plt.title("Pairwise CWE IoU Matrix Between Tools")
    plt.tight_layout()
    plt.savefig("iou_matrix.png")
    plt.close()





def main():
    print("Starting SAST automation script\n")
    clone_repos()
    results = []

    for folder, repo_url in repos:
        sfile = f"semgrep_{folder}.json"
        bfile = f"bandit_{folder}.json"
        cdb = f"codeql_db_{folder}"
        cfile = f"codeql_{folder}.sarif.json"

        semgrep_data = run_semgrep(folder, sfile)
        bandit_data = run_bandit(folder, bfile)
        codeql_data = run_codeql(folder, cdb, cfile)

        if semgrep_data:
            results += cwe_row(folder, "Semgrep", parse_semgrep(semgrep_data))
        if bandit_data:
            results += cwe_row(folder, "Bandit", parse_bandit(bandit_data))
        if codeql_data:
            results += cwe_row(folder, "CodeQL", parse_codeql(codeql_data))

    df = pd.DataFrame(results)
    df.to_csv("all_cwe_findings.csv", index=False)
    print("\nCWE findings saved to all_cwe_findings.csv\n")
    print(df.head())

    

    tool_cwes, coverage = compute_tool_level_coverage(df, top_25_cwe)
    plot_coverage(coverage)

    iou_matrix = compute_iou_matrix(tool_cwes)
    print("\nPairwise IoU matrix between tools:\n", iou_matrix)
    plot_iou_matrix(iou_matrix)

if __name__ == "__main__":
    main()
