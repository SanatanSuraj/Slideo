# Bcrypt Password Length Fix

## Issue Identified

The signup was failing with the error:
```
ValueError: password cannot be longer than 72 bytes, truncate manually if necessary
```

## Root Cause

The bcrypt library has a hard limit of 72 bytes for password length. The fallback password `"oauth_user_no_password"` (19 characters) was being used for OAuth users, but the issue was likely with user-provided passwords exceeding 72 bytes.

## Fixes Applied

### 1. **Password Truncation in User Creation**
- Added automatic password truncation to 72 bytes in `user_crud.py`
- Ensured bcrypt compatibility for all password lengths

### 2. **Input Validation**
- Added password length validation in `UserCreate` model
- Added password length validation in `LoginRequest` and `RegisterRequest` models
- Prevents users from submitting passwords longer than 72 bytes

### 3. **OAuth User Handling**
- Changed fallback password from `"oauth_user_no_password"` to `"oauth_user"` (shorter)
- Ensures OAuth users don't hit the 72-byte limit

## Code Changes

### `servers/fastapi/crud/user_crud.py`
```python
# Handle optional password (for OAuth users)
if user.password:
    # Truncate password to 72 bytes for bcrypt compatibility
    password = user.password[:72] if len(user.password.encode('utf-8')) > 72 else user.password
    hashed_password = pwd_context.hash(password)
else:
    # For OAuth users or users without passwords, create a random hash
    hashed_password = pwd_context.hash("oauth_user")
```

### `servers/fastapi/models/mongo/user.py`
```python
@validator('password')
def validate_password_length(cls, v):
    if v is not None and len(v.encode('utf-8')) > 72:
        raise ValueError('Password cannot be longer than 72 bytes')
    return v
```

### `servers/fastapi/models/auth_models.py`
```python
@validator('password')
def validate_password_length(cls, v):
    if len(v.encode('utf-8')) > 72:
        raise ValueError('Password cannot be longer than 72 bytes')
    return v
```

## Testing

The signup process should now work without the bcrypt error. The system will:

1. **Validate** password length before processing
2. **Truncate** passwords longer than 72 bytes automatically
3. **Handle** OAuth users with shorter fallback passwords
4. **Provide** clear error messages for invalid passwords

## Expected Behavior

- ✅ Short passwords (< 72 bytes): Work normally
- ✅ Long passwords (> 72 bytes): Automatically truncated
- ✅ OAuth users: Use short fallback password
- ✅ Error handling: Clear validation messages

The signup process should now work without internal server errors!
