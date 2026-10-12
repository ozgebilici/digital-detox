import asyncio
from app.database import engine
from sqlalchemy import text

async def test():
    try:
        async with engine.connect() as conn:
            r = await conn.execute(text('SELECT 1'))
            print('DB Connected OK')
    except Exception as e:
        print(f'DB Connection FAILED: {e}')

asyncio.run(test())
