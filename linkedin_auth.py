"""Run this on your own computer to get a LinkedIn access token and your person ID.
Usage:
  set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET, then: python linkedin_auth.py
Redirect URL to register in your LinkedIn app: http://localhost:8080/callback
"""
import http.server
import os
import urllib.parse
import webbrowser
import requests

CID = os.environ["LINKEDIN_CLIENT_ID"]
SECRET = os.environ["LINKEDIN_CLIENT_SECRET"]
REDIRECT = "http://localhost:8080/callback"
code_holder = {}


class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code_holder["code"] = (q.get("code") or [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Done. You can close this tab and return to the terminal.")

    def log_message(self, *a):
        pass


url = "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode({
    "response_type": "code", "client_id": CID, "redirect_uri": REDIRECT,
    "scope": "openid profile w_member_social", "state": "zeta"})
print("Opening browser...")
webbrowser.open(url)
http.server.HTTPServer(("localhost", 8080), H).handle_request()
if not code_holder.get("code"):
    raise SystemExit("No code received.")
t = requests.post("https://www.linkedin.com/oauth/v2/accessToken", data={
    "grant_type": "authorization_code", "code": code_holder["code"],
    "redirect_uri": REDIRECT, "client_id": CID, "client_secret": SECRET}).json()
tok = t["access_token"]
me = requests.get("https://api.linkedin.com/v2/userinfo",
                  headers={"Authorization": f"Bearer {tok}"}).json()
print("\nLINKEDIN_ACCESS_TOKEN =", tok)
print("LINKEDIN_PERSON_ID    =", me["sub"])
print("Token valid for about", t.get("expires_in", 0) // 86400, "days. Re-run this before it expires.")
