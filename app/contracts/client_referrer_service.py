"""
Servicio para manejar operaciones de client_referrer
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import text

from app.contracts.models import client_referrer
from app.contracts.client_referrer_schemas import (
    ClientReferrerCreate,
    ClientReferrerResponse,
    ClientReferrerUpdate,
    ClientReferrerListResponse,
    ClientReferrerBulkCreate,
    ClientReferrerBulkResponse
)

logger = logging.getLogger(__name__)


class ClientReferrerService:
    """Servicio para manejar relaciones cliente-referidor"""

    @staticmethod
    async def create_client_referrer(
        client_id: UUID,
        referrer_id: UUID,
        connection: AsyncConnection,
        relation_date: Optional[datetime] = None,
        is_active: bool = True,
        created_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Crear una relación cliente-referidor
        """
        try:
            # Verificar si ya existe una relación activa
            existing_query = select(client_referrer).where(
                client_referrer.c.client_id == client_id,
                client_referrer.c.referrer_id == referrer_id,
                client_referrer.c.is_active == True
            )
            
            existing_result = await connection.execute(existing_query)
            existing = existing_result.fetchone()
            
            if existing:
                return {
                    "success": False,
                    "message": "Ya existe una relación activa entre este cliente y referidor",
                    "client_referrer_id": existing["client_referrer_id"]
                }

            # Crear nueva relación
            insert_values = {
                "client_id": client_id,
                "referrer_id": referrer_id,
                "relation_date": relation_date or datetime.now(),
                "is_active": is_active,
                "created_by": created_by,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            insert_query = client_referrer.insert().values(**insert_values).returning(
                client_referrer.c.client_referrer_id
            )
            
            result = await connection.execute(insert_query)
            await connection.commit()
            
            client_referrer_id = result.fetchone()["client_referrer_id"]
            
            logger.info(f"✅ Relación cliente-referidor creada: {client_referrer_id}")
            
            return {
                "success": True,
                "message": "Relación cliente-referidor creada exitosamente",
                "client_referrer_id": client_referrer_id
            }

        except Exception as e:
            logger.error(f"❌ Error creando relación cliente-referidor: {str(e)}")
            await connection.rollback()
            return {
                "success": False,
                "message": f"Error creando relación: {str(e)}"
            }

    @staticmethod
    async def create_bulk_client_referrer(
        bulk_data: ClientReferrerBulkCreate,
        connection: AsyncConnection
    ) -> ClientReferrerBulkResponse:
        """
        Crear múltiples relaciones cliente-referidor
        """
        created_relations = []
        errors = []
        
        for referrer_id in bulk_data.referrer_ids:
            try:
                result = await ClientReferrerService.create_client_referrer(
                    client_id=bulk_data.client_id,
                    referrer_id=referrer_id,
                    connection=connection,
                    relation_date=bulk_data.relation_date,
                    created_by=bulk_data.created_by
                )
                
                if result["success"]:
                    created_relations.append({
                        "client_referrer_id": result["client_referrer_id"],
                        "client_id": bulk_data.client_id,
                        "referrer_id": referrer_id,
                        "relation_date": bulk_data.relation_date or datetime.now(),
                        "is_active": True,
                        "created_at": datetime.now(),
                        "created_by": bulk_data.created_by,
                        "updated_at": datetime.now(),
                        "updated_by": None
                    })
                else:
                    errors.append({
                        "referrer_id": str(referrer_id),
                        "error": result["message"]
                    })
                    
            except Exception as e:
                errors.append({
                    "referrer_id": str(referrer_id),
                    "error": str(e)
                })

        return ClientReferrerBulkResponse(
            success=len(created_relations) > 0,
            message=f"Creadas {len(created_relations)} relaciones, {len(errors)} errores",
            created_count=len(created_relations),
            errors=errors if errors else None,
            created_relations=created_relations if created_relations else None
        )

    @staticmethod
    async def get_client_referrers(
        client_id: UUID,
        connection: AsyncConnection,
        include_inactive: bool = False
    ) -> List[ClientReferrerListResponse]:
        """
        Obtener todos los referidores de un cliente
        """
        try:
            query = select(client_referrer).where(
                client_referrer.c.client_id == client_id
            )
            
            if not include_inactive:
                query = query.where(client_referrer.c.is_active == True)
                
            result = await connection.execute(query)
            rows = result.fetchall()
            
            # Convertir a lista de diccionarios
            referrers = []
            for row in rows:
                referrers.append({
                    "client_referrer_id": row["client_referrer_id"],
                    "client_id": row["client_id"],
                    "referrer_id": row["referrer_id"],
                    "relation_date": row["relation_date"],
                    "is_active": row["is_active"],
                    "created_at": row["created_at"]
                })
            
            return referrers

        except Exception as e:
            logger.error(f"❌ Error obteniendo referidores del cliente: {str(e)}")
            return []

    @staticmethod
    async def get_referrer_clients(
        referrer_id: UUID,
        connection: AsyncConnection,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Obtener todos los clientes de un referidor
        """
        try:
            query = select(client_referrer).where(
                client_referrer.c.referrer_id == referrer_id
            )
            
            if not include_inactive:
                query = query.where(client_referrer.c.is_active == True)
                
            result = await connection.execute(query)
            rows = result.fetchall()
            
            # Convertir a lista de diccionarios
            clients = []
            for row in rows:
                clients.append({
                    "client_referrer_id": row["client_referrer_id"],
                    "client_id": row["client_id"],
                    "referrer_id": row["referrer_id"],
                    "relation_date": row["relation_date"],
                    "is_active": row["is_active"],
                    "created_at": row["created_at"]
                })
            
            return clients

        except Exception as e:
            logger.error(f"❌ Error obteniendo clientes del referidor: {str(e)}")
            return []

    @staticmethod
    async def update_client_referrer(
        client_referrer_id: int,
        update_data: ClientReferrerUpdate,
        connection: AsyncConnection
    ) -> Dict[str, Any]:
        """
        Actualizar una relación cliente-referidor
        """
        try:
            update_values = {}
            
            if update_data.relation_date is not None:
                update_values["relation_date"] = update_data.relation_date
            if update_data.is_active is not None:
                update_values["is_active"] = update_data.is_active
            if update_data.updated_by is not None:
                update_values["updated_by"] = update_data.updated_by
                
            update_values["updated_at"] = datetime.now()
            
            update_query = update(client_referrer).where(
                client_referrer.c.client_referrer_id == client_referrer_id
            ).values(**update_values)
            
            result = await connection.execute(update_query)
            await connection.commit()
            
            if result.rowcount > 0:
                logger.info(f"✅ Relación cliente-referidor actualizada: {client_referrer_id}")
                return {
                    "success": True,
                    "message": "Relación cliente-referidor actualizada exitosamente"
                }
            else:
                return {
                    "success": False,
                    "message": "No se encontró la relación especificada"
                }

        except Exception as e:
            logger.error(f"❌ Error actualizando relación cliente-referidor: {str(e)}")
            await connection.rollback()
            return {
                "success": False,
                "message": f"Error actualizando relación: {str(e)}"
            }

    @staticmethod
    async def deactivate_client_referrer(
        client_referrer_id: int,
        connection: AsyncConnection,
        updated_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Desactivar una relación cliente-referidor
        """
        try:
            update_query = update(client_referrer).where(
                client_referrer.c.client_referrer_id == client_referrer_id
            ).values(
                is_active=False,
                updated_by=updated_by,
                updated_at=datetime.now()
            )
            
            result = await connection.execute(update_query)
            await connection.commit()
            
            if result.rowcount > 0:
                logger.info(f"✅ Relación cliente-referidor desactivada: {client_referrer_id}")
                return {
                    "success": True,
                    "message": "Relación cliente-referidor desactivada exitosamente"
                }
            else:
                return {
                    "success": False,
                    "message": "No se encontró la relación especificada"
                }

        except Exception as e:
            logger.error(f"❌ Error desactivando relación cliente-referidor: {str(e)}")
            await connection.rollback()
            return {
                "success": False,
                "message": f"Error desactivando relación: {str(e)}"
            }
