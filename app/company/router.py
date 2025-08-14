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
    DeleteSuccessResponse,
    CompanyAddressCreate,
    CompanyAddressUpdate,
    CompanyAddressResponse,
    CompanyAddressSuccessResponse,
    CompanyManagerCreate,
    CompanyManagerUpdate,
    CompanyManagerResponse,
    CompanyManagerSuccessResponse,
    CompanyWithRelations,
    CompanyWithRelationsSuccessResponse
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


@router.get("/{company_id}/with-relations", response_model=CompanyWithRelationsSuccessResponse)
async def get_company_with_relations(
    company_id: int,
    service: CompanyService = Depends(get_company_service)
) -> CompanyWithRelationsSuccessResponse:
    """
    Obtener empresa con sus direcciones y gerentes

    Args:
        company_id (int): ID de la empresa

    Returns:
        CompanyWithRelationsSuccessResponse: Empresa con relaciones
    """
    try:
        company = await service.get_company_with_relations(company_id)
        return CompanyWithRelationsSuccessResponse(
            success=True,
            message="Empresa obtenida exitosamente",
            data=company
        )
    except HTTPException as e:
        return CompanyWithRelationsSuccessResponse(
            success=False,
            error="NOT_FOUND",
            message=e.detail
        )
    except Exception as e:
        return CompanyWithRelationsSuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )


# Company Address Endpoints
@router.post("/{company_id}/addresses", response_model=CompanyAddressSuccessResponse)
async def create_company_address(
    company_id: int,
    address_data: CompanyAddressCreate,
    service: CompanyService = Depends(get_company_service)
) -> CompanyAddressSuccessResponse:
    """
    Crear una nueva dirección para una empresa

    Args:
        company_id (int): ID de la empresa
        address_data (CompanyAddressCreate): Datos de la dirección

    Returns:
        CompanyAddressSuccessResponse: Dirección creada
    """
    try:
        address_data.company_id = company_id
        address = await service.create_company_address(address_data)
        return CompanyAddressSuccessResponse(
            success=True,
            message="Dirección creada exitosamente",
            data=address
        )
    except HTTPException as e:
        return CompanyAddressSuccessResponse(
            success=False,
            error="CREATE_ERROR",
            message=e.detail
        )
    except Exception as e:
        return CompanyAddressSuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )


@router.get("/{company_id}/addresses", response_model=CompanyListSimpleResponse)
async def get_company_addresses(
    company_id: int,
    service: CompanyService = Depends(get_company_service)
) -> CompanyListSimpleResponse:
    """
    Obtener todas las direcciones de una empresa

    Args:
        company_id (int): ID de la empresa

    Returns:
        CompanyListSimpleResponse: Lista de direcciones
    """
    try:
        addresses = await service.get_addresses_by_company_id(company_id)
        return CompanyListSimpleResponse(
            success=True,
            message=f"Se encontraron {len(addresses)} direcciones",
            data=addresses
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


@router.get("/addresses/{address_id}", response_model=CompanyAddressSuccessResponse)
async def get_company_address(
    address_id: int,
    service: CompanyService = Depends(get_company_service)
) -> CompanyAddressSuccessResponse:
    """
    Obtener una dirección específica

    Args:
        address_id (int): ID de la dirección

    Returns:
        CompanyAddressSuccessResponse: Dirección encontrada
    """
    try:
        address = await service.get_company_address_by_id(address_id)
        return CompanyAddressSuccessResponse(
            success=True,
            message="Dirección obtenida exitosamente",
            data=address
        )
    except HTTPException as e:
        return CompanyAddressSuccessResponse(
            success=False,
            error="NOT_FOUND",
            message=e.detail
        )
    except Exception as e:
        return CompanyAddressSuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )


@router.put("/addresses/{address_id}", response_model=CompanyAddressSuccessResponse)
async def update_company_address(
    address_id: int,
    address_data: CompanyAddressUpdate,
    service: CompanyService = Depends(get_company_service)
) -> CompanyAddressSuccessResponse:
    """
    Actualizar una dirección de empresa

    Args:
        address_id (int): ID de la dirección
        address_data (CompanyAddressUpdate): Datos a actualizar

    Returns:
        CompanyAddressSuccessResponse: Dirección actualizada
    """
    try:
        address = await service.update_company_address(address_id, address_data)
        return CompanyAddressSuccessResponse(
            success=True,
            message="Dirección actualizada exitosamente",
            data=address
        )
    except HTTPException as e:
        return CompanyAddressSuccessResponse(
            success=False,
            error="UPDATE_ERROR",
            message=e.detail
        )
    except Exception as e:
        return CompanyAddressSuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )


@router.delete("/addresses/{address_id}", response_model=DeleteSuccessResponse)
async def delete_company_address(
    address_id: int,
    service: CompanyService = Depends(get_company_service)
) -> DeleteSuccessResponse:
    """
    Eliminar una dirección de empresa (soft delete)

    Args:
        address_id (int): ID de la dirección

    Returns:
        DeleteSuccessResponse: Mensaje de confirmación
    """
    try:
        await service.delete_company_address(address_id)
        return DeleteSuccessResponse(
            success=True,
            message="Dirección eliminada exitosamente",
            data={"address_id": address_id}
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


# Company Manager Endpoints
@router.post("/{company_id}/managers", response_model=CompanyManagerSuccessResponse)
async def create_company_manager(
    company_id: int,
    manager_data: CompanyManagerCreate,
    service: CompanyService = Depends(get_company_service)
) -> CompanyManagerSuccessResponse:
    """
    Crear un nuevo gerente para una empresa

    Args:
        company_id (int): ID de la empresa
        manager_data (CompanyManagerCreate): Datos del gerente

    Returns:
        CompanyManagerSuccessResponse: Gerente creado
    """
    try:
        manager_data.company_id = company_id
        manager = await service.create_company_manager(manager_data)
        return CompanyManagerSuccessResponse(
            success=True,
            message="Gerente creado exitosamente",
            data=manager
        )
    except HTTPException as e:
        return CompanyManagerSuccessResponse(
            success=False,
            error="CREATE_ERROR",
            message=e.detail
        )
    except Exception as e:
        return CompanyManagerSuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )


@router.get("/{company_id}/managers", response_model=CompanyListSimpleResponse)
async def get_company_managers(
    company_id: int,
    service: CompanyService = Depends(get_company_service)
) -> CompanyListSimpleResponse:
    """
    Obtener todos los gerentes de una empresa

    Args:
        company_id (int): ID de la empresa

    Returns:
        CompanyListSimpleResponse: Lista de gerentes
    """
    try:
        managers = await service.get_managers_by_company_id(company_id)
        return CompanyListSimpleResponse(
            success=True,
            message=f"Se encontraron {len(managers)} gerentes",
            data=managers
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


@router.get("/managers/{manager_id}", response_model=CompanyManagerSuccessResponse)
async def get_company_manager(
    manager_id: int,
    service: CompanyService = Depends(get_company_service)
) -> CompanyManagerSuccessResponse:
    """
    Obtener un gerente específico

    Args:
        manager_id (int): ID del gerente

    Returns:
        CompanyManagerSuccessResponse: Gerente encontrado
    """
    try:
        manager = await service.get_company_manager_by_id(manager_id)
        return CompanyManagerSuccessResponse(
            success=True,
            message="Gerente obtenido exitosamente",
            data=manager
        )
    except HTTPException as e:
        return CompanyManagerSuccessResponse(
            success=False,
            error="NOT_FOUND",
            message=e.detail
        )
    except Exception as e:
        return CompanyManagerSuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )


@router.put("/managers/{manager_id}", response_model=CompanyManagerSuccessResponse)
async def update_company_manager(
    manager_id: int,
    manager_data: CompanyManagerUpdate,
    service: CompanyService = Depends(get_company_service)
) -> CompanyManagerSuccessResponse:
    """
    Actualizar un gerente de empresa

    Args:
        manager_id (int): ID del gerente
        manager_data (CompanyManagerUpdate): Datos a actualizar

    Returns:
        CompanyManagerSuccessResponse: Gerente actualizado
    """
    try:
        manager = await service.update_company_manager(manager_id, manager_data)
        return CompanyManagerSuccessResponse(
            success=True,
            message="Gerente actualizado exitosamente",
            data=manager
        )
    except HTTPException as e:
        return CompanyManagerSuccessResponse(
            success=False,
            error="UPDATE_ERROR",
            message=e.detail
        )
    except Exception as e:
        return CompanyManagerSuccessResponse(
            success=False,
            error="INTERNAL_ERROR",
            message=f"Error interno: {str(e)}"
        )


@router.delete("/managers/{manager_id}", response_model=DeleteSuccessResponse)
async def delete_company_manager(
    manager_id: int,
    service: CompanyService = Depends(get_company_service)
) -> DeleteSuccessResponse:
    """
    Eliminar un gerente de empresa (soft delete)

    Args:
        manager_id (int): ID del gerente

    Returns:
        DeleteSuccessResponse: Mensaje de confirmación
    """
    try:
        await service.delete_company_manager(manager_id)
        return DeleteSuccessResponse(
            success=True,
            message="Gerente eliminado exitosamente",
            data={"manager_id": manager_id}
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
