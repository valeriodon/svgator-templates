# Working with the SVGator MCP

Every template in this repo was created, and every second brand was made, through the [SVGator](https://www.svgator.com) MCP server (`https://mcp.svgator.com/mcp`). The scripts call it through a small client in `.mcp/`.

## The client

- `.mcp/mcp.py`: a standard-library Python client for the server's Streamable HTTP transport. It opens an MCP session, caches the session id for 30 minutes, refreshes the OAuth access token on a 401, opens a new session when the server reports an unknown or expired one, and retries 502/503/504 and dropped connections with exponential backoff.
  - `mcp.py tools` lists the tools.
  - `mcp.py call TOOL '{"arg": 1}'` (or `@args.json`) calls one.
- `.mcp/svg.py`: `call(name, args)` for Python scripts, plus `export_svg(project_id)`.

Tools the scripts use: `create_project`, `replace_project`, `duplicate_project`, `get_skeleton`, `edit_part`, `get_project`, `export_project`.

## Credentials

The client reads two files next to it. Both are in `.gitignore` and must never be committed:

| File | Content | Example |
| --- | --- | --- |
| `.mcp/client.json` | the OAuth client registered with the server (`client_id` is the field the client reads) | `.mcp/client.example.json` |
| `.mcp/token.json` | `access_token` and `refresh_token`; rewritten (mode 600) on every refresh | `.mcp/token.example.json` |

`.mcp/session.txt` (the cached session id) and `.mcp/pkce.json` (a leftover of the manual login) are ignored too.

There is no login script in this repo: I did the first OAuth login by hand. The server publishes its OAuth metadata at `https://mcp.svgator.com/.well-known/oauth-authorization-server`; at the time of writing it lists dynamic client registration and PKCE (S256) with public clients. The steps, not re-tested for this public version:

1. Register a client: `POST https://mcp.svgator.com/register` with a JSON body like `client.example.json` minus `client_id` (redirect URI `http://127.0.0.1:53682/callback`, `token_endpoint_auth_method: "none"`). Save the response as `.mcp/client.json`.
2. Authorize in a browser: `https://mcp.svgator.com/authorize?response_type=code&client_id=…&redirect_uri=…&code_challenge=…&code_challenge_method=S256&state=…&resource=https://mcp.svgator.com/mcp`, sign in to SVGator, and copy the `code` from the redirect.
3. Exchange it: `POST https://mcp.svgator.com/token` with `grant_type=authorization_code`, `code`, `redirect_uri`, `client_id`, `code_verifier` and `resource=https://mcp.svgator.com/mcp`. Save the JSON response as `.mcp/token.json`.
4. Check: `python3 .mcp/mcp.py tools`.

From then on the client refreshes the token by itself. Tokens can be revoked at `https://mcp.svgator.com/revoke`.

## The SVGator document model, as used by the generators

- Every element has a stable `id` and a readable `title`. The title is what the layers panel shows and what the rebrand scripts look up through `get_skeleton`, so titles are the template's API.
- Transforms are `origin`, `translate`, `scale`, `skew`, `rotate`. The generators put the pivot in `origin` and set `translate` to minus the pivot, so an element sits where it was drawn and scales or rotates around its own centre (`group()` and `tf()` in `gen.py`). Movement is animated on `origin`.
- Text is one `text` element per line with the baseline at the origin; fonts are referenced by their Google Fonts family name. Line height is fixed at 1 x font size, which is why every multi-line block is split into lines.
- Images are `shape.href` (a data URI here) with an `aspectRatio` fit.
- Easing is a cubic Bézier per keyframe; control points with y above 1 give an overshoot. `steps` gives a hard cut.
- Layers can be `locked`, which keeps template users away from the mechanics.
- Anything outside the artboard is visible in the editor but never exported, which is where each template keeps its "how to make it yours" note.

## Gotchas found while building

- `create_project` rejects a `clipPath` without `properties.transform` ("Export failed / invalid_project"); an identity transform fixes it.
- An element with `hidden: true` makes the project fail the same way.
- Text line height is fixed at 1 x font size (see above).
