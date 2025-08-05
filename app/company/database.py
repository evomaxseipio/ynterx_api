from typing import List, Optional, Dict, Any
import asyncpg
from datetime import datetime

from app.company.models import CompanyCreate, CompanyUpdate, CompanyResponse


class CompanyDatabase:
    """Database operations for company table"""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_company(self, company_data: CompanyCreate) -> CompanyResponse:
        """Create a new company"""
        query = """
            INSERT INTO company (
                company_name, rnc, rm, email, phone, website, 
                company_type, tax_id, is_active
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING company_id, company_name, rnc, rm, email, phone, website,
                      company_type, tax_id, is_active, created_at, updated_at
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                company_data.company_name,
                company_data.rnc,
                company_data.rm,
                company_data.email,
                company_data.phone,
                company_data.website,
                company_data.company_type,
                company_data.tax_id,
                company_data.is_active
            )
            
            return CompanyResponse(**dict(row))

    async def get_company_by_id(self, company_id: int) -> Optional[CompanyResponse]:
        """Get company by ID"""
        query = """
            SELECT company_id, company_name, rnc, rm, email, phone, website,
                   company_type, tax_id, is_active, created_at, updated_at
            FROM company
            WHERE company_id = $1 AND is_active = true
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, company_id)
            return CompanyResponse(**dict(row)) if row else None

    async def get_company_by_rnc(self, rnc: str) -> Optional[CompanyResponse]:
        """Get company by RNC"""
        query = """
            SELECT company_id, company_name, rnc, rm, email, phone, website,
                   company_type, tax_id, is_active, created_at, updated_at
            FROM company
            WHERE rnc = $1 AND is_active = true
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, rnc)
            return CompanyResponse(**dict(row)) if row else None

    async def get_all_companies(
        self, 
        page: int = 1, 
        per_page: int = 50,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all companies with pagination and search"""
        
        # Build WHERE clause for search
        where_clause = "WHERE is_active = true"
        params = []
        param_count = 0
        
        if search:
            param_count += 1
            where_clause += f" AND (company_name ILIKE ${param_count} OR rnc ILIKE ${param_count})"
            params.append(f"%{search}%")
        
        # Count total
        count_query = f"SELECT COUNT(*) FROM company {where_clause}"
        async with self.pool.acquire() as conn:
            total = await conn.fetchval(count_query, *params)
        
        # Get paginated results
        offset = (page - 1) * per_page
        param_count += 1
        limit_param = param_count
        param_count += 1
        offset_param = param_count
        
        query = f"""
            SELECT company_id, company_name, rnc, rm, email, phone, website,
                   company_type, tax_id, is_active, created_at, updated_at
            FROM company
            {where_clause}
            ORDER BY company_name
            LIMIT ${limit_param} OFFSET ${offset_param}
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *(params + [per_page, offset]))
            
            companies = [CompanyResponse(**dict(row)) for row in rows]
            
            return {
                "companies": companies,
                "total": total,
                "page": page,
                "per_page": per_page
            }

    async def update_company(self, company_id: int, company_data: CompanyUpdate) -> Optional[CompanyResponse]:
        """Update company"""
        # Build dynamic update query
        update_fields = []
        params = []
        param_count = 0
        
        for field, value in company_data.dict(exclude_unset=True).items():
            if value is not None:
                param_count += 1
                update_fields.append(f"{field} = ${param_count}")
                params.append(value)
        
        if not update_fields:
            return await self.get_company_by_id(company_id)
        
        param_count += 1
        params.append(company_id)
        
        query = f"""
            UPDATE company
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE company_id = ${param_count} AND is_active = true
            RETURNING company_id, company_name, rnc, rm, email, phone, website,
                      company_type, tax_id, is_active, created_at, updated_at
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)
            return CompanyResponse(**dict(row)) if row else None

    async def delete_company(self, company_id: int) -> bool:
        """Soft delete company (set is_active = false)"""
        query = """
            UPDATE company
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE company_id = $1
            RETURNING company_id
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, company_id)
            return row is not None

    async def search_companies_by_rnc(self, rnc: str) -> List[CompanyResponse]:
        """Search companies by RNC (partial match)"""
        query = """
            SELECT company_id, company_name, rnc, rm, email, phone, website,
                   company_type, tax_id, is_active, created_at, updated_at
            FROM company
            WHERE rnc ILIKE $1 AND is_active = true
            ORDER BY company_name
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, f"%{rnc}%")
            return [CompanyResponse(**dict(row)) for row in rows]

    async def get_companies_by_type(self, company_type: str) -> List[CompanyResponse]:
        """Get companies by type"""
        query = """
            SELECT company_id, company_name, rnc, rm, email, phone, website,
                   company_type, tax_id, is_active, created_at, updated_at
            FROM company
            WHERE company_type = $1 AND is_active = true
            ORDER BY company_name
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, company_type)
            return [CompanyResponse(**dict(row)) for row in rows] 