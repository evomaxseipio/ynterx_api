from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from starlette.requests import Request

from app.company.service import RNCService, CompanyService
from app.company.models import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse,
    CompanySuccessResponse,
    CompanyListSuccessResponse,
    CompanyListSimpleResponse,
    RNCSuccessResponse,
    DeleteSuccessResponse
)

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


@router.get("/rnc/{rnc}/with-company", response_model=RNCSuccessResponse)
async def consultar_rnc_con_empresa(
    rnc: str,
    service: CompanyService = Depends(get_company_service)
) -> RNCSuccessResponse:
    """
    Consultar RNC y verificar si existe empresa en la base de datos

    Args:
        rnc (str): Número de RNC a consultar

    Returns:
        RNCSuccessResponse: Datos del RNC y información de empresa si existe
    """
    try:
        rnc_data = await service.consultar_rnc_con_empresa(rnc)
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


@router.get("/by-rnc/{rnc}", response_model=CompanySuccessResponse)
async def get_company_by_rnc(
    rnc: str,
    service: CompanyService = Depends(get_company_service)
) -> CompanySuccessResponse:
    """
    Obtener empresa por RNC

    Args:
        rnc (str): RNC de la empresa

    Returns:
        CompanySuccessResponse: Datos de la empresa
    """
    try:
        company = await service.get_company_by_rnc(rnc)
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


@router.get("/", response_model=CompanyListSuccessResponse)
async def get_all_companies(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(50, ge=1, le=100, description="Elementos por página"),
    search: Optional[str] = Query(None, description="Término de búsqueda"),
    service: CompanyService = Depends(get_company_service)
) -> CompanyListSuccessResponse:
    """
    Obtener todas las empresas con paginación y búsqueda

    Args:
        page (int): Número de página
        per_page (int): Elementos por página
        search (Optional[str]): Término de búsqueda

    Returns:
        CompanyListSuccessResponse: Lista de empresas con metadatos de paginación
    """
    try:
        companies = await service.get_all_companies(page, per_page, search)
        return CompanyListSuccessResponse(
            success=True,
            message="Empresas obtenidas exitosamente",
            data=companies
        )
    except HTTPException as e:
        return CompanyListSuccessResponse(
            success=False,
            error="FETCH_ERROR",
            message=e.detail
        )
    except Exception as e:
        return CompanyListSuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
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


@router.get("/search/rnc/{rnc}", response_model=CompanyListSimpleResponse)
async def search_companies_by_rnc(
    rnc: str,
    service: CompanyService = Depends(get_company_service)
) -> CompanyListSimpleResponse:
    """
    Buscar empresas por RNC (búsqueda parcial)

    Args:
        rnc (str): RNC a buscar

    Returns:
        CompanyListSimpleResponse: Lista de empresas que coinciden
    """
    try:
        companies = await service.search_companies_by_rnc(rnc)
        return CompanyListSimpleResponse(
            success=True,
            message=f"Se encontraron {len(companies)} empresas",
            data=companies
        )
    except HTTPException as e:
        return CompanyListSimpleResponse(
            success=False,
            error="SEARCH_ERROR",
            message=e.detail
        )
    except Exception as e:
        return CompanyListSimpleResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )


@router.get("/type/{company_type}", response_model=CompanyListSimpleResponse)
async def get_companies_by_type(
    company_type: str,
    service: CompanyService = Depends(get_company_service)
) -> CompanyListSimpleResponse:
    """
    Obtener empresas por tipo

    Args:
        company_type (str): Tipo de empresa

    Returns:
        CompanyListSimpleResponse: Lista de empresas del tipo especificado
    """
    try:
        companies = await service.get_companies_by_type(company_type)
        return CompanyListSimpleResponse(
            success=True,
            message=f"Se encontraron {len(companies)} empresas del tipo {company_type}",
            data=companies
        )
    except HTTPException as e:
        return CompanyListSimpleResponse(
            success=False,
            error="FETCH_ERROR",
            message=e.detail
        )
    except Exception as e:
        return CompanyListSimpleResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )
