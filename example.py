from kerliix_oauth import KerliixOAuth

client = KerliixOAuth(
    client_id="demo-client",
    client_secret="demo-secret",
    redirect_uri="http://localhost:5175/callback",
    base_url="http://localhost:4000"
)

# Step 1: Generate auth URL
print("Login at:", client.get_auth_url())

# Step 2: Exchange code for tokens
# code = input("Enter code from redirect URL: ")
# tokens = client.exchange_code_for_token(code)
# print("Tokens:", tokens)

# Step 3: Fetch user info
# user = client.get_user_info(tokens.access_token)
# print("User:", user)
