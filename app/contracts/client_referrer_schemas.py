"""
Schemas para la tabla client_referrer
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ClientReferrerCreate(BaseModel):
    """Schema para crear una relación cliente-referidor"""
    client_id: UUID = Field(..., description="ID del cliente")
    referrer_id: UUID = Field(..., description="ID del referidor")
    relation_date: Optional[datetime] = Field(None, description="Fecha de la relación")
    is_active: Optional[bool] = Field(True, description="Estado de la relación")
    created_by: Optional[UUID] = Field(None, description="Usuario que crea la relación")


class ClientReferrerResponse(BaseModel):
    """Schema para respuesta de relación cliente-referidor creada"""
    client_referrer_id: int
    client_id: UUID
    referrer_id: UUID
    relation_date: datetime
    is_active: bool
    created_at: datetime
    created_by: Optional[UUID]
    updated_at: datetime
    updated_by: Optional[UUID]


class ClientReferrerUpdate(BaseModel):
    """Schema para actualizar relación cliente-referidor"""
    relation_date: Optional[datetime] = Field(None, description="Fecha de la relación")
    is_active: Optional[bool] = Field(None, description="Estado de la relación")
    updated_by: Optional[UUID] = Field(None, description="Usuario que actualiza")


class ClientReferrerListResponse(BaseModel):
    """Schema para lista de relaciones cliente-referidor"""
    client_referrer_id: int
    client_id: UUID
    referrer_id: UUID
    relation_date: datetime
    is_active: bool
    created_at: datetime
    # Información adicional del cliente
    client_name: Optional[str] = None
    client_document: Optional[str] = None
    # Información adicional del referidor
    referrer_name: Optional[str] = None
    referrer_document: Optional[str] = None
    referrer_phone: Optional[str] = None
    referrer_email: Optional[str] = None


class ClientReferrerBulkCreate(BaseModel):
    """Schema para crear múltiples relaciones cliente-referidor"""
    client_id: UUID = Field(..., description="ID del cliente")
    referrer_ids: list[UUID] = Field(..., description="Lista de IDs de referidores")
    relation_date: Optional[datetime] = Field(None, description="Fecha de la relación")
    created_by: Optional[UUID] = Field(None, description="Usuario que crea las relaciones")


class ClientReferrerBulkResponse(BaseModel):
    """Schema para respuesta de creación masiva"""
    success: bool
    message: str
    created_count: int
    errors: Optional[list[dict]] = None
    created_relations: Optional[list[ClientReferrerResponse]] = None
