# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0/).

---

## Quick Start / Known Issues (Local Development)
- **TypeScript syntax cannot run directly in Node.js** without compiling. Use `tsc` to build before running.
- **Do not use `!` non-null assertions** in runtime code (`CLIENT_ID!`) – they are TypeScript-only and will break Node.js execution.
- Exported functions with TypeScript types (e.g., `code: string`) will throw syntax errors if run uncompiled.
- Always handle runtime errors from SDK methods:
  - `"Missing required config: clientId, redirectUri, or baseUrl"`
  - `"Token exchange failed: <status> <statusText>. Response: <body>"`
  - `"Failed to refresh token"`
  - `"Missing access token"`
  - `"Failed to fetch user info"`
  - `revokeToken()` may return `false` if revocation fails.
- Use compiled `dist/` files for testing locally instead of raw `.ts` files.

---

## [1.0.2] - 2025-10-28

### Added
- **Python OAuth2 client wrapper (`client.py`)** replacing older raw HTTP implementations.
  - Automatically uses the **default OAuth server URL (`https://api.kerliix.com`)** if none is provided.
  - Includes helper methods for standard OAuth 2.0 flows:
    - `get_authorize_url(state: Optional[str] = None)` – generates authorization URLs (supports PKCE for public clients).
    - `exchange_code_for_tokens(code: str)` – exchanges authorization code for access and refresh tokens.
    - `fetch_user_info(access_token: Optional[str] = None)` – fetches the authenticated user profile; auto-refreshes tokens if expired.
    - `refresh_token_if_needed()` – automatically refreshes tokens when they expire.
    - `revoke_token(token: str)` – revokes an access or refresh token.
  - **New `check_authorization_url()` method** to pre-validate client ID and redirect URI.
    - Sends a `HEAD` request to the OAuth server to confirm configuration before starting authorization.
    - Raises descriptive exceptions on validation failure and logs successful checks.

- **Client authentication middleware (`middlewares/client_auth.py`)** for validating Basic Auth credentials (`client_id` / `client_secret`).
  - Attaches the verified client to `request.oauth2.client` and `request.user`.
  - Returns clear errors for missing credentials, invalid clients, or mismatched secrets.
  - Includes structured logging for all authentication events.

- **Enhanced PKCE (Proof Key for Code Exchange) support**:
  - Securely generates and encodes the `code_verifier` and `code_challenge` (base64url-encoded SHA-256).

- **Improved developer diagnostics and logging**:
  - Logs include `error.message`, HTTP status code, reason, and response body (when available).
  - Consistent logging across all client methods for easier debugging.

### Changed
- Migration from ad-hoc HTTP client usage to **Pythonic OAuth client class** for initialization and flow management.
- Client initialization now defaults to `https://api.kerliix.com`; `base_url` is optional.
- Unified error handling across all OAuth operations.
- Internal request logic fully aligned with OAuth 2.0 Authorization Code Flow.
- Token caching and refresh mechanisms updated for better standards compliance.
- More readable error propagation (`str(error)` or `error.message`).
  - Updated in:
    - `exchange_code_for_tokens()`
    - `refresh_token_if_needed()`
    - `fetch_user_info()`
    - `revoke_token()`
- Documentation and code examples updated to show `check_authorization_url()` usage.

### Fixed
- Fixed PKCE challenge encoding to ensure correct base64url format.
- Adjusted log outputs for consistent formatting and clarity during debugging.

---

## [1.0.1] - 2025-10-27
### Added
- **Runtime error documentation** for the SDK:
  - `"Missing required config: clientId, redirectUri, or baseUrl"` in `KerliixOAuth` constructor.
  - `"Token exchange failed: <statusText>"` in `exchangeCodeForToken()`.
  - `"Failed to refresh token"` in `refreshTokenIfNeeded()`.
  - `null` returned from `refreshTokenIfNeeded()` or `TokenCache.get()` if no valid token exists.
  - `"Missing access token"` in `getUserInfo()` if no access token is available.
  - `"Failed to fetch user info"` if user info request fails.
  - `revokeToken()` returns `false` if token revocation fails.
- Enhanced **developer experience** with clearer SDK error messages and handling instructions.
- Minor improvements to TypeScript typings and internal caching logic.

### Changed
- SDK version bumped from `1.0.0-beta.1` to `1.0.1`.
- Documentation and examples updated to highlight error handling.

### Fixed
- N/A (no functional changes; only runtime errors clarified).

---

## [1.0.0-beta.1] - 2025-10-15
### Added
- **Initial beta release** of the official **Kerliix OAuth SDK** for Node.js and browser.
- Support for **OAuth 2.0 Authorization Code Flow**.
- `KerliixOAuth` main client class for authentication and token management.
- `getAuthUrl()` method to generate authorization URLs.
- `exchangeCodeForToken()` to exchange authorization codes for tokens.
- `refreshTokenIfNeeded()` to refresh tokens automatically.
- `getUserInfo()` to fetch authenticated user profile information.
- `revokeToken()` to revoke issued tokens.
- In-memory **token caching** with early refresh via `TokenCache`.
- TypeScript support with full type definitions (`types.ts`).

### Fixed
- N/A (initial release).

### Changed
- N/A (initial release).

---

## [Unreleased]
### Planned
- Add PKCE (Proof Key for Code Exchange) support for better security.
- Persistent caching options (file system or Redis).
- Improved browser compatibility and npm publishing.
- Unit tests and CI/CD integration.

---

**Repository:** [kerliix-corp/kerliix-oauth-nodejs](https://github.com/kerliix-corp/kerliix-oauth-nodejs)  
**License:** MIT © Kerliix Corporation
