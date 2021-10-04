import os
import pytest

from dotenv import load_dotenv


load_dotenv()


def pytest_addoption(parser):
    parser.addoption(
        "--api", action="store_true", default=False, help="run api tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "api: requires DIVINEPRIDE_API_KEY in .env")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--api"):
        # --api given in cli: do not skip api tests
        return
    skip_api = pytest.mark.skip(reason="need --api option to run")
    for item in items:
        if "api" in item.keywords:
            item.add_marker(skip_api)


@pytest.fixture
def fixture():
    """
    Examples of expected input and output to dp2rathena.
    """
    def _fixture(filename):
        current_path = os.path.join(os.getcwd(), os.path.dirname(__file__))
        return os.path.join(os.path.realpath(current_path), 'fixtures', filename)
    return _fixture
