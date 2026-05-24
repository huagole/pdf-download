import os, sys, subprocess, urllib3, re, json

urllib3.disable_warnings()

md5 = os.environ.get("MD5", "32d5c2bf59851a27cf83c647d207b57e")
output = os.environ.get("OUTPUT", "Pipeline_Leak_Detection_Handbook.pdf")
print(f"Target MD5: {md5} -> {output}")

# Get key from libgen.li
import requests
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
r = requests.get(f"https://libgen.li/get.php?md5={md5}", headers=headers, timeout=30, verify=False)
matches = re.findall(r'get\.php\?md5=' + md5 + r'&key=([A-Z0-9]+)', r.text)
print(f"Page size: {len(r.content)}, key matches: {len(matches)}")
if matches:
    key = matches[0]
    url = f"https://libgen.li/get.php?md5={md5}&key={key}"
    print(f"Key: {key}, URL: {url[:80]}")
    
    # Use curl to download - more reliable for large files with chunked encoding
    cmd = f'curl -skL --connect-timeout 30 --max-time 300 -o "{output}" "{url}"'
    print(f"Running: curl download...")
    result = subprocess.run(cmd, shell=True, timeout=310, capture_output=True)
    print(f"Curl exit: {result.returncode}")
    if result.stderr:
        stderr_text = result.stderr.decode('utf-8', errors='replace')[:500]
        print(f"Curl stderr: {stderr_text}")
    
    if os.path.exists(output):
        size = os.path.getsize(output)
        print(f"Downloaded: {size} bytes")
        if size > 100000:
            with open(output, 'rb') as f:
                magic = f.read(4)
            if magic == b'%PDF':
                print(f"SUCCESS! Valid PDF: {size} bytes")
                sys.exit(0)
            else:
                print(f"Not PDF. Magic: {magic}")
                # Check if it's HTML
                with open(output, 'rb') as f:
                    head = f.read(200)
                print(f"Head: {head[:100]}")
        else:
            print(f"File too small, likely error page")
            with open(output, 'r', errors='replace') as f:
                print(f"Content: {f.read()[:500]}")
    else:
        print("Download failed - no output file")
else:
    print("No key found in page")

print("FAILED")
sys.exit(1)
