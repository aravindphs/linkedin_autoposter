import os
import urllib.parse
import requests

BASE = "https://api.linkedin.com/v2"


def _headers():
    return {
        "Authorization": f"Bearer {os.environ['LINKEDIN_ACCESS_TOKEN']}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }


def _check(r, what):
    if r.status_code == 401:
        raise RuntimeError("LinkedIn token expired or invalid. Re-run linkedin_auth.py and update the secret.")
    if r.status_code >= 300:
        raise RuntimeError(f"LinkedIn {what} failed: {r.status_code} {r.text[:300]}")


def upload_image(path):
    owner = f"urn:li:person:{os.environ['LINKEDIN_PERSON_ID']}"
    body = {"registerUploadRequest": {
        "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
        "owner": owner,
        "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}],
    }}
    r = requests.post(f"{BASE}/assets?action=registerUpload", headers=_headers(), json=body, timeout=60)
    _check(r, "image register")
    v = r.json()["value"]
    upload_url = v["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    with open(path, "rb") as f:
        up = requests.put(upload_url, data=f.read(),
                          headers={"Authorization": f"Bearer {os.environ['LINKEDIN_ACCESS_TOKEN']}"}, timeout=120)
    _check(up, "image upload")
    return v["asset"]


def publish(text, image_path, title, alt):
    owner = f"urn:li:person:{os.environ['LINKEDIN_PERSON_ID']}"
    asset = upload_image(image_path)
    body = {
        "author": owner,
        "lifecycleState": "PUBLISHED",
        "specificContent": {"com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": text},
            "shareMediaCategory": "IMAGE",
            "media": [{"status": "READY", "description": {"text": alt[:200]},
                       "media": asset, "title": {"text": title[:200]}}],
        }},
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    r = requests.post(f"{BASE}/ugcPosts", headers=_headers(), json=body, timeout=60)
    _check(r, "post")
    return r.headers.get("x-restli-id") or r.json().get("id")


def comment(post_urn, text):
    owner = f"urn:li:person:{os.environ['LINKEDIN_PERSON_ID']}"
    url = f"{BASE}/socialActions/{urllib.parse.quote(post_urn, safe='')}/comments"
    r = requests.post(url, headers=_headers(),
                      json={"actor": owner, "message": {"text": text}}, timeout=60)
    _check(r, "comment")
