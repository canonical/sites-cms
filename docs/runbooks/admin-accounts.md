# Admin accounts in a deployment

How to get the first admin account, and how passwords are changed, when
the CMS runs from the charm. This applies until company sign-in is
switched on.

## There is no default admin

The charm creates no user. The local `admin` / `admin` account exists only
on a developer's machine: `create_local_admin` refuses to run when debug is
off, so it cannot be used in staging or production.

## Create an admin

```bash
juju run sites-cms/0 create-superuser username=<name> email=<email>
```

The action returns a random password in its output (`password: ...`). You
cannot choose it. Give it to the person over a private channel and ask them
to change it after their first sign-in.

The action fails if the username or the email address is already used.
Every account needs its own email address.

## Change a password

The charm has no action for this. It is done in the Wagtail admin:

- **Your own password:** Account, then the Password section.
- **Someone else's password (admins only):** Settings, then Users, then
  the user.

"Forgot password" on the sign-in page does not work yet. The charm has no
SMTP integration, so the app has no mail server and the reset email is
logged and dropped. Until one is added, an admin resets the password under
Settings, then Users.

## Every admin is locked out

1. Run `create-superuser` with a new username and email address.
2. Sign in with the password it returns.
3. Reset the locked-out accounts under Settings, then Users.
4. Delete or deactivate the extra account when you are done.

## Not the same as rotating the secret key

`juju run sites-cms/0 rotate-secret-key` signs everyone out. It does not
change any password. Use it if a session may have been stolen.
