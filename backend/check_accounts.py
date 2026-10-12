import asyncio
from app.database import AsyncSessionLocal
from app.models.account import Account
from sqlalchemy.future import select

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Account))
        accounts = result.scalars().all()
        print(f"Total accounts in DB: {len(accounts)}")
        for i, acc in enumerate(accounts):
            print(f"{i+1}: {acc.platform_name} ({acc.platform_domain}) - Category: {acc.platform_category} - Score: {acc.confidence_score}")

if __name__ == "__main__":
    asyncio.run(main())
