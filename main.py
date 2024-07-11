import csv
import re

from bidict import bidict

from modules.config import CONFIG
from modules.logger import (
    ask_for_start,
    init_email_task,
    initial_logging,
    log,
    show_template,
)
from modules.send_email import send_email

EMAIL_REGEX = re.compile(
    r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@"
    r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
)


def is_valid_email(email: str) -> bool:
    return not EMAIL_REGEX.fullmatch(email) is None


def validate_headers(headers: list[str] | None) -> None:
    if headers is None:  # Check for lack of headers ie empty file
        raise ValueError("No data found in data file.")

    if "" in headers:  # Check for unnamed headers
        raise ValueError("Empty header detected.")

    lowered_headers = [*map(lambda x: x.lower().strip(), headers)]
    if lowered_headers[0].startswith("\ufeff"):  # Check for BOM
        raise ValueError("BOM detected. Please re-save file in UTF-8 without BOM.")

    if "email" not in lowered_headers:  # Check for pressence of email header
        raise ValueError("Email header not found in data_file.")

    if len(set(lowered_headers)) != len(lowered_headers):  # Check for repeated headers
        raise ValueError("Repeated headers present.")


def main():
    log.info("Using case insensitive variables and headers.")
    log.info(
        "Remember, this program strips all preceding and ensuing whitespace from all fields."
    )

    data_file_path: str = CONFIG["email-content"]["targets-file"]
    with open(data_file_path, errors="strict", encoding="utf-8") as csv_file:
        people_reader = csv.reader(csv_file)

        headers = next(people_reader, None)
        validate_headers(headers)
        headers = [
            *map(lambda header: header.lower().strip(), headers)
        ]  # Lowercase headers

        header_pos_map: bidict[str, int] = bidict(
            {(k, v) for (v, k) in enumerate(headers)}
        )  # Header - pos map

        people: list[dict[str, str]] = []
        for i, person_data in enumerate(people_reader):
            row_number = i + 1  # Add 1 for offsetting zero-indexing
            # Check for empty row
            if len(person_data) == 0:
                log.warn(f"Empty row ({row_number}) found in data file. Skipping row.")
                continue

            # Check for stray, headerless data
            if len(person_data) > len(headers):
                raise ValueError(f"Stray data found at row {row_number}.")

            # Check each data-field for being empty, warn if it is
            # Check to make sure email is there for all rows, and is valid email
            email = person_data[header_pos_map["email"]].strip().lower()
            if not is_valid_email(email):
                raise ValueError(
                    f"Missing or malformed email address at row {row_number}'"
                )
            for i, field in enumerate(person_data):  # Ensure all fields are not empty
                if field == "":
                    raise ValueError(
                        f"Missing data at row {row_number} under column {header_pos_map.inv[i]}"
                    )

            d: dict[str, str] = {}
            for i, field in enumerate(person_data):
                header = header_pos_map.inv[i]
                if header == "email":
                    field = field.lower()

                d[header] = field.strip()

            people.append(d)

        initial_logging(
            CONFIG["email-content"]["template"],
            CONFIG["email-content"]["base-template"],
            people,
            CONFIG["email-content"]["targets-file"],
        )

    show_template()
    ask_for_start()
    init_email_task(len(people))
    for data in people:
        send_email(data)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.exception("An unhandled exception occured.")
        raise e
