import requests, re, os, sys, time

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
md5 = os.environ.get("MD5", "32d5c2bf59851a27cf83c647d207b57e")
output = os.environ.get("OUTPUT", "Pipeline_Leak_Detection_Handbook.pdf")
print(f"Target MD5: {md5} -> {output}")

import urllib3
urllib3.disable_warnings()

def try_url(url, desc):
    try:
        r = requests.get(url, headers=headers, timeout=30, verify=False, allow_redirects=True)
        print(f"{desc}: {r.status_code}, {len(r.content)}b")
        if r.content[:4] == b'%PDF':
            with open(output, 'wb') as f:
                f.write(r.content)
            print(f"SUCCESS! {len(r.content)} bytes")
            return True
        dl = re.findall(r'href="([^"]*md5=' + md5 + r'[^"]*)"', r.text)
        for d in dl[:3]: print(f"  Link: {d[:120]}")
    except Exception as e:
        print(f"{desc}: {e}")
    return False

# Strategy 1
print("=== S1: libgen.li get page ===")
r = requests.get(f"https://libgen.li/get.php?md5={md5}", headers=headers, timeout=30, verify=False)
matches = re.findall(r'get\.php\?md5=' + md5 + r'&key=([A-Z0-9]+)', r.text)
for m in re.findall(r'href="([^"]*)"', r.text):
    if 'key=' in m or md5[:8] in m:
        print(f"  Found: {m[:120]}")
if matches:
    print(f"Key: {matches[0]}")
    r2 = requests.get(f"https://libgen.li/get.php?md5={md5}&key={matches[0]}", headers=headers, timeout=60, verify=False)
    if r2.content[:4] == b'%PDF':
        with open(output, 'wb') as f: f.write(r2.content)
        print(f"SUCCESS! {len(r2.content)} bytes")
        sys.exit(0)

# Strategy 2: mirrors
for url in [
    f"https://libgen.rocks/get.php?md5={md5}",
    f"https://library.lol/main/{md5}",
    f"https://libgen.is/main/{md5}",
]:
    if try_url(url, url[:50]): sys.exit(0)

# Strategy 3: direct HTTP IPs
for ip in ["93.174.95.27", "185.39.10.101", "194.150.230.19", "195.91.220.248"]:
    url = f"http://{ip}/main/{md5[:2]}/{md5[2:4]}/{md5}"
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.content[:4] == b'%PDF':
            with open(output, 'wb') as f: f.write(r.content)
            print(f"SUCCESS from {ip}: {len(r.content)} bytes")
            sys.exit(0)
        print(f"HTTP {ip}: {r.status_code}, {len(r.content)}b")
    except Exception as e:
        print(f"HTTP {ip}: {type(e).__name__}: {str(e)[:60]}")

# Strategy 4: curl
import subprocess
for url in [
    f"https://libgen.li/get.php?md5={md5}",
    f"https://library.lol/main/{md5}",
]:
    fname = f"/tmp/out{hash(url)}.pdf"
    subprocess.run(f'curl -skL --connect-timeout 10 --max-time 60 -o {fname} "{url}"', shell=True, timeout=70)
    if os.path.exists(fname) and os.path.getsize(fname) > 0:
        with open(fname, 'rb') as f:
            if f.read(4) == b'%PDF':
                os.rename(fname, output)
                print(f"SUCCESS via curl: {os.path.getsize(output)} bytes")
                sys.exit(0)
            print(f"curl {url[:50]}: {os.path.getsize(fname)}b (not PDF)")

print("FAILED")
sys.exit(1)
