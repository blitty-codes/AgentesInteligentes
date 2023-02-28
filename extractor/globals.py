MAGAZINE_ID = 9739

BASE_URL = "https://ieeexplore.ieee.org/"
ISSUES_URL = f"{BASE_URL}rest/publication/9739/regular-issues"
MAGAZINE_URL = f"{BASE_URL}rest/publication/9739/title-history"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Accept": "application/json;q=0.9,*/*;q=0.8",
    'cache-http-response': 'false',
    # "https://ieeexplore.ieee.org/xpl/issues?punumber=9739&isnumber=9956928",
    "Referer": ISSUES_URL,
    "Content-Type": "application/json"
}
