import os
import re
from dataclasses import dataclass

import jinja2 as jinja
import requests
from requests.auth import HTTPBasicAuth

from .config import CONFIG


@dataclass(frozen=True)
class EmailTemplate:
    html_template: str
    subject: str


SUBJECT_REGEX = re.compile(
    r"{#\s*(.*?)\s*:\s*(?<subject>.*?)\s*#}", flags=re.IGNORECASE
)
jinja_env = jinja.Environment(loader=jinja.BaseLoader)
file_templates: list[dict[str, EmailTemplate]] = None  # Used to cache template


def get_filled_template(data: dict[str, str]) -> EmailTemplate:
    """Populates a template with information and returns it as a EmailTemplate"""
    global file_templates

    # Check if template is cached, if not, create one by merging the base template and the partial template, and then use MJML api to convert to HTML.
    template_path = CONFIG["email-content"]["template"]

    if template_path not in file_templates:
        with open(CONFIG["email-content"]["template"], "rt") as partial_template_f:
            partial_template = partial_template_f.read()
            subject_match = SUBJECT_REGEX.match(partial_template)
            if subject_match is None:
                raise ValueError("No subject found in template file.")
            subject = subject_match.group("subject")
            partial_template = jinja_env.from_string(partial_template).render()

        resp = requests.post(
            "https://api.mjml.io/v1/render",
            auth=HTTPBasicAuth(
                CONFIG["mjml-api"]["application-id"], CONFIG["mjml-api"]["secret-key"]
            ),
            json={"mjml": partial_template},
        )
        resp.raise_for_status()
        html_template = resp.json()["html"]
        file_templates.append({template_path, EmailTemplate(html_template, subject)})
    template: EmailTemplate = file_templates[template_path]
    return EmailTemplate(
        jinja_env.from_string(template.html_template).render(data), template.subject
    )


def preview_template():
    """Saves a template to disk"""
    with open(CONFIG["email-content"]["template"], "rt") as text_template:
        with open(CONFIG["email-content"]["base-template"], "rt") as base_template:
            mjml = base_template.read().replace(
                "{{text}}", "\n".join(text_template.read().splitlines()[1:])
            )

        resp = requests.post(
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
            try:
                os.startfile(".temp.html")
            except AttributeError as e:
                raise AttributeError(
                    "os.startfile unsupported by system. Please open .temp.html (locatated in the cwd) to preview template"
                ) from e


if __name__ == "__main__":
    preview_template()
