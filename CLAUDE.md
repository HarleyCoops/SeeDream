# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository is a search and tracking system for SeedDream 3.0, a Chinese-English bilingual image generation model by ByteDance. The project continuously searches for information about the model's implementation, which appears to be proprietary.

Key purpose: Automated daily searches across multiple platforms (GitHub, arXiv, Hugging Face) to find any publicly available information about SeedDream 3.0.

## Development Commands

### Running the Search Script
```bash
# Run the search script manually
python scripts/search_seeddream.py

# Run with GitHub token for better API rate limits
GITHUB_TOKEN=your_token python scripts/search_seeddream.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### GitHub Actions
- The search runs automatically daily at midnight UTC via GitHub Actions
- Manual trigger: Go to Actions tab → "SeedDream 3.0 Daily Search" → "Run workflow"
- Workflow file: `.github/workflows/seeddream_search.yml`

## Architecture

### Core Components

1. **Search Script** (`scripts/search_seeddream.py`)
   - Main searcher class: `SeedDreamSearcher`
   - Searches GitHub repos, GitHub code, arXiv papers, and Hugging Face models
   - Saves results in both JSON and Markdown formats to `search_results/`
   - Uses rate limiting to respect API limits
   - Automatically creates GitHub issues when new findings are discovered

2. **GitHub Actions Workflow** (`.github/workflows/seeddream_search.yml`)
   - Runs daily searches
   - Commits results automatically
   - Creates issues for new findings
   - Uses repository's GITHUB_TOKEN for API access

### Search Strategy

The script searches for multiple term variations:
- "SeedDream 3.0", "SeedDream3.0", "SeedDream-3.0"
- ByteDance-related terms
- Technical terms like "flow matching loss" and "representation alignment loss"

Specific organizations checked:
- ByteDance-Seed
- ByteDance
- bytedance

### Output Format

Results are saved with timestamps in two formats:
- `search_results/seeddream_search_YYYY-MM-DD_HH-MM-SS.json` - Complete data
- `search_results/seeddream_search_YYYY-MM-DD_HH-MM-SS.md` - Human-readable report

## Important Context

From `instructions.txt`: The primary goal is to find and download the SeedDream 3.0 codebase. The search should be persistent and creative, using any available tools or methods.

The technical report reference: arXiv:2504.11346v1