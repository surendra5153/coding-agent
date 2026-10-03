import urllib.request
 
print("Trying to reach the internet...")
urllib.request.urlopen("http://example.com", timeout=5)
print("CONNECTED - this should never print!")