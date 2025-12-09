## TrainerCentral MCP Server

MCP tools that wrap the TrainerCentral APIs (courses, chapters, lessons, tests, live workshops).  
Auth now uses OAuth 2.0 so domain / orgId / tokens are injected at runtime instead of being hardcoded.

### Requirements
- Python 3.13+
- `requests`, `python-dotenv`, `fastmcp`

### Local setup
1) Create a Zoho OAuth client for TrainerCentral (choose the correct region accounts host, e.g. `https://accounts.zoho.com` or `https://accounts.zoho.in`).
2) Generate a refresh token (authorization_code flow with `access_type=offline`).
3) Export environment variables (or place them in `.env`):
```
ZOHO_CLIENT_ID=<client-id>
ZOHO_CLIENT_SECRET=<client-secret>
ZOHO_REFRESH_TOKEN=<refresh-token>
TRAINERCENTRAL_DOMAIN=<https://trainercentral.zoho.<region>>
TRAINERCENTRAL_ORG_ID=<your-org-id>
# optional overrides
ZOHO_ACCOUNTS_URL=<accounts host, defaults to https://accounts.zoho.com>
```
4) Run the MCP server:
```
python main.py
```

### ChatGPT Custom Connector (OAuth 2.0, not OIDC)
- Use OAuth 2.0 authorization code flow in the connector UI (not OIDC).
- Authorization URL: `https://accounts.zoho.in/oauth/v2/auth` (switch to the correct region).
- Token URL: `https://accounts.zoho.in/oauth/v2/token` (switch to the correct region).
- Scopes: include the TrainerCentral scopes your tools need (e.g. `TrainerCentral.courseapi.CREATE`, `TrainerCentral.courseapi.READ`, `TrainerCentral.sectionapi.CREATE`, `TrainerCentral.sessionapi.CREATE`, `TrainerCentral.talkapi.READ`, etc.).
- Request offline access so a refresh token is returned.
- Map tokens from the connector into environment variables before launching the MCP process:
  - `ACCESS_TOKEN` (or `ZOHO_ACCESS_TOKEN`)
  - `REFRESH_TOKEN` (or `ZOHO_REFRESH_TOKEN`)
  - `API_DOMAIN` (Zoho returns this in the token response; used if `DOMAIN` is not provided)
  - `TRAINERCENTRAL_DOMAIN`/`DOMAIN` (optional override if you want to pin a domain)
  - `TRAINERCENTRAL_ORG_ID`/`ORG_ID`

The code will pick up these values at startup, cache them in a shared context, and refresh the access token automatically when expired. No hardcoded domain or org values remain.

