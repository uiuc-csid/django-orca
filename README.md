# django-orca

[![Test Project](https://github.com/uiuc-csid/django-orca/actions/workflows/test.yaml/badge.svg)](https://github.com/uiuc-csid/django-orca/actions/workflows/test.yaml)[![codecov](https://codecov.io/gh/uiuc-csid/django-orca/branch/main/graph/badge.svg?token=VJ3CMWEV4P)](https://codecov.io/gh/uiuc-csid/django-orca)

A role-based access control backend for django based on [django-improved-permissions](https://github.com/s-sys/django-improved-permissions) which is no longer maintained

## To Do

- [ ] Add separate cache so that role cache invalidation does not clear everything
- [ ] Clean up unused shortcuts etc...
- [ ] Standardize queryset fetching methods
- [ ] Remove deny mode
- [ ] Enable `ALL_MODELS` mode
- [ ] Enable `ANY_OBJECT` mode
- [ ] Create local role permissions cache like django does
- [ ] Prefix role name in database with the app name

## Questions

- [ ] Should you be able to tie a role to a group?
