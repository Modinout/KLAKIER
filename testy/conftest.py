import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope='session', autouse=True)
def usun_reklamy_testowe():
    # The tests run against the live stack, so their ads would stay in the analysts' queue.
    yield
    subprocess.run(
        ['docker', 'compose', 'exec', '-T', 'baza', 'psql', '-U', 'klakier', '-d', 'klakier',
         '-c', "DELETE FROM reklamy WHERE zrodlo = 'test'", '-c', "DELETE FROM strony WHERE domena LIKE '%.example'"],
        cwd=REPO,
        check=True,
    )
