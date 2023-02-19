base_url = "https://ieeexplore.ieee.org/"
issues_url = f"{base_url}rest/publication/9739/regular-issues"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Accept": "application/json;q=0.9,*/*;q=0.8",
    'cache-http-response': 'false',
    # "https://ieeexplore.ieee.org/xpl/issues?punumber=9739&isnumber=9956928",
    "Referer": issues_url,
    "Content-Type": "application/json"
}
