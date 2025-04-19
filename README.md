Bluesky Disaster Post Classifier

This project fetches posts from Bluesky, classifies them as disaster-related, and then extracts key disaster information (location, severity, reasoning) using a language model (Claude). It helps in identifying and processing disaster-related content from Bluesky to better understand the situation and aid in disaster response analysis.

Features
Bluesky Post Fetcher: Fetches posts based on a search query.

Disaster Post Classifier: Filters posts that are related to disasters using a keyword-based classifier.

Disaster Information Extractor: Extracts disaster-related details (location, severity, and reasoning) using Claude's API.

LLM Integration: Uses a language model (Claude) to extract structured disaster event details from classified posts.

Requirements
Before you start, make sure you have the following dependencies installed:

Python 3.7+

.env file for Bluesky API credentials

Packages:

atproto: For interacting with the Bluesky API.

dotenv: To load environment variables.

llama_index: For interacting with Claude’s API.

pydantic: For data validation.

requests: For making HTTP requests (if needed).