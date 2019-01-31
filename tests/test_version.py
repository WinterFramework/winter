from winter.__version__ import __version__
from semver import parse


def test_version_is_a_valid_semver():
    # Act
    version = parse(__version__)

    # Assert
    assert version['major'] > 0  # In fact we test that parse doesn't fail with ValueError
