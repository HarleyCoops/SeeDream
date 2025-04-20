#!/usr/bin/env python3
"""
SeedDream 3.0 Search Script

This script performs a comprehensive search for SeedDream 3.0 information,
including code repositories, papers, and related resources.
It saves the results to a markdown file with a timestamp.
"""

import os
import requests
import json
import datetime
import time
from pathlib import Path
import re
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('seeddream_search')

# Constants
GITHUB_API_URL = "https://api.github.com"
SEARCH_TERMS = [
    "SeedDream 3.0",
    "SeedDream3.0",
    "SeedDream-3.0",
    "ByteDance Seed Team SeedDream",
    "ByteDance-Seed SeedDream",
    "flow matching loss SeedDream",
    "representation alignment loss SeedDream",
    "Chinese-English bilingual image generation SeedDream",
]
GITHUB_ORGS_TO_CHECK = [
    "ByteDance-Seed",
    "ByteDance",
    "bytedance",
]
ARXIV_QUERY = "SeedDream+3.0+OR+ByteDance+Seed+Team"
MAX_RESULTS_PER_SOURCE = 10

class SeedDreamSearcher:
    """Class to search for SeedDream 3.0 information across various sources."""
    
    def __init__(self, github_token: Optional[str] = None):
        """Initialize the searcher with optional GitHub token."""
        self.github_token = github_token
        self.github_headers = {}
        if github_token:
            self.github_headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        
        # Create results directory if it doesn't exist
        self.results_dir = Path("search_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Timestamp for this search run
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
    def search_github(self) -> List[Dict[str, Any]]:
        """Search GitHub for SeedDream 3.0 repositories and code."""
        logger.info("Searching GitHub for SeedDream 3.0...")
        results = []
        
        # Search repositories
        for term in SEARCH_TERMS:
            try:
                encoded_term = term.replace(" ", "+")
                url = f"{GITHUB_API_URL}/search/repositories?q={encoded_term}&sort=updated&order=desc"
                response = requests.get(url, headers=self.github_headers)
                response.raise_for_status()
                data = response.json()
                
                if "items" in data:
                    for repo in data["items"][:MAX_RESULTS_PER_SOURCE]:
                        results.append({
                            "type": "github_repo",
                            "name": repo["full_name"],
                            "url": repo["html_url"],
                            "description": repo["description"],
                            "stars": repo["stargazers_count"],
                            "updated_at": repo["updated_at"],
                            "search_term": term
                        })
                
                # Respect GitHub API rate limits
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error searching GitHub repositories for '{term}': {e}")
        
        # Check specific organizations
        for org in GITHUB_ORGS_TO_CHECK:
            try:
                url = f"{GITHUB_API_URL}/orgs/{org}/repos?sort=updated&direction=desc"
                response = requests.get(url, headers=self.github_headers)
                response.raise_for_status()
                repos = response.json()
                
                for repo in repos:
                    # Check if repo name or description contains any of our search terms
                    repo_text = f"{repo['name']} {repo.get('description', '')}".lower()
                    if any(term.lower().replace(" ", "") in repo_text.replace(" ", "") for term in SEARCH_TERMS):
                        results.append({
                            "type": "github_org_repo",
                            "name": repo["full_name"],
                            "url": repo["html_url"],
                            "description": repo["description"],
                            "stars": repo["stargazers_count"],
                            "updated_at": repo["updated_at"],
                            "organization": org
                        })
                
                # Respect GitHub API rate limits
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error checking repositories for organization '{org}': {e}")
        
        # Search code
        for term in SEARCH_TERMS[:3]:  # Limit to first few terms to avoid rate limiting
            try:
                encoded_term = term.replace(" ", "+")
                url = f"{GITHUB_API_URL}/search/code?q={encoded_term}&sort=indexed&order=desc"
                response = requests.get(url, headers=self.github_headers)
                response.raise_for_status()
                data = response.json()
                
                if "items" in data:
                    for item in data["items"][:MAX_RESULTS_PER_SOURCE]:
                        results.append({
                            "type": "github_code",
                            "repo": item["repository"]["full_name"],
                            "path": item["path"],
                            "url": item["html_url"],
                            "search_term": term
                        })
                
                # Respect GitHub API rate limits
                time.sleep(5)  # Longer sleep for code search as it's more rate-limited
            except Exception as e:
                logger.error(f"Error searching GitHub code for '{term}': {e}")
        
        return results
    
    def search_arxiv(self) -> List[Dict[str, Any]]:
        """Search arXiv for SeedDream 3.0 papers."""
        logger.info("Searching arXiv for SeedDream 3.0 papers...")
        results = []
        
        try:
            url = f"http://export.arxiv.org/api/query?search_query={ARXIV_QUERY}&start=0&max_results={MAX_RESULTS_PER_SOURCE}"
            response = requests.get(url)
            response.raise_for_status()
            
            # Simple regex-based extraction (for demo purposes)
            # In a production environment, use a proper XML parser
            entries = re.findall(r'<entry>(.*?)</entry>', response.text, re.DOTALL)
            
            for entry in entries:
                title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
                link_match = re.search(r'<id>(.*?)</id>', entry, re.DOTALL)
                summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
                published_match = re.search(r'<published>(.*?)</published>', entry, re.DOTALL)
                
                if title_match and link_match:
                    title = title_match.group(1).strip()
                    link = link_match.group(1).strip()
                    summary = summary_match.group(1).strip() if summary_match else ""
                    published = published_match.group(1).strip() if published_match else ""
                    
                    # Check if related to SeedDream
                    if any(term.lower().replace(" ", "") in title.lower().replace(" ", "") or 
                           term.lower().replace(" ", "") in summary.lower().replace(" ", "") 
                           for term in SEARCH_TERMS):
                        results.append({
                            "type": "arxiv_paper",
                            "title": title,
                            "url": link,
                            "summary": summary,
                            "published": published
                        })
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
        
        return results
    
    def search_huggingface(self) -> List[Dict[str, Any]]:
        """Search Hugging Face for SeedDream 3.0 models."""
        logger.info("Searching Hugging Face for SeedDream 3.0 models...")
        results = []
        
        for term in SEARCH_TERMS:
            try:
                encoded_term = term.replace(" ", "%20")
                url = f"https://huggingface.co/api/models?search={encoded_term}"
                response = requests.get(url)
                response.raise_for_status()
                models = response.json()
                
                for model in models[:MAX_RESULTS_PER_SOURCE]:
                    results.append({
                        "type": "huggingface_model",
                        "name": model.get("modelId", ""),
                        "url": f"https://huggingface.co/{model.get('modelId', '')}",
                        "downloads": model.get("downloads", 0),
                        "likes": model.get("likes", 0),
                        "tags": model.get("tags", []),
                        "search_term": term
                    })
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error searching Hugging Face for '{term}': {e}")
        
        return results
    
    def search_web(self) -> List[Dict[str, Any]]:
        """
        Placeholder for web search functionality.
        In a real implementation, this would use a search API like Google Custom Search or Bing.
        """
        logger.info("Web search functionality would be implemented here.")
        # This is a placeholder - in a real implementation, you would use a search API
        return []
    
    def run_search(self) -> Dict[str, List[Dict[str, Any]]]:
        """Run all search methods and compile results."""
        logger.info("Starting comprehensive search for SeedDream 3.0...")
        
        results = {
            "github": self.search_github(),
            "arxiv": self.search_arxiv(),
            "huggingface": self.search_huggingface(),
            "web": self.search_web(),
            "timestamp": self.timestamp
        }
        
        logger.info(f"Search completed. Found: {len(results['github'])} GitHub results, "
                   f"{len(results['arxiv'])} arXiv papers, "
                   f"{len(results['huggingface'])} Hugging Face models")
        
        return results
    
    def save_results(self, results: Dict[str, List[Dict[str, Any]]]) -> str:
        """Save search results to JSON and markdown files."""
        # Save as JSON
        json_path = self.results_dir / f"seeddream_search_{self.timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save as Markdown
        md_path = self.results_dir / f"seeddream_search_{self.timestamp}.md"
        with open(md_path, 'w') as f:
            f.write(f"# SeedDream 3.0 Search Results\n\n")
            f.write(f"**Search Date:** {self.timestamp.replace('_', ' ')}\n\n")
            
            # GitHub results
            f.write(f"## GitHub Results ({len(results['github'])} found)\n\n")
            if results['github']:
                for item in results['github']:
                    if item['type'] == 'github_repo' or item['type'] == 'github_org_repo':
                        f.write(f"### [{item['name']}]({item['url']})\n\n")
                        f.write(f"**Description:** {item.get('description', 'No description')}\n\n")
                        f.write(f"**Stars:** {item['stars']}  \n")
                        f.write(f"**Updated:** {item['updated_at']}  \n")
                        if 'search_term' in item:
                            f.write(f"**Matched:** {item['search_term']}  \n")
                        f.write("\n---\n\n")
                    elif item['type'] == 'github_code':
                        f.write(f"### Code: [{item['repo']} / {item['path']}]({item['url']})\n\n")
                        f.write(f"**Matched:** {item['search_term']}  \n")
                        f.write("\n---\n\n")
            else:
                f.write("No GitHub results found.\n\n")
            
            # arXiv results
            f.write(f"## arXiv Papers ({len(results['arxiv'])} found)\n\n")
            if results['arxiv']:
                for paper in results['arxiv']:
                    f.write(f"### [{paper['title']}]({paper['url']})\n\n")
                    f.write(f"**Published:** {paper['published']}  \n")
                    f.write(f"**Summary:** {paper['summary'][:300]}...  \n\n")
                    f.write("\n---\n\n")
            else:
                f.write("No arXiv papers found.\n\n")
            
            # Hugging Face results
            f.write(f"## Hugging Face Models ({len(results['huggingface'])} found)\n\n")
            if results['huggingface']:
                for model in results['huggingface']:
                    f.write(f"### [{model['name']}]({model['url']})\n\n")
                    f.write(f"**Downloads:** {model['downloads']}  \n")
                    f.write(f"**Likes:** {model['likes']}  \n")
                    f.write(f"**Tags:** {', '.join(model['tags'])}  \n")
                    f.write(f"**Matched:** {model['search_term']}  \n\n")
                    f.write("\n---\n\n")
            else:
                f.write("No Hugging Face models found.\n\n")
            
            # Web results
            f.write(f"## Web Results ({len(results['web'])} found)\n\n")
            if results['web']:
                for item in results['web']:
                    f.write(f"### [{item['title']}]({item['url']})\n\n")
                    f.write(f"**Source:** {item.get('source', 'Unknown')}  \n")
                    f.write(f"**Snippet:** {item.get('snippet', 'No snippet available')}  \n\n")
                    f.write("\n---\n\n")
            else:
                f.write("No web results found.\n\n")
            
            # Comparison with previous results
            f.write("## Changes Since Last Search\n\n")
            f.write("*Comparison with previous results would be shown here.*\n\n")
            
            # Conclusion
            f.write("## Conclusion\n\n")
            f.write("This report was automatically generated by the SeedDream 3.0 search script.\n")
            f.write("For more information, check the JSON file for complete data.\n")
        
        logger.info(f"Results saved to {json_path} and {md_path}")
        return str(md_path)

def main():
    """Main function to run the search."""
    # Get GitHub token from environment variable if available
    github_token = os.environ.get("GITHUB_TOKEN")
    
    searcher = SeedDreamSearcher(github_token)
    results = searcher.run_search()
    output_path = searcher.save_results(results)
    
    print(f"Search completed successfully. Results saved to {output_path}")
    
    # If running in GitHub Actions, output the path for use in the workflow
    if os.environ.get("GITHUB_ACTIONS") == "true":
        with open(os.environ.get("GITHUB_OUTPUT", ""), "a") as f:
            f.write(f"result_path={output_path}\n")

if __name__ == "__main__":
    main()
