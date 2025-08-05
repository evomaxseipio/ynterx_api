from fastapi import HTTPException
from bs4 import BeautifulSoup
import httpx
from typing import Dict, Any, Optional, List
import logging
import csv
import os
from pathlib import Path
import asyncpg

from app.company.models import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyListResponse
from app.company.database import CompanyDatabase

logger = logging.getLogger(__name__)


class RNCService:
    """Servicio para consultar RNC en la DGII"""

    BASE_URL = "https://dgii.gov.do/app/WebApps/ConsultasWeb2/ConsultasWeb/consultas/rnc.aspx"
    CSV_FILE_PATH = Path(__file__).parent.parent / "utils" / "RNC_Contribuyentes_Actualizado_26_Jul_2025.csv"

    def __init__(self):
        self._csv_data = None
        self._load_csv_data()

    def _load_csv_data(self):
        """Cargar datos del CSV en memoria para búsquedas rápidas"""
        try:
            if not self.CSV_FILE_PATH.exists():
                logger.warning(f"CSV file not found: {self.CSV_FILE_PATH}")
                return

            self._csv_data = {}
            with open(self.CSV_FILE_PATH, 'r', encoding='iso-8859-1') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    rnc = row.get('RNC', '').strip()
                    if rnc:
                        self._csv_data[rnc] = {
                            'rnc': rnc,
                            'nombre': row.get('RAZÓN SOCIAL', '').strip(),
                            'actividad_economica': row.get('ACTIVIDAD ECONÓMICA', '').strip(),
                            'fecha_inicio': row.get('FECHA DE INICIO OPERACIONES', '').strip(),
                            'estado': row.get('ESTADO', '').strip(),
                            'regimen_pago': row.get('RÉGIMEN DE PAGO', '').strip(),
                            'source': 'csv'
                        }

            logger.info(f"Loaded {len(self._csv_data)} RNC records from CSV file")
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            self._csv_data = {}

    def _search_in_csv(self, rnc: str) -> Optional[Dict[str, Any]]:
        """
        Buscar RNC en el archivo CSV local

        Args:
            rnc (str): Número de RNC a buscar

        Returns:
            Optional[Dict[str, Any]]: Datos del RNC si se encuentra, None si no
        """
        if not self._csv_data:
            return None

        # Buscar con diferentes formatos del RNC
        search_variants = [
            rnc,
            rnc.replace('-', ''),
            rnc.replace(' ', ''),
            f"{rnc[:3]}-{rnc[3:10]}-{rnc[10:]}" if len(rnc) == 11 else rnc,
        ]

        for variant in search_variants:
            if variant in self._csv_data:
                return self._csv_data[variant]

        return None

    async def consultar_rnc(self, rnc: str) -> Dict[str, Any]:
        """
        Consultar RNC - primero en CSV local, luego en la web

        Args:
            rnc (str): Número de RNC a consultar

        Returns:
            Dict[str, Any]: Datos del RNC consultado

        Raises:
            HTTPException: Si hay error en la consulta
        """
        # Paso 1: Buscar en CSV local
        csv_result = self._search_in_csv(rnc)
        if csv_result:
            logger.info(f"RNC {rnc} found in CSV file")
            return csv_result

        # Paso 2: Si no está en CSV, buscar en la web
        logger.info(f"RNC {rnc} not found in CSV, searching on web...")
        return await self._consultar_rnc_web(rnc)

    async def _consultar_rnc_web(self, rnc: str) -> Dict[str, Any]:
        """
        Consultar RNC en la DGII web

        Args:
            rnc (str): Número de RNC a consultar

        Returns:
            Dict[str, Any]: Datos del RNC consultado

        Raises:
            HTTPException: Si hay error en la consulta
        """
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            try:
                get_response = await client.get(self.BASE_URL)
                logger.info(f"DGII GET response status: {get_response.status_code}")

                if get_response.status_code == 403:
                    raise HTTPException(
                        status_code=503,
                        detail="El sitio web de la DGII no está disponible temporalmente. Por favor, intente más tarde."
                    )

                if get_response.status_code != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"No se pudo acceder a la DGII. Status: {get_response.status_code}"
                    )

                soup = BeautifulSoup(get_response.text, "html.parser")
                viewstate = soup.find(id="__VIEWSTATE")
                eventvalidation = soup.find(id="__EVENTVALIDATION")
                viewstategenerator = soup.find(id="__VIEWSTATEGENERATOR")

                if not viewstate or not eventvalidation or not viewstategenerator:
                    raise HTTPException(
                        status_code=500,
                        detail="No se pudo obtener los tokens de la página de la DGII."
                    )

                viewstate_value = viewstate["value"]
                eventvalidation_value = eventvalidation["value"]
                viewstategenerator_value = viewstategenerator["value"]

                # Paso 2: Enviar POST con los datos y los hidden fields
                payload = {
                    "__VIEWSTATE": viewstate_value,
                    "__VIEWSTATEGENERATOR": viewstategenerator_value,
                    "__EVENTVALIDATION": eventvalidation_value,
                    "rncCedula": rnc,
                    "btnConsultar": "Buscar",
                }

                post_response = await client.post(self.BASE_URL, data=payload)
                logger.info(f"DGII POST response status: {post_response.status_code}")

                if post_response.status_code == 403:
                    raise HTTPException(
                        status_code=503,
                        detail="El sitio web de la DGII no está disponible temporalmente. Por favor, intente más tarde."
                    )

                if post_response.status_code != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error al consultar el RNC. Status: {post_response.status_code}"
                    )

                soup = BeautifulSoup(post_response.text, "html.parser")
                nombre = soup.find(id="lblNombre")
                estado = soup.find(id="lblEstado")

                if not nombre or not estado:
                    raise HTTPException(
                        status_code=404,
                        detail="No se encontraron datos para este RNC."
                    )

                return {
                    "rnc": rnc,
                    "nombre": nombre.text.strip(),
                    "estado": estado.text.strip(),
                    "source": "web"
                }

            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=504,
                    detail="Timeout al conectar con la DGII. Por favor, intente más tarde."
                )
            except httpx.ConnectError:
                raise HTTPException(
                    status_code=503,
                    detail="No se pudo conectar con la DGII. Por favor, intente más tarde."
                )
            except Exception as e:
                logger.error(f"Error inesperado consultando RNC: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error inesperado: {str(e)}"
                )


