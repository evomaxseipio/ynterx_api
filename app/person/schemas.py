from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, constr

###
### Common Schemas
###

class GenderBase(BaseModel):
    gender_name: constr(min_length=1, max_length=50)
    is_active: bool = True


class GenderResponse(GenderBase):
    model_config = ConfigDict(from_attributes=True)

    gender_id: int


class MaritalStatusBase(BaseModel):
    status_name: constr(min_length=1, max_length=50)
    is_active: bool = True


class MaritalStatusResponse(MaritalStatusBase):
    model_config = ConfigDict(from_attributes=True)

    marital_status_id: int


class EducationLevelBase(BaseModel):
    level_name: constr(min_length=1, max_length=100)
    is_active: bool = True


class EducationLevelResponse(EducationLevelBase):
    model_config = ConfigDict(from_attributes=True)

    education_level_id: int


class CountryBase(BaseModel):
    country_name: constr(min_length=1, max_length=100)
    country_code: constr(min_length=2, max_length=3)
    phone_code: str | None = Field(None, max_length=5)
    is_active: bool = True


class CountryResponse(CountryBase):
    model_config = ConfigDict(from_attributes=True)

    country_id: int


###
### Person Schemas
###

class PersonBase(BaseModel):
    first_name: constr(min_length=1, max_length=255)
    last_name: constr(min_length=1, max_length=255)
    middle_name: str | None = Field(None, max_length=255)
    date_of_birth: date | None = None
    gender_id: int | None = None
    nationality_country_id: int | None = None
    marital_status_id: int | None = None
    education_level_id: int | None = None
    is_active: bool = True


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    first_name: constr(min_length=1, max_length=255) | None = None
    last_name: constr(min_length=1, max_length=255) | None = None
    middle_name: str | None = Field(None, max_length=255)
    date_of_birth: date | None = None
    gender_id: int | None = None
    nationality_country_id: int | None = None
    marital_status_id: int | None = None
    education_level_id: int | None = None
    is_active: bool | None = None


class PersonResponse(PersonBase):
    model_config = ConfigDict(from_attributes=True)

    person_id: UUID
    created_at: datetime
    updated_at: datetime
