import abc

from pydantic import BaseModel, validator


class Value(abc.ABC, BaseModel):
    """Base class for all value objects."""

    class Config:  # noqa WPS431
        extra = 'forbid'  # Forbid to pass unnecessary kwargs to constructor.


class Paging(Value):
    """Used to limit/offset results returned by views."""

    limit: int
    offset: int

    @validator('limit')
    @classmethod
    def validate_max_limit(cls, limit: int) -> int:
        max_limit = 20
        if limit > max_limit:
            raise ValueError(
                "Max limit can't be greater than {0}".format(max_limit),
            )

        return limit
