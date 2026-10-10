# Contributing

Please discuss substantial changes in an issue first, and follow the [code of conduct](CODE_OF_CONDUCT.md).

## Pull requests

- Every PR must pass the **Required checks** (test matrix + 100% coverage).
- Use [Conventional Commits](https://www.conventionalcommits.org/) for the commits that land on
  `master`. With squash merge that is the PR title; with a merge commit it is every commit in the PR.
  Nothing else is needed for a release: no version bumps, no CHANGELOG edits.

| Commit prefix                                   | Effect on the next release          |
|-------------------------------------------------|-------------------------------------|
| `fix:`, `perf:`                                 | PATCH release                       |
| `feat:`                                         | MINOR release                       |
| `feat!:`, `fix!:` or a `BREAKING CHANGE:` footer | MAJOR release                       |
| `refactor:`, `docs:`, `test:`, `chore:`, `ci:`, `build:`, `style:` | no release; listed in the next changelog |

Examples:

```
fix: handle None in Page serialization
feat(openapi): generate enum for order_by parameter
feat!: drop Django 4.1 support
```

## Releases

Releases are fully automated by [`.github/workflows/release.yml`](.github/workflows/release.yml)
using [python-semantic-release](https://python-semantic-release.readthedocs.io/).
Every push to `master` runs the tests, computes the next version from the commits since the last tag,
commits the bumped `pyproject.toml` and `CHANGELOG.md`, tags `X.Y.Z`, creates a GitHub Release and
publishes to PyPI. If nothing is releasable, the workflow stops.

To release manually (for example a patch after refactoring-only merges), run the **Release** workflow
from the Actions tab and choose the bump. **Dry run** only prints the version that would be released.
