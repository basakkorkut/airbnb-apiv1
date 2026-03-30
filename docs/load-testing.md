# Load Testing (k6)

This repository includes a k6 script that:

- Logs in as a test guest user to obtain a JWT
- Calls the public listing search endpoint
- Attempts to create bookings with randomized dates

Script: [load_test.js](file:///Users/basakkorkut/Desktop/airbnb-api/load_test.js)

## Prerequisites

- Install k6: https://k6.io/docs/get-started/installation/

## Configure Target

The script currently targets a deployed Azure URL via:

- `BASE_URL` constant in [load_test.js](file:///Users/basakkorkut/Desktop/airbnb-api/load_test.js#L5)

For local testing, replace `BASE_URL` with:

- `http://localhost:8000`

## Run

Example:

```bash
k6 run load_test.js
```

## Notes

- Listing search is rate-limited to 3 requests/day/IP by middleware; the k6 check accepts both `200` and `429` for that endpoint.
- Booking creation may return:
  - `201` when a booking is created
  - `409` when there is a date conflict
