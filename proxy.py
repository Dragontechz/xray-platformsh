import os, asyncio, ssl
from aiohttp import web, ClientSession, ClientTimeout

TARGET_HOST = os.environ.get("TARGET_HOST", "konoyves.shop")
TARGET_PORT = int(os.environ.get("TARGET_PORT", "443"))

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

async def proxy_handler(request):
    url = f"https://{TARGET_HOST}:{TARGET_PORT}{request.path_qs}"
    headers = dict(request.headers)
    body = await request.read() if request.can_read_body else None
    timeout = ClientTimeout(total=60)
    async with ClientSession(timeout=timeout) as session:
        try:
            async with session.request(
                method=request.method,
                url=url,
                headers=headers,
                data=body,
                ssl=ssl_ctx,
                allow_redirects=False
            ) as resp:
                resp_headers = dict(resp.headers)
                for h in ["content-encoding", "transfer-encoding", "content-length"]:
                    resp_headers.pop(h, None)
                resp_body = await resp.read()
                return web.Response(body=resp_body, status=resp.status, headers=resp_headers)
        except Exception as e:
            return web.Response(text=f"Proxy error: {e}", status=502)

app = web.Application()
app.router.add_route("*", "/{path:.*}", proxy_handler)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
