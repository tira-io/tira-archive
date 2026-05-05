#!/usr/bin/env python3
import click
import requests
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime
from tqdm import tqdm
from pathlib import Path
import json


def track_execution(func, retries=3, timeout=300):
    last_exception = None

    for attempt in range(1, retries + 1):
        start_time = time.perf_counter()

        try:
            # Use ThreadPoolExecutor to enforce the timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func)
                # .result() will raise TimeoutError if it hits the limit
                result = future.result(timeout=timeout)

            return time.perf_counter() - start_time

        except TimeoutError:
            print(f"Attempt {attempt} failed: Execution timed out after {timeout}s")
            last_exception = Exception(f"Function timed out after {timeout} seconds")
        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")
            last_exception = e
        finally:
            pass

def well_known_is_available(token):
    ret = requests.get("https://www.tira.io/.well-known/tira/client")
    if not ret.ok:
        raise ValueError("Well known could not be retrieved.")
    ret = ret.json()
    if "api" not in ret or ret["api"] != 'https://www.tira.io':
        raise ValueError("invalid response")

ALL_TESTS = [
    well_known_is_available,
]

@click.command()
@click.argument("token")
@click.argument("output_file")
def main(token, output_file):
    current_iso = datetime.now().isoformat()
    ret = {"timestamp": current_iso}
    for test in tqdm(ALL_TESTS):
        result = track_execution(lambda: test(token))
        ret[test.__name__] = result

    Path(output_file).parent.mkdir(exist_ok=True, parents=True)

    if not Path(output_file).is_file():
        Path(output_file).touch()

    with open(output_file, "a") as f:
        f.write(json.dumps(ret) + "\n")

if __name__ == '__main__':
    main()
