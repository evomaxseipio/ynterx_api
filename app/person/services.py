from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import select, update, insert, text
from app.database import fetch_one, fetch_all, execute
from app.person.models import referrer
from app.person.schemas import ReferrerCreate, ReferrerUpdate, ReferrerResponse
from uuid import UUID


class ReferrerService:
    """Servicio para manejar referentes"""

    @staticmethod
    async def create_or_update_referrer(
        referrer_data: ReferrerCreate,
        connection: AsyncConnection | None = None,
    ) -> Dict[str, Any]:
        """Crear o actualizar un referente"""
        try:
            # Verificar si ya existe un referente para esta persona
            existing_query = select(referrer).where(
                referrer.c.person_id == referrer_data.person_id
            )
            existing_referrer = await fetch_one(existing_query, connection=connection)

            if existing_referrer:
                # Actualizar referente existente
                update_query = (
                    update(referrer)
                    .where(referrer.c.person_id == referrer_data.person_id)
                    .values(
                        referral_code=referrer_data.referral_code,
                        referrer_phone_number=referrer_data.referrer_phone_number,
                        bank_name=referrer_data.bank_name,
                        bank_account=referrer_data.bank_account,
                        commission_percentage=referrer_data.commission_percentage,
                        notes=referrer_data.notes,
                        is_active=referrer_data.is_active,
                        updated_at=text("CURRENT_TIMESTAMP")
                    )
                    .returning(referrer)
                )
                result = await fetch_one(update_query, connection=connection, commit_after=True)
                return {
                    "success": True,
                    "message": "Referente actualizado exitosamente",
                    "action": "updated",
                    "referrer": result
                }
            else:
                # Crear nuevo referente
                insert_query = (
                    insert(referrer)
                    .values(
                        person_id=referrer_data.person_id,
                        referral_code=referrer_data.referral_code,
                        referrer_phone_number=referrer_data.referrer_phone_number,
                        bank_name=referrer_data.bank_name,
                        bank_account=referrer_data.bank_account,
                        commission_percentage=referrer_data.commission_percentage,
                        notes=referrer_data.notes,
                        is_active=referrer_data.is_active
                    )
                    .returning(referrer)
                )
                result = await fetch_one(insert_query, connection=connection, commit_after=True)
                return {
                    "success": True,
                    "message": "Referente creado exitosamente",
                    "action": "created",
                    "referrer": result
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error al crear/actualizar referente: {str(e)}",
                "action": "error"
            }

    @staticmethod
    async def get_referrer_by_person_id(
        person_id: UUID,
        connection: AsyncConnection | None = None,
    ) -> Optional[Dict[str, Any]]:
        """Obtener referente por person_id"""
        query = select(referrer).where(
            referrer.c.person_id == person_id,
            referrer.c.is_active == True
        )
        return await fetch_one(query, connection=connection)

    @staticmethod
    async def get_referrer_by_id(
        referrer_id: UUID,
        connection: AsyncConnection | None = None,
    ) -> Optional[Dict[str, Any]]:
        """Obtener referente por referrer_id"""
        query = select(referrer).where(
            referrer.c.referrer_id == referrer_id,
            referrer.c.is_active == True
        )
        return await fetch_one(query, connection=connection)

    @staticmethod
    async def list_referrers(
        connection: AsyncConnection | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Listar todos los referentes activos"""
        query = (
            select(referrer)
            .where(referrer.c.is_active == True)
            .order_by(referrer.c.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return await fetch_all(query, connection=connection)

    @staticmethod
    async def increment_referred_clients_count(
        person_id: UUID,
        connection: AsyncConnection | None = None,
    ) -> Dict[str, Any]:
        """Incrementar el contador de clientes referidos"""
        try:
            update_query = (
                update(referrer)
                .where(referrer.c.person_id == person_id)
                .values(
                    referred_clients_count=referrer.c.referred_clients_count + 1,
                    updated_at=text("CURRENT_TIMESTAMP")
                )
                .returning(referrer)
            )
            result = await fetch_one(update_query, connection=connection, commit_after=True)
            return {
                "success": True,
                "message": "Contador de clientes referidos incrementado",
                "referrer": result
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al incrementar contador: {str(e)}"
            } 