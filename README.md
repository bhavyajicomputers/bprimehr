# B-Prime HR

Frappe/ERPNext v15 custom app for branded offline HR Check In, Check Out, Activity Start, and Activity Stop.

## Correct Frappe App Structure

This structure is required. Do not remove the inner `b_prime_hr/b_prime_hr/__init__.py`.

```text
bprimehr/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
└── b_prime_hr/
    ├── __init__.py
    ├── hooks.py
    ├── patches.txt
    ├── modules.txt
    ├── api.py
    ├── b_prime_hr/
    │   └── __init__.py
    ├── config/
    │   ├── __init__.py
    │   └── desktop.py
    ├── public/
    ├── setup/
    └── www/
```

`modules.txt` must contain:

```text
B Prime HR
```

Frappe scrubs this to `b_prime_hr` and imports `b_prime_hr.b_prime_hr`, so the inner folder is mandatory.

## Install on Frappe Cloud

1. Push these files to GitHub branch `v15`.
2. Confirm on GitHub that `b_prime_hr/b_prime_hr/__init__.py` exists.
3. In Frappe Cloud, remove/re-add or update the app on the bench.
4. Deploy/Update Bench.
5. Install app on the site.
6. Open `/offline-hr`.

## URL

```text
https://your-site.frappe.cloud/offline-hr
```
