# Changelog

All notable changes to django-orca. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [semantic versioning](https://semver.org/) (before 1.0, a minor version can include breaking changes).

## Unreleased

### Changed

- Development only: git hooks and linting run through hk (`mise run lint`, `mise run fix`) instead of pre-commit, and code is formatted with ruff instead of black. Markdown is linted with markdownlint-cli2.

### Removed

- Unused helpers in `django_orca.utils`: `get_from_cache`, `delete_from_cache`, `generate_cache_key`, `get_parents` and `inherit_check`. Nothing in django-orca called them, and permission inheritance is handled by the role registry. Code that imported them directly will need to stop.

### Fixed

- Saving an existing `UserRole` again no longer fails with `IntegrityError`. Its permissions are only created when the role is first saved. `UserRole.save()` also passes its arguments, such as `update_fields` and `using`, on to Django.

## 0.1.0 - 2026-09-25

### Changed

- **Python 3.10 or later is required.** Python 3.9 is no longer supported.
- Clearing orca's cache no longer clears the whole Django cache. Orca keys now carry a generation number, and clearing bumps it so only orca's entries are retired. Other data in the same cache is kept. This happens each time the role registry is created, which is on every process start.
- Orca cache entries always expire, after 300 seconds by default. Set `ORCA_SETTINGS["CACHE_TIMEOUT"]` to change it. Previously they used the cache's default timeout, which could be never.
- The built package includes the `LICENSE` file.
- Development only: the project uses uv instead of Poetry, and builds with `uv_build`. `django-heavy-water` comes from PyPI instead of GitHub.
- Development only: the example project and tests live in `tests/`, and ruff skips migrations.
