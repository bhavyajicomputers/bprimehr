# B-Prime HR

Frappe/ERPNext v15 custom app for branded offline HR Check In, Check Out, Activity Start, and Activity Stop.

## App Name

`b_prime_hr`

## Important Install Fix

This app has no custom DocTypes. Therefore `b_prime_hr/modules.txt` is intentionally blank.

This prevents this Frappe install error:

```text
No module named 'b_prime_hr.b_prime_hr'
```

## Correct GitHub Structure

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
    ├── modules.txt        # keep this file blank
    ├── api.py
    ├── public/
    ├── setup/
    └── www/
```

## Install on Frappe Cloud

1. Push these files to GitHub.
2. Frappe Cloud → Bench → Apps → Update/Deploy Bench.
3. Frappe Cloud → Site → Apps → Install App → b_prime_hr.
4. Open `/offline-hr`.

## URL

```text
https://your-site.frappe.cloud/offline-hr
```
