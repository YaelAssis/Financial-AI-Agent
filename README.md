# Financial AI Agent

## Overview
An autonomous financial support agent built with Python. This project demonstrates the integration of a custom-trained model via the OpenAI API to parse data, process queries, and provide logical, automated responses. 

## Key Features
*   **Automated Logic:** Processes structured and unstructured input to generate accurate support responses.
*   **API Integration:** Seamlessly communicates with the OpenAI API for advanced language modeling.
*   **Security First:** Uses environment variables to securely manage sensitive API keys without hardcoding them into the repository.

## Technologies Used
*   Python
*   OpenAI API
*   Jupyter Notebook

## Setup and Installation

1. Clone the repository:
   git clone https://github.com/YaelAssis/Financial-AI-Agent.git
   
2. Install the required dependencies (e.g., `openai`):
   pip install openai
   
3. **Security Setup:** Create a `.env` file in the root directory and add your OpenAI API key. (Never commit this file to GitHub):
   OPENAI_API_KEY="your_actual_api_key_here"
   
4. Open and run the `final_model.ipynb` notebook in your local environment.
