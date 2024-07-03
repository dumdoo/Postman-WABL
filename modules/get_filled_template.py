import os
from dataclasses import dataclass

import requests as re
from requests.auth import HTTPBasicAuth

from .config import CONFIG


@dataclass
class EmailTemplate:
    html_template: str
    subject: str


template: EmailTemplate = None  # Used to cache template


def get_filled_template(name: str) -> EmailTemplate:
    """Populates a template with information and returns it as a EmailTemplate"""
    global template  # Not usually a great idea but I can't be bothered

    # Check if template is cached, if not, create one by merging the base template, and the target template, and then use MJML api to convert to HTML.
    if template is None:

        with open(CONFIG["email-content"]["template"], "rt") as text_template_f:
            text_template = text_template_f.read()
            subject = (
                text_template.splitlines()[0].split("SUBJ:", maxsplit=1)[1].strip()
            )
            text_template = "\n".join(text_template.splitlines()[1:])
            with open("./templates/base.mjml", "rt") as base_template_f:
                mjml = base_template_f.read().replace("{{text}}", text_template)

        resp = re.post(
            "https://api.mjml.io/v1/render",
            auth=HTTPBasicAuth(
                CONFIG["mjml-api"]["application-id"], CONFIG["mjml-api"]["secret-key"]
            ),
            json={"mjml": mjml},
        )
        resp.raise_for_status()
        html_template = resp.json()["html"]
        template = EmailTemplate(html_template, subject)

    return EmailTemplate(
        template.html_template.replace("{{name}}", name), template.subject
    )


def preview_template():
    """Saves a template to disk"""
    with open(CONFIG["email-content"]["template"], "rt") as text_template:
        with open(CONFIG["email-content"]["base-template"], "rt") as base_template:
            mjml = base_template.read().replace(
                "{{text}}", "\n".join(text_template.read().splitlines[1:])
            )

        resp = re.post(
            "https://api.mjml.io/v1/render",
            auth=HTTPBasicAuth(
                CONFIG["mjml-api"]["application-id"], CONFIG["mjml-api"]["secret-key"]
            ),
            json={"mjml": mjml},
        )
        resp.raise_for_status()
        template = resp.json()["html"]

        with open(".temp.html", "wt") as f:
            f.write(template)
            os.startfile(".temp.html")


if __name__ == "__main__":
    preview_template()
