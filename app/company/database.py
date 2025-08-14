from typing import List, Optional, Dict, Any
import asyncpg
from datetime import datetime

from app.company.models import (
    CompanyCreate, CompanyUpdate, CompanyResponse,
    CompanyAddressCreate, CompanyAddressUpdate, CompanyAddressResponse,
    CompanyManagerCreate, CompanyManagerUpdate, CompanyManagerResponse
)


class CompanyDatabase:
    """Database operations for company table"""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_company(self, company_data: CompanyCreate) -> CompanyResponse:
        """Create a new company"""
        query = """
            INSERT INTO company (
                company_name, company_rnc, mercantil_registry, nationality, email, phone, website, 
                company_type, company_description, frontImagePath, backImagePath, is_active
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING company_id, company_name, company_rnc, mercantil_registry, nationality, email, phone, website,
                      company_type, company_description, frontImagePath, backImagePath, is_active, created_at, updated_at
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                company_data.company_name,
                company_data.company_rnc,
                company_data.mercantil_registry,
                company_data.nationality,
                company_data.email,
                company_data.phone,
                company_data.website,
                company_data.company_type,
                company_data.company_description,
                company_data.frontImagePath,
                company_data.backImagePath,
                company_data.is_active
            )
            
            return CompanyResponse(**dict(row))

    async def get_company_by_id(self, company_id: int) -> Optional[CompanyResponse]:
        """Get company by ID"""
        query = """
            SELECT company_id, company_name, company_rnc, mercantil_registry, nationality, email, phone, website,
                   company_type, company_description, frontImagePath, backImagePath, is_active, created_at, updated_at
            FROM company
            WHERE company_id = $1 AND is_active = true
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, company_id)
            return CompanyResponse(**dict(row)) if row else None

    async def get_company_by_rnc(self, rnc: str) -> Optional[CompanyResponse]:
        """Get company by RNC"""
        query = """
            SELECT company_id, company_name, company_rnc, mercantil_registry, nationality, email, phone, website,
                   company_type, company_description, frontImagePath, backImagePath, is_active, created_at, updated_at
            FROM company
            WHERE company_rnc = $1 AND is_active = true
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
            where_clause += f" AND (company_name ILIKE ${param_count} OR company_rnc ILIKE ${param_count})"
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
            SELECT company_id, company_name, company_rnc, mercantil_registry, nationality, email, phone, website,
                   company_type, company_description, frontImagePath, backImagePath, is_active, created_at, updated_at
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
            RETURNING company_id, company_name, company_rnc, mercantil_registry, nationality, email, phone, website,
                      company_type, company_description, frontImagePath, backImagePath, is_active, created_at, updated_at
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
            SELECT company_id, company_name, company_rnc, mercantil_registry, nationality, email, phone, website,
                   company_type, company_description, frontImagePath, backImagePath, is_active, created_at, updated_at
            FROM company
            WHERE company_rnc ILIKE $1 AND is_active = true
            ORDER BY company_name
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, f"%{rnc}%")
            return [CompanyResponse(**dict(row)) for row in rows]

    async def get_companies_by_type(self, company_type: str) -> List[CompanyResponse]:
        """Get companies by type"""
        query = """
            SELECT company_id, company_name, company_rnc, mercantil_registry, nationality, email, phone, website,
                   company_type, company_description, frontImagePath, backImagePath, is_active, created_at, updated_at
            FROM company
            WHERE company_type = $1 AND is_active = true
            ORDER BY company_name
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, company_type)
            return [CompanyResponse(**dict(row)) for row in rows]


