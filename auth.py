import requests
import json
import time
import logging
from requests.auth import HTTPBasicAuth


def retry_request(method, url, max_retries=10, timeout=300, delay=5, **kwargs):
    """
    Generic retry logic.
    If the request fails, retry; after timeout, re-login.
    If re-login exceeds max_retries, raise an error to terminate the script.

    :param method     : Request method (e.g., SESS.get, SESS.patch)
    :param url        : Target URL for the request
    :param max_retries: Maximum number of re-login attempts
    :param timeout    : Timeout for each retry
    :param delay      : Interval time between two requests
    :param kwargs     : Request parameters (e.g., json, headers)
    """
    retry_count = 0
    start_time = time.time()
    while retry_count <= max_retries:
        try:
            response = method(url, **kwargs)
            response.raise_for_status()
            result = response.json()
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            if elapsed_time < timeout:
                logging.warning(
                    f"Request to {url} failed. Retrying after {delay} seconds... Elapsed time: {elapsed_time:.2f}s."
                )
                time.sleep(delay)
            else:
                if retry_count < max_retries:
                    logging.warning(
                        f"Timeout reached. Attempting re-login... (Retry count: {retry_count + 1})"
                    )
                    global SESS
                    SESS = global_sign_in()
                    start_time = time.time()
                    retry_count += 1
                else:
                    logging.error(
                        f"Request to {url} failed after {max_retries} re-login attempts."
                    )
                    return None
                    # raise RuntimeError(f"Request to {url} failed after {max_retries} re-login attempts.") from e


def setup_logging(
    level=logging.INFO, log_file="app.log", log_to_file=True, log_to_console=True
):
    """
    Configure logging settings with options to output to console and file.
    :param level: Logging level, defaults to INFO
    :param log_file: Log file path, defaults to 'app.log'
    :param log_to_file: Whether to output logs to a file, defaults to True
    :param log_to_console: Whether to output logs to console, defaults to True
    """
    handlers = []
    if log_to_console:
        handlers.append(logging.StreamHandler())
    if log_to_file:
        handlers.append(logging.FileHandler(log_file, mode="w"))
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def global_sign_in():
    credential_file = "./credentials.json"
    with open(credential_file) as f:
        print("Reading credentials...")
        credentials = json.load(f)
        email = credentials.get("username")
        password = credentials.get("password")
        print(f"Email: {email}")

    sess = requests.Session()
    sess.auth = HTTPBasicAuth(email, password)
    timeout = 300
    start_time = time.time()
    while True:
        try:
            response = sess.post("https://api.worldquantbrain.com/authentication")
            response.raise_for_status()
            break
        except:
            elapsed_time = time.time() - start_time
            print("Connection down, trying to login again...")
            if elapsed_time >= timeout:
                print(f"{email} login Failed, returning None.")
                return None
            time.sleep(15)
    id = response.json().get("user").get("id")
    print(f"{id} Login to WorldQuant BRAIN successfully.")
    return sess


if __name__ == "__main__":
    SESS = global_sign_in()
