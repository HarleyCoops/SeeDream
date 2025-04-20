# SeedDream 3.0 Search

This repository is dedicated to tracking and searching for information about SeedDream 3.0, a high-performance Chinese-English bilingual image generation foundation model developed by ByteDance Seed Team.

## About SeedDream 3.0

SeedDream 3.0 is described in a technical report (arXiv:2504.11346v1) and uses advanced techniques like flow matching loss and representation alignment loss. It's integrated into platforms like Doubao and Jimeng, but the actual implementation appears to be proprietary.

## Automated Daily Search

This repository contains a GitHub Action that automatically searches for SeedDream 3.0 information every day at midnight UTC. The search includes:

1. GitHub repositories and code
2. arXiv papers
3. Hugging Face models
4. (Future) Web search results

When new information is found, the action:
1. Saves the search results to the `search_results` directory
2. Creates a GitHub issue with the findings

## Search Results

Search results are stored in the `search_results` directory in both JSON and Markdown formats. Each search run is timestamped, allowing for easy tracking of when new information becomes available.

## Manual Triggering

You can manually trigger the search workflow by:
1. Going to the "Actions" tab
2. Selecting the "SeedDream 3.0 Daily Search" workflow
3. Clicking "Run workflow"

## Technical Details

The search is implemented in Python and uses the following APIs:
- GitHub API for repository and code search
- arXiv API for academic papers
- Hugging Face API for models

The search script is located at `scripts/search_seeddream.py` and the GitHub Action workflow is defined in `.github/workflows/seeddream_search.yml`.

## Contributing

If you have information about SeedDream 3.0 or would like to improve the search functionality, please feel free to open an issue or submit a pull request.

## License

This project is open source and available under the MIT License.
