# Xray on Platform.sh

## Deploy

```bash
# Create a Platform.sh project, then:
git init
git add .
git commit -m "init"
git remote add platform <your-platformsh-git-remote>
git push platform main
```

## Configure client

Set client's `address` and TLS `serverName` to your Platform.sh domain, and the xhttp `host` to match.

## Note

TLS is terminated at Platform.sh edge. The server listens on port 8080 (internal) via xhttp without TLS.
