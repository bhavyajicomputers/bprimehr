# B-Prime HR

Frappe/ERPNext v15 custom app for a branded employee HR page.

## App Name

`b_prime_hr`

## Features

- B-Prime HR branded page
- Check In
- Check Out
- Start Activity
- Stop Activity
- Captures latitude, longitude, accuracy, and browser timestamp
- Stores events offline in browser localStorage
- Syncs pending logs when internet is available
- Creates Employee Checkin records
- Creates and updates Employee Activity records
- Resolves address, city, state, and place_id on server during sync using Google Settings API key
- Works on laptop, desktop, Android Chrome, and as an Android home-screen PWA shortcut

## Important Offline Note

Latitude and longitude can be captured and stored offline. Full address text cannot be generated reliably while offline because reverse geocoding needs Google Maps or another online address service. This app fills address automatically when the device reconnects and syncs.

## Correct GitHub Structure

Your repository root must look like this:

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
    ├── public/
    ├── setup/
    └── www/
```

Do not put these files inside an extra folder.

## Install on Frappe Cloud

1. Push this repository to GitHub.
2. In Frappe Cloud, go to Bench → Apps → Add App → Your GitHub App.
3. Select repository and branch.
4. Add app `b_prime_hr`.
5. Install it on your site.
6. Run migrate and clear cache.
7. Open `/offline-hr`.

## Required ERPNext Setup

- Each ERPNext User must be linked to an Employee through `Employee.user_id`.
- Google Settings should be enabled with API key for reverse geocoding.
- Employee role should have create permission for Employee Checkin and Employee Activity.
- Employee Activity should have your start/stop fields such as `started`, `stoped`, `from_time`, `to_time`, `latitude`, `longitude`, `address`, `out_address`.

## URL

```text
https://your-site.frappe.cloud/offline-hr
```
