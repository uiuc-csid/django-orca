# django-orca

[![Test Project](https://github.com/uiuc-csid/django-orca/actions/workflows/test.yaml/badge.svg)](https://github.com/uiuc-csid/django-orca/actions/workflows/test.yaml)[![codecov](https://codecov.io/gh/uiuc-csid/django-orca/branch/main/graph/badge.svg?token=VJ3CMWEV4P)](https://codecov.io/gh/uiuc-csid/django-orca)

A role-based access control backend for django based on [django-improved-permissions](https://github.com/s-sys/django-improved-permissions) which is no longer maintained

## To Do

### Bugs

- [ ] Enable `ALL_MODELS` mode. Roles with `all_models = True` can be assigned but grant nothing, `get_objects()` crashes for users who have one, and `UserRole.natural_key()` fails for them.
- [ ] Use one source of truth for permissions. `has_perm` reads the role classes and follows inheritance, but `get_user_permissions`/`get_all_permissions` read `RolePermission` rows saved at assignment time and ignore inheritance, so the two disagree.
- [ ] `get_user_permissions`/`get_all_permissions` return `Permission` objects, but Django expects `"app_label.codename"` strings, so they mix badly with other backends.
- [ ] Only attach the `post_delete` cleanup handler to models used by roles. Attaching it to every model disables fast deletes across the whole project, and it deletes roles one query at a time.

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
- [ ] Remove the leftover `del self.get_roles_for_perm` in `OrcaRegistry.register()`, and sort rows before grouping them in `get_objects()`.

### Tooling

- [ ] Run ruff and mypy in CI, and fix the existing mypy errors.
- [ ] Test against a matrix of Python 3.10–3.14 and Django 4.2, 5.2 and 6.x.
- [ ] Require Django 4.2 or later, and add classifiers and project URLs.
- [ ] Remove ruff's `target-version`, so it follows `requires-python`.
- [ ] Update the GitHub Actions to their current major versions (`checkout` and `codecov-action` are on v3).
- [ ] Add a `py.typed` marker.
- [ ] Remove or fix the `demo` task in `mise.toml`, which runs `tests.demo`.

### Done

- [x] Support large and non-integer primary keys
- [x] Fix `IntegrityError` when re-saving a `UserRole`
- [x] Replace pre-commit and black with hk
- [x] Add separate cache so that role cache invalidation does not clear everything

## Questions

- [ ] Should you be able to tie a role to a group?
