import warnings
from typing import Dict, Any, Optional, List
from pathlib import Path
from fastapi import HTTPException

# Suprimir warning de pkg_resources deprecado
warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API")

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
            from jinja2 import Environment
            
            # Agregar filtros personalizados para formateo de texto
            def pad_filter(value: Any, width: int) -> str:
                """Pad string to specified width with spaces on the right"""
                if value is None:
                    return " " * width
                value_str = str(value).strip()
                if len(value_str) >= width:
                    return value_str[:width]
                return value_str + " " * (width - len(value_str))
            
            def center_filter(value: Any, width: int) -> str:
                """Center string in specified width"""
                if value is None:
                    return " " * width
                value_str = str(value).strip()
                if len(value_str) >= width:
                    return value_str[:width]
                padding = width - len(value_str)
                left_pad = padding // 2
                right_pad = padding - left_pad
                return " " * left_pad + value_str + " " * right_pad
            
            # Crear entorno Jinja2 con filtros personalizados
            # No usar trim_blocks/lstrip_blocks para preservar espacios en blanco en Word
            jinja_env = Environment(trim_blocks=False, lstrip_blocks=False)
            jinja_env.filters['pad'] = pad_filter
            jinja_env.filters['center'] = center_filter
            
            # Crear template y renderizar con el entorno personalizado
            doc = DocxTemplate(template_path)
            doc.render(data, jinja_env=jinja_env)
            
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
