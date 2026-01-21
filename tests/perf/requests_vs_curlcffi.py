import requests
import time
import statistics
from curl_cffi import requests as curl

targets = {
    "Profile": "https://letterboxd.com/nmcassa/",
    "Movie": "https://letterboxd.com/film/the-matrix/",
    "Search": "https://letterboxd.com/s/search/Interstellar/"
}

def run(lib, url, n=3):
    ts = []
    res = "Err"
    for _ in range(n):
        s = time.perf_counter()
        try:
            r = lib.get(url, impersonate="chrome131", timeout=10) if hasattr(lib, "BrowserType") else lib.get(url, timeout=10)
            res = r.status_code
        except Exception:
            res = "Err"
        ts.append(time.perf_counter() - s)
    return statistics.mean(ts), res

print(f"{'Target':<10} | {'Req (s)':<8} | {'Curl (s)':<8} | Status")
print("-" * 45)
for name, url in targets.items():
    tr, sr = run(requests, url)
    tc, sc = run(curl, url)
    print(f"{name:<10} | {tr:<8.3f} | {tc:<8.3f} | R:{sr} C:{sc}")
