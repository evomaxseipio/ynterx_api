from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum

class ContractType(str, Enum):
    JURIDICA = "juridica"
    FISICA_SOLTERA = "fisica_soltera"
    FISICA_CASADA = "fisica_casada"

class ContractServices(str, Enum):
    MORTGAGE = "mortgage"
    SERVICES = "services"
    LOAN = "loan"

class ContractParagraphBase(BaseModel):
    person_role: str = Field(..., min_length=1, max_length=100)
    contract_type: ContractType
    section: str = Field(..., min_length=1, max_length=100)
    order_position: Optional[int] = Field(1, ge=1)
    title: Optional[str] = Field(None, max_length=255)
    paragraph_content: str
    paragraph_variables: Optional[Dict] = None
    contract_services: ContractServices = Field("mortgage")
    is_active: bool = Field(True)

    @validator('paragraph_content')
    def content_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Paragraph content cannot be empty")
        return v.strip()

class ContractParagraphCreate(ContractParagraphBase):
    pass

class ContractParagraphUpdate(BaseModel):
    order_position: Optional[int] = Field(None, ge=1)
    title: Optional[str] = Field(None, max_length=255)
    paragraph_content: Optional[str]
    paragraph_variables: Optional[Dict] = None
    is_active: Optional[bool]

    @validator('paragraph_content')
    def content_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Paragraph content cannot be empty")
        return v.strip() if v else None

class ContractParagraphResponse(ContractParagraphBase):
    paragraph_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ContractParagraphListResponse(BaseModel):
    paragraphs: List[ContractParagraphResponse]
    total: int
