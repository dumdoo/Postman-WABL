import os
import re
from dataclasses import dataclass

import jinja2
import jinja2.meta
import requests
from requests.auth import HTTPBasicAuth

from .config import CONFIG


@dataclass(frozen=True)
class EmailTemplate:
    html_template: str
    subject: str


SUBJECT_REGEX = re.compile(r"{#\s*(.*?)\s*:\s*(.*?)\s*#}", flags=re.IGNORECASE)
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
file_templates: dict[str, EmailTemplate] = {}  # Used to cache template


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
            subject = subject_match.group(2)
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
        file_templates[template_path] = EmailTemplate(html_template, subject)

    placeholder_vars = jinja2.meta.find_undeclared_variables(
        jinja_env.parse(html_template)
    )
    for placeholder in placeholder_vars:
        if placeholder not in data:
            raise ValueError(f"{placeholder} header not present")
    for header in data:
        if header not in placeholder_vars:
            raise Warning(f"Unused header {header}")

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
