from typing import Optional


def check_username(v: Optional[str]) -> Optional[str]:
    if v is not None:
        v = v.strip()
        if not v:
            raise ValueError("Username cannot be empty or white space only")
        if " " in v:
            raise ValueError("Username cannot contain spaces")
    return v


def check_password(v: Optional[str]) -> Optional[str]:
    if v is not None:
        v = v.strip()
        if not v:
            raise ValueError("Password cannot be empty or whitespaces only")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain atleast one number")
        return v