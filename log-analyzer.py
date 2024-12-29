import argparse
import requests
import yaml
import logging

# Configure logging to go to a file, not the console
logging.basicConfig(
    filename='log-analyzer.log',
    filemode='a',  # Use 'w' if you want to overwrite on each run
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    logging.info("Starting main function")

    parser = argparse.ArgumentParser(
        description=(
            "Send a YAML-based prompt plus the last N lines from a file "
            "to Ollama."
        )
    )
    parser.add_argument(
        '-f',
        required=True,
        help='Path to the text file'
    )
    parser.add_argument(
        '-c',
        required=True,
        help='Path to the YAML config file'
    )
    parser.add_argument(
        '-p',
        default='11434',
        help='Ollama server port (default: 11434)'
    )
    parser.add_argument(
        '-m',
        default='llama3.2',
        help='Model name for Ollama (default: llama3.2)'
    )
    parser.add_argument(
        '-n',
        type=int,
        default=10,
        help='Number of lines to read from file (default: 10)'
    )
    args = parser.parse_args()

    logging.info(
        "Parsed arguments: file=%s, config=%s, port=%s, model=%s, lines=%d",
        args.f, args.c, args.p, args.m, args.n
    )

    # Read the last N lines from the file
    logging.info("Reading file: %s", args.f)
    with open(args.f, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    if len(lines) > args.n:
        last_n_lines = lines[-args.n:]
    else:
        last_n_lines = lines

    logging.debug("Last %d lines from file:\n%s",
                  args.n, "\n".join(last_n_lines))

    # Read the YAML config (prompt)
    logging.info("Reading config file: %s", args.c)
    with open(args.c, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    prompt = config.get("prompt", "")
    logging.debug("Prompt from config:\n%s", prompt)

    # Combine prompt with the last N lines
    full_prompt = f"{prompt}\n\n" + "\n".join(last_n_lines)
    logging.debug("Full prompt to send:\n%s", full_prompt)

    # Ollama endpoint (try '/api/generate' or '/generate' if needed)
    OLLAMA_URL = f"http://localhost:{args.p}/api/generate"
    data = {
        "model": args.m,
        "prompt": full_prompt,
        "stream": False
    }

    logging.info("Sending POST request to: %s", OLLAMA_URL)
    logging.debug("POST payload:\n%s", data)

    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=60)
        logging.debug("Response status: %d", response.status_code)
        logging.debug("Response body:\n%s", response.text)

        if response.status_code == 200:
            resp_data = response.json()
            if "response" in resp_data:
                logging.info("Received 'response' key from Ollama.")
                # Print only the model's "response" in a human-readable way
                final_answer = resp_data["response"].strip()
                print("\n" + "="*60)
                print("LLM RESPONSE:")
                print("="*60)
                print(final_answer)
                print("="*60 + "\n")
            else:
                logging.warning("No 'response' field found.")
                print("\nNo 'response' field found in the JSON.\n")
        else:
            logging.error(
                "Error: %d - %s", response.status_code, response.text
            )
            print(f"\nError: {response.status_code} - {response.text}\n")
    except requests.exceptions.RequestException as e:
        logging.error("Connection error: %s", e)
        print(f"\nConnection error: {e}\n")

    logging.info("Finished main function")

if __name__ == "__main__":
    main()

