# Daily LinkedIn Auto-Poster (100% free)

Research (RSS) -> Gemini writes the post -> Pillow builds a branded image (AI background optional)
-> Telegram preview -> LinkedIn publish. Runs on GitHub Actions.

## One-time setup
1. Create a PRIVATE GitHub repo and upload all these files.
2. Get a free Gemini API key at https://aistudio.google.com/apikey
3. Telegram: message @BotFather, /newbot, copy the token. Send any message to your bot, then open
   https://api.telegram.org/bot<TOKEN>/getUpdates and copy chat.id.
4. LinkedIn app: https://www.linkedin.com/developers/apps -> Create app (needs a LinkedIn Company Page to link).
   Products tab: add "Share on LinkedIn" and "Sign In with LinkedIn using OpenID Connect".
   Auth tab: add redirect URL http://localhost:8080/callback
5. On your computer: pip install requests, set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET, run
   python linkedin_auth.py. Copy the token and person ID it prints.
6. Repo -> Settings -> Secrets and variables -> Actions -> add secrets:
   GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_ID
7. Edit data/examples.md (paste your best posts), data/style.md and config.py (name, tagline, feeds).
8. Actions tab -> Daily LinkedIn Post -> Run workflow -> choose "generate" and check Telegram.
   Then try "both" to test the full post.

## Daily behaviour
- 07:00 IST: draft + image sent to Telegram. Reply /skip to cancel.
- 09:00 IST: posts to LinkedIn unless you skipped.
- Set repo variable POST_MODE=auto to post straight away without review.

## Maintenance
- LinkedIn tokens last about 60 days. Re-run linkedin_auth.py and update the secret. You get a Telegram alert on failure.
- If Gemini rejects the model name, set repo variable GEMINI_MODEL to a current free-tier model.
- If the AI background fails, the image falls back to a gradient automatically.
