from typing import Dict, Any, Optional, List
from pathlib import Path
from fastapi import HTTPException
from docxtpl import DocxTemplate


class ContractTemplateService:
    """Servicio para manejo de plantillas de contratos"""
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
    
    def select_template(self, data: Dict[str, Any]) -> Path:
        """Seleccionar plantilla apropiada"""
        # Determinar tipo de contrato
        if "loan" in data or data.get("contract_type") == "mortgage":
            template_name = "mortgage_template.docx"
        else:
            template_name = data.get("template_name", "default_template.docx")

        template_path = self.template_dir / template_name

        # Si no existe la plantilla específica, usar la primera disponible
        if not template_path.exists():
            available_templates = list(self.template_dir.glob("*.docx"))
            if not available_templates:
                raise HTTPException(404, "No se encontraron plantillas disponibles")
            template_path = available_templates[0]

        return template_path
    
    def render_template(self, template_path: Path, data: Dict[str, Any]) -> bytes:
        """Renderizar plantilla con datos"""
        try:
            doc = DocxTemplate(template_path)
            doc.render(data)
            
            # Guardar en bytes
            from io import BytesIO
            output = BytesIO()
            doc.save(output)
            output.seek(0)
            
            return output.getvalue()
        except Exception as e:
            raise HTTPException(400, f"Error renderizando plantilla: {str(e)}")
    
    def validate_template_data(self, data: Dict[str, Any]) -> List[str]:
        """Validar datos para la plantilla"""
        errors = []
        
        # Validaciones básicas
        if not data.get("contract_type"):
            errors.append("contract_type es requerido")
        
        if not data.get("contract_number"):
            errors.append("contract_number es requerido")
        
        # Validar que existan participantes mínimos
        if not data.get("clients") and not data.get("investors"):
            errors.append("Se requiere al menos un cliente o inversionista")
        
        return errors
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Obtener lista de plantillas disponibles"""
        templates = []
        
        if not self.template_dir.exists():
            return templates
        
        for template_file in self.template_dir.glob("*.docx"):
            templates.append({
                "name": template_file.name,
                "path": str(template_file),
                "size": template_file.stat().st_size,
                "modified": template_file.stat().st_mtime
            })
        
        return templates
    
    def template_exists(self, template_name: str) -> bool:
        """Verificar si existe una plantilla específica"""
        template_path = self.template_dir / template_name
        return template_path.exists()
