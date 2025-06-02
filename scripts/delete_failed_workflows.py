#!/usr/bin/env python3
"""
Delete failed workflow runs from GitHub repository.
Requires GITHUB_TOKEN environment variable with repo permissions.
"""

import os
import requests
import sys
import time

# Configuration
REPO_OWNER = "HarleyCoops"
REPO_NAME = "SeeDream"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN environment variable not set")
    print("Please set it with: export GITHUB_TOKEN=your_personal_access_token")
    sys.exit(1)

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_workflow_runs(status="failure", per_page=100):
    """Get workflow runs with specified status."""
    runs = []
    page = 1
    
    while True:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
        params = {
            "status": status,
            "per_page": per_page,
            "page": page
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching runs: {response.status_code} - {response.text}")
            break
            
        data = response.json()
        workflow_runs = data.get("workflow_runs", [])
        
        if not workflow_runs:
            break
            
        runs.extend(workflow_runs)
        page += 1
        
        # Check if we've fetched all pages
        if len(workflow_runs) < per_page:
            break
    
    return runs

def delete_workflow_run(run_id):
    """Delete a specific workflow run."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}"
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 204:
        return True
    else:
        print(f"Error deleting run {run_id}: {response.status_code} - {response.text}")
        return False

def main():
    print(f"Fetching failed workflow runs for {REPO_OWNER}/{REPO_NAME}...")
    
    # Get all failed runs
    failed_runs = get_workflow_runs(status="failure")
    print(f"Found {len(failed_runs)} failed workflow runs")
    
    if not failed_runs:
        print("No failed runs to delete")
        return
    
    # Show summary
    print("\nFailed runs by workflow:")
    workflow_counts = {}
    for run in failed_runs:
        workflow_name = run["name"]
        workflow_counts[workflow_name] = workflow_counts.get(workflow_name, 0) + 1
    
    for workflow, count in workflow_counts.items():
        print(f"  - {workflow}: {count} failed runs")
    
    # Ask for confirmation
    response = input(f"\nDo you want to delete all {len(failed_runs)} failed runs? (yes/no): ")
    if response.lower() != "yes":
        print("Cancelled")
        return
    
    # Delete runs
    print("\nDeleting failed runs...")
    deleted = 0
    failed = 0
    
    for i, run in enumerate(failed_runs):
        run_id = run["id"]
        workflow_name = run["name"]
        created_at = run["created_at"]
        
        print(f"[{i+1}/{len(failed_runs)}] Deleting run {run_id} from '{workflow_name}' (created: {created_at})...", end="")
        
        if delete_workflow_run(run_id):
            print(" ✓")
            deleted += 1
        else:
            print(" ✗")
            failed += 1
        
        # Rate limiting - GitHub allows 1000 requests per hour
        if (i + 1) % 10 == 0:
            time.sleep(1)  # Brief pause every 10 deletions
    
    print(f"\nDeletion complete: {deleted} deleted, {failed} failed")

if __name__ == "__main__":
    main()