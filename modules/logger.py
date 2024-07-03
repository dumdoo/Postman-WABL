import logging
import os
import os.path
from pathlib import Path
from time import sleep, strftime

import pandas
from rich import print
from rich.logging import RichHandler
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn, TimeElapsedColumn
from rich.prompt import Confirm

if not os.path.isdir("./logs"):
    os.mkdir("./logs")

n = 0
for log in os.listdir("./logs"):
    path = Path(f"./logs/{log}")
    i = int(path.stem.split("-")[1])
    if i > n:
        n = i
n += 1

FORMAT = "%(message)s"
logging.getLogger(__name__).basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[
        RichHandler(markup=False),
        logging.FileHandler(f"./logs/log-{n}.log"),
    ],
)
log = logging.getLogger("rich")


progress = Progress(
    SpinnerColumn(),
    *Progress.get_default_columns(),
    TimeElapsedColumn(),
    MofNCompleteColumn(),
    transient=True,
)
email_send_task = None


def init_email_task(total_emails_to_be_sent: int):
    global email_send_task
    email_send_task = progress.add_task("Sending Emails", total=total_emails_to_be_sent)
    progress.start()


def on_email_sent(name: str, email: str):
    progress.advance(email_send_task)
    log.info(f"[green][{strftime('%H:%M:%S')}]\t[blue]Sent to [i]{name} - [red]{email}")
    if progress.finished:
        sleep(0.1)  # Keep process alive so bar can update to 100%
        log.info("[green]Done!")


def intial_logging(
    template_name: str,
    base_template_name: str,
    email_data: pandas.DataFrame,
    email_file: str,
):
    log.info(f"Using Template '{template_name}' with base '{base_template_name}'")
    log.info(f"{len(email_data)} non-header rows found in {email_file}")
    if len(email_data) <= 7:
        print(email_data)
    else:
        print(email_data.head(3), end="\n...\n")
        print(
            email_data.tail(3).to_string(header=None),
            end="\n\n",
        )


def ask_for_start():
    if not Confirm.ask("Proceed?"):
        raise SystemExit
