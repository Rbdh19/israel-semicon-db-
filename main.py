import os
import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_url = os.environ.get("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://").strip().rstrip("'")
    app.state.pool = await asyncpg.create_pool(db_url, min_size=1, max_size=5)
    yield
    await app.state.pool.close()

app = FastAPI(title="Israel Semicon PE DB", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
async def health(request: __import__("starlette").requests.Request):
    async with request.app.state.pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM companies")
    return {"status": "ok", "company_count": count}

@app.get("/companies/stats")
async def stats(request: __import__("starlette").requests.Request):
    async with request.app.state.pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM companies")
        by_type = await conn.fetch("SELECT company_type, COUNT(*) as n FROM companies GROUP BY company_type ORDER BY n DESC")
        by_sector = await conn.fetch("SELECT unnest(sub_sector) as s, COUNT(*) as n FROM companies GROUP BY s ORDER BY n DESC")
        by_city = await conn.fetch("SELECT hq_city, COUNT(*) as n FROM companies WHERE hq_city IS NOT NULL GROUP BY hq_city ORDER BY n DESC LIMIT 10")
    return {
        "total": total,
        "by_type": {r["company_type"]: r["n"] for r in by_type},
        "by_sector": {r["s"]: r["n"] for r in by_sector},
        "by_city": {r["hq_city"]: r["n"] for r in by_city},
    }

@app.get("/companies")
async def list_companies(
    request: __import__("starlette").requests.Request,
    sub_sector: str = None,
    company_type: str = None,
    hq_city: str = None,
    search: str = None,
    page: int = 1,
    page_size: int = 50,
):
    conditions = ["status = 'active'"]
    params = []
    i = 1
    if sub_sector:
        conditions.append(f"${i} = ANY(sub_sector)"); params.append(sub_sector); i+=1
    if company_type:
        conditions.append(f"company_type = ${i}"); params.append(company_type); i+=1
    if hq_city:
        conditions.append(f"hq_city ILIKE ${i}"); params.append(f"%{hq_city}%"); i+=1
    if search:
        conditions.append(f"(name_en ILIKE ${i} OR name_he ILIKE ${i})"); params.append(f"%{search}%"); i+=1
    where = " AND ".join(conditions)
    offset = (page - 1) * page_size
    async with request.app.state.pool.acquire() as conn:
        total = await conn.fetchval(f"SELECT COUNT(*) FROM companies WHERE {where}", *params)
        rows = await conn.fetch(
            f"SELECT company_id, name_en, name_he, company_type, sub_sector, hq_city, founded_year, employee_count_est, data_quality_score, last_funding_date, description FROM companies WHERE {where} ORDER BY data_quality_score DESC LIMIT {page_size} OFFSET {offset}",
            *params
        )
    return {"total": total, "page": page, "page_size": page_size, "results": [dict(r) for r in rows]}

@app.get("/companies/{company_id}")
async def get_company(company_id: str, request: __import__("starlette").requests.Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM companies WHERE company_id = $1::uuid", company_id)
    if not row:
        raise HTTPException(status_code=404, detail="Company not found")
    return dict(row)
