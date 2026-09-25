# django-orca

[![Test Project](https://github.com/uiuc-csid/django-orca/actions/workflows/test.yaml/badge.svg)](https://github.com/uiuc-csid/django-orca/actions/workflows/test.yaml)[![codecov](https://codecov.io/gh/uiuc-csid/django-orca/branch/main/graph/badge.svg?token=VJ3CMWEV4P)](https://codecov.io/gh/uiuc-csid/django-orca)

A role-based access control backend for django based on [django-improved-permissions](https://github.com/s-sys/django-improved-permissions) which is no longer maintained

## To Do

### Design

- [ ] Remove deny mode. `deny`, `inherit_deny` and the `inherit` flag are validated but ignored by `has_perm`.
- [ ] Create local role permissions cache like django does. The existing cache is only used by `string_to_permission`, which nothing calls.
- [ ] Clean up unused shortcuts etc...
- [ ] Standardize queryset fetching methods
- [ ] Enable `ANY_OBJECT` mode
- [ ] Prefix role name in database with the app name, so roles with the same class name in different apps don't collide
- [ ] Redirect anonymous users to the login page in the view mixins (call `handle_no_permission()`), and share `get_permission_object` between them.
- [ ] Stop registering Django's `Permission` model in the admin.
- [ ] Accept model classes in `Role.models`, and raise `ImproperlyConfigured` for unknown model names.

### Done

- [x] Run ruff and mypy in CI
- [x] Test against Python 3.10–3.14 and Django 4.2, 5.2 and 6.1
- [x] Require Django 4.2 or later, and add classifiers and project URLs
- [x] Update the GitHub Actions
- [x] Remove ruff's `target-version`
- [x] Remove the broken `demo` task from `mise.toml`
- [x] Add a `py.typed` marker
- [x] Enable `ALL_MODELS` mode
- [x] Sort rows before grouping them in `get_objects()`
- [x] Remove the unused `RolePermission` rows
- [x] Make `get_user_permissions`/`get_all_permissions` agree with `has_perm` and return strings
- [x] Only attach the `post_delete` cleanup handler to models used by roles
- [x] Fix the mypy errors
- [x] Support large and non-integer primary keys
- [x] Fix `IntegrityError` when re-saving a `UserRole`
- [x] Replace pre-commit and black with hk
- [x] Add separate cache so that role cache invalidation does not clear everything

## Questions

- [ ] Should you be able to tie a role to a group?
