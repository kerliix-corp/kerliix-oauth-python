from kerliix_oauth import KerliixOAuth

client = KerliixOAuth(
    client_id="your-client-id",
    redirect_uri="https://yourapp.com/callback",
    base_url="https://api.kerliix.com",
    client_secret="your-client-secret"
)

# 1️⃣ Generate Auth URL (PKCE optional)
auth = client.get_auth_url(use_pkce=True)
print("Visit:", auth["url"])

# 2️⃣ Exchange Code
token = client.exchange_code_for_token(code="AUTH_CODE", code_verifier=auth["code_verifier"])

# 3️⃣ Fetch User Info
user = client.get_user_info()
print("User:", user)

# 4️⃣ Revoke Token
client.revoke_token(token.access_token)
