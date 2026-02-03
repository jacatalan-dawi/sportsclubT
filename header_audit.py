import requests

# The target URL
# URL = "https://github.com/"
URL = "http://localhost:8000/api/v1/core/addresses"

# The "Must Have" Headers for a Secure Deployment
REQUIRED_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",  # or SAMEORIGIN
    "Strict-Transport-Security": "max-age", # Only works if HTTPS is enabled!
    "Content-Security-Policy": "default-src 'none'", # For APIs, block everything
    "Referrer-Policy": "same-origin",
}

try:
    response = requests.get(URL)
    print(f"Scanning {URL}")
    print(f"Status: {response.status_code}\n")

    score = 0
    max_score = len(REQUIRED_HEADERS)

    for header, expected_value in REQUIRED_HEADERS.items():
        value = response.headers.get(header)

        if value:
            # Check if value roughly matches expectation
            if expected_value in value:
                print(f"Found header {header} with value {value}")
                score += 1
            else:
                print(f"Found header {header} but value differs")
                print(f"\tExpected substring: {expected_value}")
                print(f"\tActual: {value}")
                score += 0.5 # Partial credit
        else:
            print(f"Missing header {header}")

    print(f"\nYour security score: {score}/{max_score}")

except Exception as e:
    print(f"Error connecting: {e}")

