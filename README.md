# Employee Offline HR v15 Branded

Frappe/ERPNext v15 custom app for a branded employee self-service mobile/desktop page.

## Features

- Company-branded offline page
- Check In
- Check Out
- Start Activity
- Stop Activity
- Captures latitude, longitude, accuracy, browser timestamp
- Stores events offline in browser localStorage
- Syncs pending logs when internet is available
- Creates Employee Checkin records
- Creates/updates Employee Activity records
- Resolves address/city/state/place_id on server during sync using Google Settings API key
- Works from laptop, desktop, Android Chrome, and as a browser/PWA shortcut

## Important limitation

True address text cannot be reliably generated while fully offline because reverse geocoding requires Google Maps or another online address service. This app captures GPS latitude/longitude offline and stores it immediately. Address is filled automatically when the device reconnects and syncs.

## Install on Frappe Cloud

1. Push this repository to GitHub.
2. In Frappe Cloud, add it to your Bench as a Custom App.
3. Install app on your site.
4. Run migrate and clear cache.
5. Open `/offline-hr`.

## Required ERPNext settings

- HR Settings: enable geolocation tracking if available.
- Google Settings: enable and add API key for reverse geocoding.
- Each User must be linked to an Employee record through `Employee.user_id`.

## Fields expected on Employee Activity

The app checks if fields exist before setting them. Recommended fields:

- employee
- activity
- customer_name
- remarks
- started
- stoped
- from_time
- to_time
- latitude
- longitude
- address
- city
- state
- out_latitude
- out_longitude
- out_address
- out_city
- out_state
- time_taken

## Fields recommended on Employee Checkin

- latitude
- longitude
- address
- formatted_address
- city
- state
- place_id
- custom_employee_activity
- custom_source
