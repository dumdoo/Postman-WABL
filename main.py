import csv
import re

from modules.config import CONFIG
from modules.logger import (
    ask_for_start,
    init_email_task,
    intial_logging,
    log,
    show_template,
)
from modules.send_email import send_email


def main():
    data_file_path = CONFIG["email-content"]["targets-file"]
    with open(data_file_path) as csv_file:
        people_reader = csv.reader(csv_file)

        headers = next(people_reader, None)
        match headers:
            case None:
                raise ValueError(f"No data found in data file {data_file_path}.")
            case [name_header, email_header]:
                if name_header != "Name" or email_header != "Email":
                    raise ValueError(
                        f"Improperly formatted data found. Data file headers must be 'Name,Email' not '{name_header},{email_header}'. (Case and order-sensitive)"
                    )
            case headers:
                raise ValueError(
                    f"Too many or too few data file headers found. Data file headers must be 'Name,Email' only, not '{','.join(headers)}' (Case and order sensitive)"
                )

        people = []
        for i, data in enumerate(people_reader):
            if len(data) == 0:
                log.warn("Empty row found in data file. Skipping row.")
                continue
            name, email = data
            if name == "":
                raise ValueError(f"Missing name at row {i+2}")
            if (
                re.match(
                    r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
                    email,
                )
                is None
            ):
                raise ValueError(
                    f"Missing or malformed email address at row {i+2} for name '{name}'"
                )
            people.append((name.strip().title(), email.strip().lower()))
        intial_logging(
            CONFIG["email-content"]["template"],
            CONFIG["email-content"]["base-template"],
            people,
            CONFIG["email-content"]["targets-file"],
        )

    show_template()
    ask_for_start()
    init_email_task(len(people))
    for name, email in people:
        send_email(name, email)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.exception("An unhandled exception occured.")
        raise e
