from pkg_resources import get_distribution
from semver import parse


def test_version_is_a_valid_semver():
    # Act
    version = parse(get_distribution('winter').version)

    # Assert
    assert version['major'] > 0  # In fact we test that parse doesn't fail with ValueError
