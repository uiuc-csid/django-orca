# Changelog

All notable changes to django-orca. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [semantic versioning](https://semver.org/) (before 1.0, a minor version can include breaking changes).

## Unreleased

### Upgrading from 0.1.0

- **Run `manage.py migrate`.** Migration `0003` changes `UserRole.object_id` from an integer to text. Existing values are kept.
- **`UserRole.object_id` is now a string**, such as `"5"` instead of `5`. Code that reads it and compares it with an integer needs to convert it. Filtering with an integer, such as `UserRole.objects.filter(object_id=5)`, still works.

### Changed

- The cleanup handler that removes roles when their object is deleted is only connected to models listed in roles and their subclasses, instead of every model in the project. Other models can be deleted in bulk again, which Django can't do for models with a `post_delete` receiver. It also removes an object's roles in one query instead of one per role.
- Querysets are built with each model's default manager instead of `objects`, so models whose manager has another name work.
- A `permission_parents` entry that isn't a relation to another model raises `ImproperlyConfigured` with the field name.
- Development only: mypy passes with no errors and runs in the hk checks, and the test factories are typed.
- Development only: git hooks and linting run through hk (`mise run lint`, `mise run fix`) instead of pre-commit, and code is formatted with ruff instead of black. Markdown is linted with markdownlint-cli2.

### Removed

- Unused helpers in `django_orca.utils`: `get_from_cache`, `delete_from_cache`, `generate_cache_key`, `get_parents` and `inherit_check`. Nothing in django-orca called them, and permission inheritance is handled by the role registry. Code that imported them directly will need to stop.

### Fixed

- Roles work with objects whose primary key isn't a 32-bit integer, including `BigAutoField` values above 2,147,483,647, UUIDs and text keys. Models whose primary key isn't named `id` also have their roles removed when they're deleted, and custom user models with a differently named primary key work with `UserRole` natural keys.
- `UserRole.natural_key()` no longer fails for roles that aren't attached to an object.
- Saving an existing `UserRole` again no longer fails with `IntegrityError`. Its permissions are only created when the role is first saved. `UserRole.save()` also passes its arguments, such as `update_fields` and `using`, on to Django.

## 0.1.0 - 2026-09-25

### Changed

- **Python 3.10 or later is required.** Python 3.9 is no longer supported.
- Clearing orca's cache no longer clears the whole Django cache. Orca keys now carry a generation number, and clearing bumps it so only orca's entries are retired. Other data in the same cache is kept. This happens each time the role registry is created, which is on every process start.
- Orca cache entries always expire, after 300 seconds by default. Set `ORCA_SETTINGS["CACHE_TIMEOUT"]` to change it. Previously they used the cache's default timeout, which could be never.
- The built package includes the `LICENSE` file.
- Development only: the project uses uv instead of Poetry, and builds with `uv_build`. `django-heavy-water` comes from PyPI instead of GitHub.
- Development only: the example project and tests live in `tests/`, and ruff skips migrations.
