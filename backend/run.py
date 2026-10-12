"""
Windows üzerinde psycopg async uyumluluğu için SelectorEventLoop kullanarak
uvicorn'u başlatır. Direkt `uvicorn app.main:app` yerine bu dosyayı kullanın.
"""
import asyncio
import selectors
import uvicorn

# Windows default'u ProactorEventLoop'tur ama psycopg SelectorEventLoop ister
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
loop = asyncio.SelectorEventLoop(selectors.SelectSelector())
asyncio.set_event_loop(loop)

if __name__ == "__main__":
    config = uvicorn.Config(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        loop="none",        # kendi event loop'umuzu kullanıyoruz
    )
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())
