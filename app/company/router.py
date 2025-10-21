# router_clean.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from starlette.requests import Request

from app.company.service import RNCService, CompanyService
from app.company.models import (
    CompanyCreate,
    CompanyUpdate,
    CompanySuccessResponse,
    CompanyListSuccessResponse,
    CompanyListSimpleResponse,
    RNCSuccessResponse,
    DeleteSuccessResponse,
    CompanyWithRelations,
    CompanyWithRelationsSuccessResponse,
    CompanyCompleteDataSuccessResponse
)
from app.auth.dependencies import DepCurrentUser

router = APIRouter(prefix="/company", tags=["company"])


def get_company_service(request: Request) -> CompanyService:
    """Dependency to get company service with database pool"""
    pool = request.app.state.db_pool
    return CompanyService(pool)


@router.get("/rnc/{rnc}", response_model=RNCSuccessResponse)
async def consultar_rnc(rnc: str) -> RNCSuccessResponse:
    """
    Consultar RNC en la DGII

    Args:
        rnc (str): Número de RNC a consultar

    Returns:
        RNCSuccessResponse: Datos del RNC consultado
    """
    try:
        service = RNCService()
        rnc_data = await service.consultar_rnc(rnc)
        return RNCSuccessResponse(
            success=True,
            message="RNC consultado exitosamente",
            data=rnc_data
        )
    except HTTPException as e:
        return RNCSuccessResponse(
            success=False,
            error="RNC_NOT_FOUND",
            message=e.detail
        )
    except Exception as e:
        return RNCSuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )


@router.get("/complete/rnc/{rnc}", response_model=CompanyCompleteDataSuccessResponse)
async def get_company_complete_by_rnc(
    rnc: str,
    service: CompanyService = Depends(get_company_service)
) -> CompanyCompleteDataSuccessResponse:
    """
    Obtener empresa completa por RNC con managers y direcciones

    Args:
        rnc (str): Número de RNC de la empresa

    Returns:
        CompanyCompleteDataSuccessResponse: Datos completos de la empresa con managers y direcciones
    """
    try:
        company_data = await service.get_company_complete_by_rnc(rnc)
        return CompanyCompleteDataSuccessResponse(
            success=True,
            message="Empresa encontrada exitosamente",
            data=company_data
        )
    except HTTPException as e:
        return CompanyCompleteDataSuccessResponse(
            success=False,
            error="COMPANY_NOT_FOUND",
            message=e.detail
        )
    except Exception as e:
        return CompanyCompleteDataSuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )


@router.post("/", response_model=CompanySuccessResponse)
async def create_company(
    company_data: CompanyCreate,
    service: CompanyService = Depends(get_company_service)
) -> CompanySuccessResponse:
    """
    Crear una nueva empresa

    Args:
        company_data (CompanyCreate): Datos de la empresa a crear

    Returns:
        CompanySuccessResponse: Empresa creada
    """
    try:
        company = await service.create_company(company_data)
        return CompanySuccessResponse(
            success=True,
            message="Empresa creada exitosamente",
            data=company
        )
    except HTTPException as e:
        return CompanySuccessResponse(
            success=False,
            error="CREATE_ERROR",
            message=e.detail
        )
    except Exception as e:
        return CompanySuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )


@router.get("/list", response_model=dict)
async def list_companies(
    _: DepCurrentUser,
    request: Request,
    rnc: Optional[str] = Query(None, description="Filtrar por RNC"),
    limit: int = Query(20, ge=1, le=100, description="Número de registros por página"),
    offset: int = Query(0, ge=0, description="Número de registros a saltar"),
) -> dict:
    """List all companies with pagination using stored procedure."""
    try:
        async with request.app.state.db_pool.acquire() as connection:
            # Crear CompanyService con el pool
            service = CompanyService(request.app.state.db_pool)
            return await service.list_companies(
                connection=connection,
                rnc=rnc,
                limit=limit,
                offset=offset
            )
    except Exception as e:
        return {
            "success": False,
            "status_code": 500,
            "error": f"Error en el endpoint: {str(e)}",
            "company_list": [],
            "pagination": {"limit": limit, "offset": offset, "total": 0}
        }


@router.get("/{company_id}", response_model=CompanySuccessResponse)
async def get_company(
    company_id: int,
    service: CompanyService = Depends(get_company_service)
) -> CompanySuccessResponse:
    """
    Obtener empresa por ID

    Args:
        company_id (int): ID de la empresa

    Returns:
        CompanySuccessResponse: Datos de la empresa
    """
    try:
        company = await service.get_company_by_id(company_id)
        return CompanySuccessResponse(
            success=True,
            message="Empresa encontrada exitosamente",
            data=company
        )
    except HTTPException as e:
        return CompanySuccessResponse(
            success=False,
            error="COMPANY_NOT_FOUND",
            message=e.detail
        )
    except Exception as e:
        return CompanySuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )
async def list_companies(
    _: DepCurrentUser,
    request: Request,
    rnc: Optional[str] = Query(None, description="Filtrar por RNC"),
    limit: int = Query(20, ge=1, le=100, description="Número de registros por página"),
    offset: int = Query(0, ge=0, description="Número de registros a saltar"),
) -> dict:
    """List all companies with pagination using stored procedure."""
    async with request.app.state.db_pool.acquire() as connection:
        return await CompanyService().list_companies(
            connection=connection,
            rnc=rnc,
            limit=limit,
            offset=offset
        )


@router.put("/{company_id}", response_model=CompanySuccessResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    service: CompanyService = Depends(get_company_service)
) -> CompanySuccessResponse:
    """
    Actualizar empresa

    Args:
        company_id (int): ID de la empresa
        company_data (CompanyUpdate): Datos a actualizar

    Returns:
        CompanySuccessResponse: Empresa actualizada
    """
    try:
        company = await service.update_company(company_id, company_data)
        return CompanySuccessResponse(
            success=True,
            message="Empresa actualizada exitosamente",
            data=company
        )
    except HTTPException as e:
        return CompanySuccessResponse(
            success=False,
            error="UPDATE_ERROR",
            message=e.detail
        )
    except Exception as e:
        return CompanySuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )


@router.delete("/{company_id}", response_model=DeleteSuccessResponse)
async def delete_company(
    company_id: int,
    service: CompanyService = Depends(get_company_service)
) -> DeleteSuccessResponse:
    """
    Eliminar empresa (soft delete)

    Args:
        company_id (int): ID de la empresa

    Returns:
        DeleteSuccessResponse: Mensaje de confirmación
    """
    try:
        await service.delete_company(company_id)
        return DeleteSuccessResponse(
            success=True,
            message="Empresa eliminada exitosamente",
            data={"company_id": company_id}
        )
    except HTTPException as e:
        return DeleteSuccessResponse(
            success=False,
            error="DELETE_ERROR",
            message=e.detail
        )
    except Exception as e:
        return DeleteSuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )
