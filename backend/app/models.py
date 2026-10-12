from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    StringConstraints,
    field_validator,
)

NonEmptyText = Annotated[
    StrictStr,
    StringConstraints(strip_whitespace=True, min_length=1),
]


class ScenarioRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: Annotated[StrictStr, StringConstraints(min_length=1, max_length=280)]
    year: Annotated[StrictInt, Field(ge=0, le=3000)]
    unrealismLevel: Literal["realista", "ilusionante", "descerebrado"]

    @field_validator("question", mode="before")
    @classmethod
    def trim_question(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class ScenarioResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    narrative: NonEmptyText
    consequences: Annotated[list[NonEmptyText], Field(min_length=3, max_length=5)]


class ProviderScenarioOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    narrative: NonEmptyText
    consequences: Annotated[list[NonEmptyText], Field(min_length=3, max_length=5)]