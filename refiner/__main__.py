import json
import logging
import os
import sys
import traceback
import zipfile
import requests

from refiner.refine import Refiner
from refiner.config import settings

logging.basicConfig(level=logging.INFO, format="%(message)s")


def run() -> None:
    """Transform all input files into the database."""
    response = requests.get('https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new')
    raise Exception("WHAT THE HELL", float(response.text.strip()))
    input_files_exist = os.path.isdir(settings.INPUT_DIR) and bool(
        os.listdir(settings.INPUT_DIR)
    )

    if not input_files_exist:
        raise FileNotFoundError(f"No input files found in {settings.INPUT_DIR}")
    extract_input()

    refiner = Refiner()

    output = refiner.transform()

    output_path = os.path.join(settings.OUTPUT_DIR, "output.json")
    with open(output_path, "w") as f:
        json.dump(output.model_dump(), f, indent=2)
    logging.info(f"Data transformation complete: {output}")


def extract_input() -> None:
    """
    If the input directory contains any zip files, extract them
    :return:
    """
    for input_filename in os.listdir(settings.INPUT_DIR):
        input_file = os.path.join(settings.INPUT_DIR, input_filename)

        if zipfile.is_zipfile(input_file):
            with zipfile.ZipFile(input_file, "r") as zip_ref:
                zip_ref.extractall(settings.INPUT_DIR)


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logging.error(f"Error during data transformation: {e}")
        traceback.print_exc()
        sys.exit(1)
