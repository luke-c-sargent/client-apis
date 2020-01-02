import pytest


def pytest_addoption(parser):
    """Adds command line options."""
    parser.addoption(
        "--terra_auth_url", action="store", default="https://broad-bond-dev.appspot.com/api/link/v1/fence/accesstoken/", help="Full url for terra fence/accesstoken endpoint"
    )
    parser.addoption(
        "--user_email", action="store", default=None, help="gmail account registered with terra (None will use default)"
    )
    parser.addoption(
        "--gen3_endpoint", action="store", default="https://staging.theanvil.io", help="gen3 endpoint"
    )


@pytest.fixture
def terra_auth_url(request):
    """Returns command line options as fixture."""
    return request.config.getoption("--terra_auth_url")


@pytest.fixture
def user_email(request):
    """Returns command line options as fixture."""
    return request.config.getoption("--user_email")


@pytest.fixture
def gen3_endpoint(request):
    """Returns command line options as fixture."""
    return request.config.getoption("--gen3_endpoint")
