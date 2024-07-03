import re

from pandas import read_csv

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
    people = read_csv(CONFIG["email-content"]["targets-file"])
    intial_logging(
        CONFIG["email-content"]["template"],
        CONFIG["email-content"]["base-template"],
        people,
        CONFIG["email-content"]["targets-file"],
    )

    for i, person in people.iterrows():  # Validate data
        name: str
        email: str

        name, email = person.Name, person.Email
        name = name.strip().title()
        email = email.strip().lower()

        if name == "":
            raise ValueError(f"Missing name at row {i+1}")
        if (
            re.match(
                r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
                email,
            )
            is None
        ):
            raise ValueError(f"Missing or malformed email address at row {i+1}")
    show_template()
    ask_for_start()
    init_email_task(len(people))
    for i, person in people.iterrows():
        name: str
        email: str

        name, email = person.Name, person.Email
        name = name.strip().title()
        email = email.strip().lower()
        send_email(name, email)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.exception("An unhandled exception occured.")
        raise e
