import os, sys, subprocess, urllib3, re, json

urllib3.disable_warnings()

md5 = os.environ.get("MD5", "32d5c2bf59851a27cf83c647d207b57e")
output = os.environ.get("OUTPUT", "Pipeline_Leak_Detection_Handbook.pdf")
print(f"Target MD5: {md5} -> {output}")

import requests
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
r = requests.get(f"https://libgen.li/get.php?md5={md5}", headers=headers, timeout=30, verify=False)
matches = re.findall(r'get\.php\?md5=' + md5 + r'&key=([A-Z0-9]+)', r.text)
if matches:
    key = matches[0]
    url = f"https://libgen.li/get.php?md5={md5}&key={key}"
    cmd = f'curl -skL --connect-timeout 30 --max-time 300 -o "{output}" "{url}"'
    subprocess.run(cmd, shell=True, timeout=310)
    
    if os.path.exists(output) and os.path.getsize(output) > 100000:
        with open(output, 'rb') as f:
            if f.read(4) == b'%PDF':
                size = os.path.getsize(output)
                print(f"SUCCESS! PDF: {size} bytes")
                print(f"OUTPUT_FILE={output}")
                print(f"OUTPUT_PATH={os.path.abspath(output)}")
                sys.exit(0)

print("FAILED")
sys.exit(1)
