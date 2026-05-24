import requests, re, os, hashlib, sys

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Target book info
md5 = os.environ.get("MD5", "32d5c2bf59851a27cf83c647d207b57e")
title = os.environ.get("TITLE", "Pipeline Leak Detection Handbook")
output = f"{title.replace(' ', '_')}.pdf"
print(f"Target: {title} (MD5: {md5})")

# Try multiple sources
sources = [
    # LibGen download server direct IPs  
    ("libgen.is", f"https://library.lol/main/{md5}"),
    ("libgen.li", f"https://libgen.li/get.php?md5={md5}"),
    ("direct IP 1", f"http://93.174.95.27/main/{md5[:2]}/{md5[2:4]}/{md5}"),
    ("direct IP 2", f"http://194.150.230.19/main/{md5[:2]}/{md5[2:4]}/{md5}"),
    # Google Books
    ("google books YO0OkAEACAAJ", "https://books.google.com/books/download?id=YO0OkAEACAAJ&printsec=frontcover&output=pdf"),
    # Anna's Archive  
    ("annas-archive", f"https://annas-archive.org/md5/{md5}"),
    # Sci-Hub
    ("sci-hub", f"https://sci-hub.se/{md5}"),
]

for name, url in sources:
    try:
        print(f"\n--- Trying {name} ---")
        r = requests.get(url, headers=headers, timeout=30, allow_redirects=True, stream=True)
        print(f"Status: {r.status_code}, Size: {len(r.content)}, CT: {r.headers.get('Content-Type','?')[:40]}")
        
        # Check if PDF
        is_pdf = r.content[:4] == b'%PDF' or 'application/pdf' in r.headers.get('Content-Type','')
        is_html = 'text/html' in r.headers.get('Content-Type','')
        
        if is_pdf:
            with open(output, 'wb') as f:
                f.write(r.content)
            print(f"SUCCESS! Downloaded to {output} ({len(r.content)} bytes)")
            sys.exit(0)
        elif not is_html:
            # Might still be binary (some servers don't set Content-Type)
            if len(r.content) > 100000 and not b'<!DOCTYPE' in r.content[:500]:
                with open(output, 'wb') as f:
                    f.write(r.content)
                print(f"Maybe PDF? Write to {output} ({len(r.content)} bytes)")
                sys.exit(0)
        
        # Extract links from HTML
        if is_html:
            pdf_links = re.findall(r'href="([^"]*\.pdf[^"]*)"', r.text)
            for pl in pdf_links[:3]:
                print(f"PDF link found: {pl[:150]}")
            dl_links = re.findall(r'href="([^"]*download[^"]*md5[^"]*)"', r.text, re.I)
            for dl in dl_links[:3]:
                print(f"DL link: {dl[:150]}")
            # Try alternate download links
            links_contain = re.findall(r'href="([^"]*' + md5[:8] + r'[^"]*)"', r.text)
            for lk in links_contain[:3]:
                print(f"Link with MD5: {lk[:150]}")
                
    except Exception as e:
        print(f"Error with {name}: {e}")

print("\nAll sources exhausted. Trying fallback...")

# Fallback: try libgen on different formats
fallbacks = [
    f"https://libgen.is/book/index.php?md5={md5}",
    f"https://libgen.rocks/get.php?md5={md5}",
    f"http://libgen.gs/get.php?md5={md5}",
    f"https://libgen.li/ads.php?md5={md5}",
]

for url in fallbacks:
    try:
        r = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        if r.content[:4] == b'%PDF':
            with open(output, 'wb') as f:
                f.write(r.content)
            print(f"SUCCESS from fallback {url[:50]} ({len(r.content)} bytes)")
            sys.exit(0)
        # Look for download links
        links = re.findall(r'(?:href|src)="([^"]*(?:md5|MD5)[' + re.escape(md5[:8]) + r'][^"]*)"', r.text)
        print(f"  {url[:50]}: {r.status_code}, {len(r.content)}b, links={len(links)}")
    except Exception as e:
        print(f"  {url[:50]}: Error: {e}")

print("\nFAILED - no source worked")
sys.exit(1)
