# Postman with a Broken Leg

Sends automated, beautiful, bodged emails en masse!

<a href="https://project-types.github.io/#toy">
  <img src="https://img.shields.io/badge/project%20type-toy-blue?style=for-the-badge" alt="Toy Badge"/>
</a>

![License GPL 3.0](https://img.shields.io/badge/License-GPL%203.0-purple?style=for-the-badge)
![Python Badge](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=for-the-badge)
[![code style: black](https://img.shields.io/badge/code_style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=for-the-badge&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&style=for-the-badge)](https://github.com/pre-commit/pre-commit)
![Gmail Badge](https://img.shields.io/badge/Gmail-EA4335?logo=gmail&logoColor=fff&style=for-the-badge)

## How to run

1. [Install the latest version of Python for your system](https://www.python.org/downloads/)
2. [Install the Poetry package manager](https://python-poetry.org/docs/#installation)
3. Clone this repo
4. Grab a MJML API Key from [here](https://mjml.io/api) and put in into your `config.toml`
5. Get credentials for a [Google Cloud Project](https://developers.google.com/workspace/guides/create-project) with the `gmail.send` scope. Save it as `credentials.json`
6. Update your `config.toml` with all of your information
7. Run `poetry install` in the project directory (use `poetry install --with dev` for development)
8. Finally, `poetry run python main.py`!

## Details

- This project only supports the Gmail API. I do not plan to add SMTP support
- I will not be migrating to the new Google Cloud APIs
- Speed, efficiency, user-experience, a complete feature set. Postman-WABL focuses on none of these. Your mail will reach its destination... _eventually_. (Your emails should be fine though!)

## How templating works

The project uses [jinja](https://jinja.palletsprojects.com/en/3.1.x/) and [MJML](https://mjml.io/).

The sub-template must have a subject line present in it as follows `{# Subject: Subject Here #}` (as you can guess, this is how you specify your email's subject). All jinja placeholder variables are populated. Ensure that all jinja code is escaped. If you fail to escape, your template will break.

## Known Bugs

The preview feature does not work at this moment.
