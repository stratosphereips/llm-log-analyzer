import argparse
import requests
import yaml
import logging
from dotenv import load_dotenv
import os
from openai import OpenAI
from datetime import datetime

# Configure logging to go to a file, not the console
logging.basicConfig(
    filename='log-analyzer.log',
    filemode='a',  # Use 'w' if you want to overwrite on each run
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def call_ollama(full_prompt, model, port):
    OLLAMA_URL = f"http://localhost:{port}/api/generate"
    data = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "temperature": 0,
        "max_tokens": 4096  # Assuming 4096 is the max tokens for Ollama
    }
    headers = {"Content-Type": "application/json"}
    return requests.post(OLLAMA_URL, json=data, headers=headers, timeout=300)

def call_openai(full_prompt, model):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        logging.error("OpenAI API key not found in .env file.")
        print("\nOpenAI API key not found in .env file.\n")
        return None

    client = OpenAI(api_key=OPENAI_API_KEY)
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model=model,
            max_tokens=4096,
            temperature=0
        )
        return response
    except Exception as e:
        logging.error("OpenAI API call error: %s", e)
        print(f"\nOpenAI API call error: {e}\n")
        return None

def save_response_to_file(filename, log_filename, num_lines, system, model, answer):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"Datetime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Log Filename: {log_filename}\n")
        f.write(f"Number of Lines Analyzed: {num_lines}\n")
        f.write(f"System: {system}\n")
        f.write(f"Model: {model}\n")
        f.write(f"Answer:\n{answer}\n")
        f.write("="*60 + "\n\n")

def main():
    logging.info("# Starting LLM log analyzer")
    print('Starting the LLM log analyzer')

    # Load environment variables from .env file
    load_dotenv()

    parser = argparse.ArgumentParser(
        description=(
            "Send a YAML-based prompt plus the last N lines from a file "
            "to Ollama or OpenAI."
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
    parser.add_argument(
        '-s',
        choices=['ollama', 'openai'],
        default='ollama',
        help='Select the server to use: ollama or openai (default: ollama)'
    )
    parser.add_argument(
        '-om',
        default='gpt-4',
        help='Model name for OpenAI (default: gpt-4)'
    )
    parser.add_argument(
        '-o',
        default='log-analyzer-output.txt',
        help='Output file to save the response (default: log-analyzer-output.txt)'
    )
    args = parser.parse_args()

    logging.info(
        "Parsed arguments: file=%s, config=%s, port=%s, model=%s, lines=%d, server=%s, openai_model=%s, output=%s",
        args.f, args.c, args.p, args.m, args.n, args.s, args.om, args.o
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

    if args.s == 'ollama':
        print(f'-> Sending POST request to Ollama')
        logging.info("Sending POST request to Ollama")
        response = call_ollama(full_prompt, args.m, args.p)
    else:
        print(f'-> Sending POST request to OpenAI')
        logging.info("Sending POST request to OpenAI")
        response = call_openai(full_prompt, args.om)

    if response:
        if args.s == 'ollama':
            logging.debug("Response status: %d", response.status_code)
            logging.debug("Response body:\n%s", response.text)
            if response.status_code == 200:
                resp_data = response.json()
                if "response" in resp_data:
                    final_answer = resp_data["response"].strip()
                else:
                    logging.warning("No valid response field found.")
                    print("\nNo valid response field found in the JSON.\n")
                    return
            else:
                logging.error(
                    "Error: %d - %s", response.status_code, response.text
                )
                print(f"\nError: {response.status_code} - {response.text}\n")
                return
        else:
            if response.choices and len(response.choices) > 0:
                final_answer = response.choices[0].message.content.strip()
            else:
                logging.warning("No valid response field found.")
                print("\nNo valid response field found in the JSON.\n")
                return

        logging.info("Received valid response.")
        print("\n" + "="*60)
        print("LLM RESPONSE:")
        print("="*60)
        print(final_answer)
        print("="*60 + "\n")

        # Save the response to a file
        save_response_to_file(args.o, args.f, args.n, args.s, args.m if args.s == 'ollama' else args.om, final_answer)
    else:
        logging.error("Failed to get a response from the server.")

    logging.info("Finished main function")

if __name__ == "__main__":
    main()