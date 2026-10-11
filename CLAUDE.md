# Winter

- Tests: `poetry run pytest --cov --cov-config=.coveragerc`. CI requires 100% coverage. Redis tests need Docker.
- No `poetry.lock` on purpose.
- Commits on `master` follow Conventional Commits (squash merge: the PR title). See CONTRIBUTING.md.
- Releases are automated (`.github/workflows/release.yml`). Never edit `version` in `pyproject.toml`
  or the generated part of `CHANGELOG.md` by hand.
- Architecture: `docs/architecture.md`. `winter` is a PEP 420 namespace package: never add `winter/__init__.py`.
  Old import paths are aliases in `winter/_deprecation.py` until 34.0; `tools/migrate_to_33.py` rewrites consumers. `poetry run lint-imports` enforces
  the layer rules; `ignore_imports` in `pyproject.toml` is the known debt, never add to it.
- Long-term direction: split core from HTTP adapters, move off Django to ASGI. Not a side task.
- Pushing workflow files needs the `workflow` scope on the `gh` token (`gh auth refresh -s workflow`).
