# Usage
1. Install [Pipenv](https://docs.pipenv.org/install/#installing-pipenv), if not already installed.
2. Install dependencies with `pipenv install`.
3. Start the virtual environment shell with `pipenv shell`.
4. Set environment variables `OPENAI_API_KEY` and `REPLICATE_API_TOKEN` with the OpenAI API key and the [Replicate](https://replicate.com/) API token respectively. (The replicate API token is required for `codellama-34b` inferences and hence optional.)
5. Run `python3 cli.py --help` to for the cli usage options.
6. For a local in-memory RAG with `gpt-4` as the llm, and a top-level directory `~/infra` containing the terraform state files, start the cli with `python3 cli.py -m gpt-4 -d ~/infra` and start chatting away!
7. For a RAG using the OpenAI Assistants API, start the cli with `python3 cli.py -m -a ~/infra` and start chatting away!

# Example Usage

1. Go through this [tutorial](https://developer.hashicorp.com/terraform/tutorials/networking/multicloud-kubernetes?ajs_aid=7e134de7-1e00-4e81-8ac4-13bd8f9acd8a&product_intent=terraform#clean-up-resources) for a federated muticloud kubernetes clusters deployment.  