class CompanyAddressDatabase:
    """Database operations for company_address table"""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_company_address(self, address_data: CompanyAddressCreate) -> CompanyAddressResponse:
        """Create a new company address"""
        query = """
            INSERT INTO company_address (
                company_id, address_line1, address_line2, city, postal_code, address_type,
                email, phone, is_principal, is_active
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING company_address_id, company_id, address_line1, address_line2, city, postal_code,
                      address_type, email, phone, is_principal, is_active, created_at, updated_at
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                address_data.company_id,
                address_data.address_line1,
                address_data.address_line2,
                address_data.city,
                address_data.postal_code,
                address_data.address_type,
                address_data.email,
                address_data.phone,
                address_data.is_principal,
                address_data.is_active
            )
            
            return CompanyAddressResponse(**dict(row))

    async def get_company_address_by_id(self, address_id: int) -> Optional[CompanyAddressResponse]:
        """Get company address by ID"""
        query = """
            SELECT company_address_id, company_id, address_line1, address_line2, city, postal_code,
                   address_type, email, phone, is_principal, is_active, created_at, updated_at
            FROM company_address
            WHERE company_address_id = $1 AND is_active = true
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, address_id)
            return CompanyAddressResponse(**dict(row)) if row else None

    async def get_addresses_by_company_id(self, company_id: int) -> List[CompanyAddressResponse]:
        """Get all addresses for a company"""
        query = """
            SELECT company_address_id, company_id, address_line1, address_line2, city, postal_code,
                   address_type, email, phone, is_principal, is_active, created_at, updated_at
            FROM company_address
            WHERE company_id = $1 AND is_active = true
            ORDER BY is_principal DESC, address_line1
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, company_id)
            return [CompanyAddressResponse(**dict(row)) for row in rows]

    async def update_company_address(self, address_id: int, address_data: CompanyAddressUpdate) -> Optional[CompanyAddressResponse]:
        """Update company address"""
        # Build dynamic update query
        update_fields = []
        params = []
        param_count = 0
        
        for field, value in address_data.dict(exclude_unset=True).items():
            if value is not None:
                param_count += 1
                update_fields.append(f"{field} = ${param_count}")
                params.append(value)
        
        if not update_fields:
            return await self.get_company_address_by_id(address_id)
        
        param_count += 1
        params.append(address_id)
        
        query = f"""
            UPDATE company_address
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE company_address_id = ${param_count} AND is_active = true
            RETURNING company_address_id, company_id, address_line1, address_line2, city, postal_code,
                      address_type, email, phone, is_principal, is_active, created_at, updated_at
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)
            return CompanyAddressResponse(**dict(row)) if row else None

    async def delete_company_address(self, address_id: int) -> bool:
        """Soft delete company address (set is_active = false)"""
        query = """
            UPDATE company_address
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE company_address_id = $1
            RETURNING company_address_id
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, address_id)
            return row is not None


class CompanyManagerDatabase:
    """Database operations for company_manager table"""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_company_manager(self, manager_data: CompanyManagerCreate) -> CompanyManagerResponse:
        """Create a new company manager"""
        query = """
            INSERT INTO company_manager (
                company_id, manager_full_name, manager_position, manager_address, manager_document_number,
                manager_nationality, manager_civil_status, is_principal, is_active, created_by
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING manager_id, company_id, manager_full_name, manager_position, manager_address,
                      manager_document_number, manager_nationality, manager_civil_status, is_principal,
                      is_active, created_at, updated_at, created_by, updated_by
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                manager_data.company_id,
                manager_data.manager_full_name,
                manager_data.manager_position,
                manager_data.manager_address,
                manager_data.manager_document_number,
                manager_data.manager_nationality,
                manager_data.manager_civil_status,
                manager_data.is_principal,
                manager_data.is_active,
                manager_data.created_by
            )
            
            return CompanyManagerResponse(**dict(row))

    async def get_company_manager_by_id(self, manager_id: int) -> Optional[CompanyManagerResponse]:
        """Get company manager by ID"""
        query = """
            SELECT manager_id, company_id, manager_full_name, manager_position, manager_address,
                   manager_document_number, manager_nationality, manager_civil_status, is_principal,
                   is_active, created_at, updated_at, created_by, updated_by
            FROM company_manager
            WHERE manager_id = $1 AND is_active = true
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, manager_id)
            return CompanyManagerResponse(**dict(row)) if row else None

    async def get_managers_by_company_id(self, company_id: int) -> List[CompanyManagerResponse]:
        """Get all managers for a company"""
        query = """
            SELECT manager_id, company_id, manager_full_name, manager_position, manager_address,
                   manager_document_number, manager_nationality, manager_civil_status, is_principal,
                   is_active, created_at, updated_at, created_by, updated_by
            FROM company_manager
            WHERE company_id = $1 AND is_active = true
            ORDER BY is_principal DESC, manager_full_name
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, company_id)
            return [CompanyManagerResponse(**dict(row)) for row in rows]

    async def update_company_manager(self, manager_id: int, manager_data: CompanyManagerUpdate) -> Optional[CompanyManagerResponse]:
        """Update company manager"""
        # Build dynamic update query
        update_fields = []
        params = []
        param_count = 0
        
        for field, value in manager_data.dict(exclude_unset=True).items():
            if value is not None:
                param_count += 1
                update_fields.append(f"{field} = ${param_count}")
                params.append(value)
        
        if not update_fields:
            return await self.get_company_manager_by_id(manager_id)
        
        param_count += 1
        params.append(manager_id)
        
        query = f"""
            UPDATE company_manager
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE manager_id = ${param_count} AND is_active = true
            RETURNING manager_id, company_id, manager_full_name, manager_position, manager_address,
                      manager_document_number, manager_nationality, manager_civil_status, is_principal,
                      is_active, created_at, updated_at, created_by, updated_by
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)
            return CompanyManagerResponse(**dict(row)) if row else None

    async def delete_company_manager(self, manager_id: int) -> bool:
        """Soft delete company manager (set is_active = false)"""
        query = """
            UPDATE company_manager
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE manager_id = $1
            RETURNING manager_id
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, manager_id)
            return row is not None 