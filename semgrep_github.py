import os
import subprocess
import requests
import json
import pandas as pd

# Constant variables for connecting
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
ORG_NAME = os.getenv('ORG_NAME')
SEMGRP_RULES = {
    'default': 'p/default'
}
OUTPUT_JSON = 'semgrep_results.json'
REPOS_DIR = '' #add the org part of the GH url here
TEST_MODE = True  # Set to True for testing on one repo, False for full run

# Headers for GitHub API authentication
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def fetch_repositories(org_name):
    repos = []
    page = 1
    while True:
        repos_url = f'https://api.github.com/orgs/{org_name}/repos?per_page=100&page={page}'
        response = requests.get(repos_url, headers=headers)
        if response.status_code != 200:
            print(f'Failed to fetch repositories: {response.status_code}')
            break
        page_repos = response.json()
        if not page_repos:
            break
        repos.extend(page_repos)
        page += 1
    return repos

def clone_repository(repo_url, repo_dir):
    if not os.path.exists(repo_dir):
        # Incorporate the PAT directly into the clone URL 
        # TODO: THIS SHOULD BE DONE VIA SSH
        repo_url_with_token = repo_url.replace("https://", f"https://{GITHUB_TOKEN}@")
        subprocess.run(['git', 'clone', repo_url_with_token, repo_dir])

def run_semgrep(repo_dir, repo_name, rule_set, rule_path, verbose=False):
    output_file = f'{repo_name}_{rule_set}.json'
    semgrep_command = f'semgrep --config {rule_path} --json --output {output_file} {repo_dir}'
    if verbose:
        semgrep_command += " --verbose"
    result = subprocess.run(semgrep_command, shell=True, capture_output=True, text=True)
    
    parsing_errors = []
    if verbose:
        parsing_errors = parse_parsing_errors(result.stderr, repo_name)
    
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            semgrep_result = json.load(f)
        os.remove(output_file)
        return semgrep_result, parsing_errors
    return None, parsing_errors

def parse_parsing_errors(stderr_output, repo_name):
    parsing_errors = []
    for line in stderr_output.splitlines():
        if "error" in line.lower() or "warning" in line.lower():
            parsing_errors.append(f"{repo_name}: {line}")
    return parsing_errors

def aggregate_results(results):
    error_count = 0
    warning_count = 0
    info_count = 0

    for result in results:
        for finding in result['result']['results']:
            severity = finding.get('extra', {}).get('severity', '').lower()
            if severity == 'error':
                error_count += 1
            elif severity == 'warning':
                warning_count += 1
            elif severity == 'info':
                info_count += 1

    print(f"Total Errors: {error_count}")
    print(f"Total Warnings: {warning_count}")
    print(f"Total Info: {info_count}")

def main():
    repos = fetch_repositories(ORG_NAME)
    results = []
    parsing_errors = []

    if TEST_MODE:
        repos = repos[:2]  # Only process the first 2 repositories for testing

    for repo in repos:
        repo_name = repo['name']
        repo_url = repo['clone_url']
        repo_dir = os.path.join(REPOS_DIR, repo_name)

        print(f'Cloning repository {repo_name}...')
        clone_repository(repo_url, repo_dir)

        for rule_set, rule_path in SEMGRP_RULES.items():
            print(f'Running Semgrep with {rule_set} on repository {repo_name}...')
            semgrep_result, errors = run_semgrep(repo_dir, repo_name, rule_set, rule_path, verbose=True)
            if semgrep_result:
                results.append({
                    'repository': repo_name,
                    'rule_set': rule_set,
                    'result': semgrep_result
                })
            parsing_errors.extend(errors)

    # Aggregate and display the counts of errors, warnings, and info
    aggregate_results(results)

    # Save the parsing errors to a file
    with open("parsing_errors.log", 'w') as error_file:
        for error in parsing_errors:
            error_file.write(f"{error}\n")

    # Save the results to a JSON file
    with open(OUTPUT_JSON, 'w') as json_file:
        json.dump(results, json_file, indent=4)

    print(f'Results saved to {OUTPUT_JSON}')
    if parsing_errors:
        print(f'Parsing errors saved to parsing_errors.log')

if __name__ == '__main__':
    main()