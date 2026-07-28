# Upsun TCP Proxy

A minimal TCP proxy deployed on Upsun that forwards incoming traffic to any server.

## How it works

```
Browser                     Upsun Router                    Container (port 8080)              Your Server
   │                             │                               │                                │
   ├─ HTTPS ────────────────────►│                               │                                │
   │                             ├── HTTP (plain) ─────────────►│                                │
   │                             │  (TLS terminated at edge)    │                                │
   │                             │                               ├── TCP ───────────────────────►│
   │                             │                               │   your-server.com:8080       │
   │                             │                               │◄── TCP ───────────────────────┤
   │◄─ HTTPS ────────────────────┤                               │                                │
```

1. **Client → Upsun Router**: HTTPS connection. Upsun terminates TLS at the edge using auto-provisioned Let's Encrypt certificates.
2. **Router → Container**: Plain HTTP on port 8080. No TLS between router and your app.
3. **Container → Your Server**: Raw TCP connection to your target `host:port`. The proxy does `io.Copy` in both directions — no HTTP parsing, no TLS, no headers. Pure byte forwarding.

## What the proxy does

`proxy.go` is a 59-line Go program that:

- Listens on port 8080 (or `$PORT`)
- Accepts TCP connections
- Opens a TCP connection to `$TARGET_HOST`
- Copies bytes bidirectionally using `io.Copy`
- When one side closes, the other side closes too

That's it. No HTTP awareness, no TLS handshake, no header manipulation. It's a transparent TCP tunnel.

## Files

| File | Purpose |
|---|---|
| `proxy.go` | The TCP proxy |
| `.upsun/app.yaml` | Upsun app configuration |
| `.upsun/routes.yaml` | Upsun routing rules |

## How to configure for your own server

### 1. Set the target

Edit `.upsun/app.yaml` — change `TARGET_HOST` to your server:

```yaml
variables:
  env:
    TARGET_HOST: "your-server.com:8080"
```

For an IP address and different port:

```yaml
variables:
  env:
    TARGET_HOST: "192.168.1.1:443"
```

### 2. Deploy to Upsun

```bash
# Create a project
upsun create \
  --org YOUR_ORG_ID \
  --region fr-3.platform.sh \
  --title my-proxy

# Add the Upsun remote
git remote add upsun PROJECT_ID@git.fr-3.platform.sh:PROJECT_ID.git

# Push
git push upsun main
```

Or if your Upsun project uses `master` as the default branch:

```bash
git push upsun master
```

### 3. Get your URL

```bash
upsun environment:url
```

You'll get a URL like `https://main-xxxxx-PROJECT_ID.fr-3.platformsh.site/`. All traffic to that URL is tunneled to your target.

## Why this approach

- **No TLS to manage**: Upsun handles certificates automatically
- **No HTTP awareness**: Works with any TCP-based protocol (HTTP, HTTPS, SSH, WebSocket, etc.)
- **Minimal resource usage**: Tiny Go binary, ~5MB RAM
- **Free tier**: Upsun's development plan is free
