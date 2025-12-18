from dataclasses import dataclass


@dataclass(frozen=True)
class JsActions:
    ELEMENT_NOT_VALID = "el => !el.validity.valid"