class CompanyService:
    """Servicio para operaciones de empresas"""

    def __init__(self, pool: asyncpg.Pool):
        self.db = CompanyDatabase(pool)
        self.rnc_service = RNCService()

    async def create_company(self, company_data: CompanyCreate) -> CompanyResponse:
        """Crear una nueva empresa"""
        try:
            return await self.db.create_company(company_data)
        except Exception as e:
            logger.error(f"Error creating company: {e}")
            raise HTTPException(status_code=500, detail="Error al crear la empresa")

    async def get_company_by_id(self, company_id: int) -> CompanyResponse:
        """Obtener empresa por ID"""
        company = await self.db.get_company_by_id(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
        return company

    async def get_company_by_rnc(self, rnc: str) -> CompanyResponse:
        """Obtener empresa por RNC"""
        company = await self.db.get_company_by_rnc(rnc)
        if not company:
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
        return company

    async def get_all_companies(
        self,
        page: int = 1,
        per_page: int = 50,
        search: Optional[str] = None
    ) -> CompanyListResponse:
        """Obtener todas las empresas con paginación"""
        try:
            result = await self.db.get_all_companies(page, per_page, search)
            return CompanyListResponse(**result)
        except Exception as e:
            logger.error(f"Error getting companies: {e}")
            raise HTTPException(status_code=500, detail="Error al obtener las empresas")

    async def update_company(self, company_id: int, company_data: CompanyUpdate) -> CompanyResponse:
        """Actualizar empresa"""
        try:
            company = await self.db.update_company(company_id, company_data)
            if not company:
                raise HTTPException(status_code=404, detail="Empresa no encontrada")
            return company
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating company: {e}")
            raise HTTPException(status_code=500, detail="Error al actualizar la empresa")

    async def delete_company(self, company_id: int) -> bool:
        """Eliminar empresa (soft delete)"""
        try:
            success = await self.db.delete_company(company_id)
            if not success:
                raise HTTPException(status_code=404, detail="Empresa no encontrada")
            return success
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting company: {e}")
            raise HTTPException(status_code=500, detail="Error al eliminar la empresa")

    async def search_companies_by_rnc(self, rnc: str) -> List[CompanyResponse]:
        """Buscar empresas por RNC"""
        try:
            return await self.db.search_companies_by_rnc(rnc)
        except Exception as e:
            logger.error(f"Error searching companies by RNC: {e}")
            raise HTTPException(status_code=500, detail="Error al buscar empresas")

    async def get_companies_by_type(self, company_type: str) -> List[CompanyResponse]:
        """Obtener empresas por tipo"""
        try:
            return await self.db.get_companies_by_type(company_type)
        except Exception as e:
            logger.error(f"Error getting companies by type: {e}")
            raise HTTPException(status_code=500, detail="Error al obtener empresas por tipo")

    async def consultar_rnc_con_empresa(self, rnc: str) -> Dict[str, Any]:
        """Consultar RNC y obtener información de empresa si existe en la base de datos"""
        # Primero consultar RNC
        rnc_data = await self.rnc_service.consultar_rnc(rnc)

        # Buscar si existe empresa con este RNC en la base de datos
        try:
            company = await self.db.get_company_by_rnc(rnc)
            if company:
                rnc_data['company_in_db'] = True
                rnc_data['company_data'] = company.dict()
            else:
                rnc_data['company_in_db'] = False
        except Exception as e:
            logger.warning(f"Error checking company in DB: {e}")
            rnc_data['company_in_db'] = False

        return rnc_data
