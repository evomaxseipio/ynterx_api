# paragraphs.py
import re
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import text

async def get_paragraph_from_db(connection: AsyncConnection, contract_type_id: int, section: str) -> str:
    query = """
        SELECT content FROM contract_paragraphs
        WHERE contract_type_id = :contract_type_id AND section = :section AND is_active = true
        ORDER BY order_position ASC
        LIMIT 1
    """
    result = await connection.execute(text(query), {
        "contract_type_id": contract_type_id,
        "section": section
    })
    row = result.first()
    return row[0] if row else ""

def process_paragraph(template: str, data: Dict[str, Any]) -> str:
    """Reemplaza los {{placeholders}} de un párrafo"""
    if not template:
        return ""
    for placeholder in re.findall(r'\{\{([^}]+)\}\}', template):
        value = str(data.get(placeholder, f"[{placeholder}]"))
        template = template.replace(f"{{{{{placeholder}}}}}", value)
    return template
