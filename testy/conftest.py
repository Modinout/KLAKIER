import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope='session', autouse=True)
def usun_reklamy_testowe():
    # Testy działają na żywym stosie, więc ich reklamy zostałyby w kolejce analityków.
    yield
    subprocess.run(
        ['docker', 'compose', 'exec', '-T', 'baza', 'psql', '-U', 'klakier', '-d', 'klakier',
         '-c', "DELETE FROM reklamy WHERE zrodlo = 'test'", '-c', "DELETE FROM strony WHERE domena LIKE '%.example'",
         '-c', "DELETE FROM domeny WHERE domena LIKE '%.example'"],
        cwd=REPO,
        check=True,
    )
