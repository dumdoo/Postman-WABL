import logging
import os
import os.path
from pathlib import Path
from time import strftime

import rich
import rich.align
import rich.table
from rich import print
from rich.logging import RichHandler
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn, TimeElapsedColumn
from rich.prompt import Confirm

from .get_filled_template import preview_template

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
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[
        RichHandler(
            markup=True,
            rich_tracebacks=True,
        ),
        logging.FileHandler(f"./logs/log-{n}.log"),
    ],
)
logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)
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


def on_email_sent(email: str):
    progress.advance(email_send_task)
    log.info(f"[green][{strftime('%H:%M:%S')}]\t[blue]Sent to [red]{email}")
    if progress.finished:
        progress.refresh()
        log.info("[green]Done!")


def initial_logging(
    template_name: str,
    base_template_name: str,
    data: list[dict[str, str]],
    email_file: str,
):
    log.info(f"Using template '{template_name}' with base '{base_template_name}'")
    log.info(f"{len(data)} rows found in {email_file} (count does not include header)")

    if len(data) <= 7:
        data_w_row_n = [
            (str(i + 1), *person_data.values()) for i, person_data in enumerate(data)
        ]
    else:
        data_w_row_n = []

        for i, person_data in enumerate(data[:3]):  # add first 3
            data_w_row_n.append((str(i + 1), *person_data.values()))

        data_w_row_n.append(("...", "...", "..."))  # add gap

        for i, person_data in enumerate(data[-3:]):  # add last 3
            row_number = str((i + 1 + len(data)) - 3)
            data_w_row_n.append((row_number, *person_data.values()))
    data_w_row_n: list[tuple[str, str, str]]

    preview_table = rich.table.Table(
        "n",
        *data[0].keys(),
        title=f"Preview of {email_file}",
        box=rich.box.MINIMAL,
        # expand=True,
        highlight=True,
        title_style="bold red",
        style="cornsilk1",
        header_style="bold chartreuse1",
        row_styles=["pale_turquoise1", "purple"],
    )
    for d in data_w_row_n:
        preview_table.add_row(*d)
    print("\n")
    print(rich.align.Align(preview_table, align="center"))


def ask_for_start():
    if not Confirm.ask("Proceed?"):
        raise SystemExit


def show_template():
    if Confirm.ask("Show template?"):
        try:
            preview_template()
        except AttributeError as e:
            log.warning(e, exc_info=True)
