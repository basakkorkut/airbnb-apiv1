import http from 'k6/http';
import { check, sleep } from 'k6';


const BASE_URL = 'https://airbnb-apiv1-f7a7aedkcyfcbaba.italynorth-01.azurewebsites.net';


export function setup() {
    const loginRes = http.post(`${BASE_URL}/api/v1/auth/login`, 
        'grant_type=password&username=guest%40example.com&password=password123&scope=&client_id=string&client_secret=string',
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    );

    const token = JSON.parse(loginRes.body).access_token;
    return { token: token };
}

// =============================================
// TEST SCENARIOS
// =============================================

export default function (data) {
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${data.token}`,
    };

    // Test 1: Query Listings (GET)
    const queryRes = http.get(
        `${BASE_URL}/api/v1/listings/?date_from=2026-07-01&date_to=2026-07-05&no_of_people=2&country=Turkey&city=Istanbul&page=1&size=10`
    );
    check(queryRes, {
        'Query Listings status 200 or 429': (r) => r.status === 200 || r.status === 429,
    });

    sleep(1);

    // Test 2: Book a Stay (POST)
    const bookingRes = http.post(
        `${BASE_URL}/api/v1/bookings/`,
        JSON.stringify({
            listing_id: 1,
            date_from: `2027-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-01`,
            date_to: `2027-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-05`,
            guest_names: `Test User ${__VU}`,
        }),
        { headers: headers }
    );
    check(bookingRes, {
        'Book a Stay status 201 or 409': (r) => r.status === 201 || r.status === 409,
    });

    sleep(1);
}