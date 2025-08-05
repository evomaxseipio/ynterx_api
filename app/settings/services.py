"""Service layer for contract paragraphs operations."""

from typing import Dict, Any, List
from sqlalchemy import select, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.exc import IntegrityError

from app.database import fetch_one, fetch_all
from app.settings.models import contract_paragraphs
from app.settings.schemas import (
    ContractParagraphCreate,
    ContractParagraphUpdate,
    ContractParagraphFilter,
    ContractParagraphBulkCreate,
    ContractParagraphBulkOrderUpdate
)


class ContractParagraphService:
    @staticmethod
    async def create_paragraph(
        paragraph_data: ContractParagraphCreate,
        connection: AsyncConnection | None = None,
    ) -> dict:
        """Create a new contract paragraph."""
        try:
            query = contract_paragraphs.insert().values(
                person_role=paragraph_data.person_role,
                contract_type=paragraph_data.contract_type,
                section=paragraph_data.section,
                order_position=paragraph_data.order_position,
                title=paragraph_data.title,
                paragraph_content=paragraph_data.paragraph_content,
                paragraph_variables=paragraph_data.paragraph_variables,
                contract_services=paragraph_data.contract_services,
                is_active=paragraph_data.is_active,
            ).returning(contract_paragraphs)

            result = await fetch_one(query, connection=connection, commit_after=True)
            return result
        except IntegrityError as e:
            if "contract_paragraphs_person_role_contract_type_section_contr_key" in str(e):
                raise ValueError(
                    f"A paragraph already exists for person_role='{paragraph_data.person_role}', "
                    f"contract_type='{paragraph_data.contract_type}', "
                    f"section='{paragraph_data.section}', "
                    f"contract_services='{paragraph_data.contract_services}'"
                )
            raise e

    @staticmethod
    async def get_paragraph(
        paragraph_id: int,
        connection: AsyncConnection | None = None,
    ) -> dict | None:
        """Get a contract paragraph by ID."""
        query = select(contract_paragraphs).where(
            contract_paragraphs.c.paragraph_id == paragraph_id
        )
        return await fetch_one(query, connection=connection)

    @staticmethod
    async def update_paragraph(
        paragraph_id: int,
        paragraph_data: ContractParagraphUpdate,
        connection: AsyncConnection | None = None,
    ) -> dict | None:
        """Update a contract paragraph."""
        values = paragraph_data.model_dump(exclude_unset=True)
        if not values:
            return await ContractParagraphService.get_paragraph(paragraph_id, connection=connection)

        # Add updated_at timestamp
        values["updated_at"] = text("CURRENT_TIMESTAMP")

        try:
            query = (
                contract_paragraphs.update()
                .where(contract_paragraphs.c.paragraph_id == paragraph_id)
                .values(**values)
                .returning(contract_paragraphs)
            )
            return await fetch_one(query, connection=connection, commit_after=True)
        except IntegrityError as e:
            if "contract_paragraphs_person_role_contract_type_section_contr_key" in str(e):
                raise ValueError(
                    "This combination of person_role, contract_type, section, and contract_services already exists"
                )
            raise e

    @staticmethod
    async def delete_paragraph(
        paragraph_id: int,
        connection: AsyncConnection | None = None,
        soft_delete: bool = True,
    ) -> dict | None:
        """Delete a contract paragraph (soft delete by default)."""
        if soft_delete:
            query = (
                contract_paragraphs.update()
                .where(contract_paragraphs.c.paragraph_id == paragraph_id)
                .values(is_active=False, updated_at=text("CURRENT_TIMESTAMP"))
                .returning(contract_paragraphs)
            )
        else:
            query = (
                contract_paragraphs.delete()
                .where(contract_paragraphs.c.paragraph_id == paragraph_id)
                .returning(contract_paragraphs)
            )
        return await fetch_one(query, connection=connection, commit_after=True)

    @staticmethod
    async def list_paragraphs(
        filters: ContractParagraphFilter,
        connection: AsyncConnection | None = None,
    ) -> list[dict]:
        """List contract paragraphs with filters and pagination."""
        conditions = []

        if filters.person_role:
            conditions.append(contract_paragraphs.c.person_role == filters.person_role)

        if filters.contract_type:
            conditions.append(contract_paragraphs.c.contract_type == filters.contract_type)

        if filters.section:
            conditions.append(contract_paragraphs.c.section == filters.section)

        if filters.contract_services:
            conditions.append(contract_paragraphs.c.contract_services == filters.contract_services)

        if filters.is_active is not None:
            conditions.append(contract_paragraphs.c.is_active == filters.is_active)

        query = select(contract_paragraphs)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(
            contract_paragraphs.c.person_role,
            contract_paragraphs.c.contract_type,
            contract_paragraphs.c.section,
            contract_paragraphs.c.order_position
        ).offset(filters.skip).limit(filters.limit)

        return await fetch_all(query, connection=connection)

    @staticmethod
    async def get_paragraphs_for_contract(
        person_role: str,
        contract_type: str,
        contract_services: str = "mortgage",
        connection: AsyncConnection | None = None,
    ) -> list[dict]:
        """Get all active paragraphs for a specific contract configuration."""
        query = select(contract_paragraphs).where(
            and_(
                contract_paragraphs.c.person_role == person_role,
                contract_paragraphs.c.contract_type == contract_type,
                contract_paragraphs.c.contract_services == contract_services,
                contract_paragraphs.c.is_active == True
            )
        ).order_by(contract_paragraphs.c.section, contract_paragraphs.c.order_position)

        return await fetch_all(query, connection=connection)

    @staticmethod
    async def bulk_create_paragraphs(
        bulk_data: ContractParagraphBulkCreate,
        connection: AsyncConnection | None = None,
    ) -> list[dict]:
        """Create multiple contract paragraphs."""
        results = []
        for paragraph_data in bulk_data.paragraphs:
            try:
                result = await ContractParagraphService.create_paragraph(
                    paragraph_data, connection=connection
                )
                results.append(result)
            except ValueError as e:
                # Skip duplicates and continue
                results.append({"error": str(e), "data": paragraph_data.model_dump()})

        return results

    @staticmethod
    async def update_paragraph_orders(
        bulk_order_data: ContractParagraphBulkOrderUpdate,
        connection: AsyncConnection | None = None,
    ) -> list[dict]:
        """Update order positions for multiple paragraphs."""
        results = []

        for order_update in bulk_order_data.order_updates:
            query = (
                contract_paragraphs.update()
                .where(contract_paragraphs.c.paragraph_id == order_update.paragraph_id)
                .values(
                    order_position=order_update.order_position,
                    updated_at=text("CURRENT_TIMESTAMP")
                )
                .returning(contract_paragraphs)
            )
            result = await fetch_one(query, connection=connection, commit_after=True)
            if result:
                results.append(result)

        return results

    @staticmethod
    async def search_paragraphs(
        search_term: str,
        connection: AsyncConnection | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search paragraphs by title or content."""
        query = select(contract_paragraphs).where(
            and_(
                or_(
                    contract_paragraphs.c.title.ilike(f"%{search_term}%"),
                    contract_paragraphs.c.paragraph_content.ilike(f"%{search_term}%")
                ),
                contract_paragraphs.c.is_active == True
            )
        ).order_by(contract_paragraphs.c.section, contract_paragraphs.c.order_position).limit(limit)

        return await fetch_all(query, connection=connection)

    @staticmethod
    async def get_paragraph_variables(
        paragraph_id: int,
        connection: AsyncConnection | None = None,
    ) -> Dict[str, Any] | None:
        """Get paragraph variables for a specific paragraph."""
        query = select(contract_paragraphs.c.paragraph_variables).where(
            contract_paragraphs.c.paragraph_id == paragraph_id
        )
        result = await fetch_one(query, connection=connection)
        return result["paragraph_variables"] if result else None
