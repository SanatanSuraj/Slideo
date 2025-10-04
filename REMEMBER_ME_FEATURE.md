# Remember Me Feature Implementation

This document explains the "Remember Me" functionality that has been added to the Presenton authentication system.

## Overview

The "Remember Me" feature allows users to stay logged in for an extended period (30 days) instead of the default short session (30 minutes). This provides a better user experience for users who frequently use the application.

## Implementation Details

### Frontend Changes

#### Login Page (`/auth/login`)
- Added "Remember me" checkbox below the password field
- Checkbox is positioned alongside a "Forgot your password?" link
- State is managed with React `useState`
- Value is sent to the backend in the login request

#### Signup Page (`/auth/signup`)
- Added "Remember me" checkbox below the confirm password field
- Same styling and behavior as login page
- Integrated with the registration flow

### Backend Changes

#### JWT Token Configuration
- **Default Session**: 30 minutes for access tokens, 7 days for refresh tokens
- **Remember Me Session**: 30 days for both access and refresh tokens
- Configurable expiration times in `jwt_handler.py`

#### API Endpoints
- Updated `/api/v1/auth/login` to accept `remember_me` parameter
- Updated `/api/v1/auth/register` to accept `remember_me` parameter
- Created new request models (`LoginRequest`, `RegisterRequest`) for proper parameter handling

### Token Expiration Logic

```python
# Default tokens (30 minutes)
if not remember_me:
    access_token_expires = 30 minutes
    refresh_token_expires = 7 days

# Remember me tokens (30 days)
if remember_me:
    access_token_expires = 30 days
    refresh_token_expires = 30 days
```

## User Experience

### Login Flow
1. User enters email and password
2. User can optionally check "Remember me"
3. If checked: User stays logged in for 30 days
4. If unchecked: User stays logged in for 30 minutes (default)

### Signup Flow
1. User fills out registration form
2. User can optionally check "Remember me"
3. Same token expiration logic applies as login

### Visual Design
- Clean, modern checkbox styling
- Consistent with existing form design
- Proper spacing and alignment
- Accessible labels and focus states

## Security Considerations

### Token Security
- JWT tokens are still secure with proper signing
- Longer expiration doesn't compromise security
- Tokens can still be revoked by logging out
- Refresh token mechanism remains intact

### User Control
- Users explicitly choose to extend their session
- Default behavior remains short sessions for security
- Users can still log out manually at any time

## Configuration

### Environment Variables
No additional environment variables are required. The feature uses existing JWT configuration.

### Customization
Token expiration times can be modified in `servers/fastapi/auth/jwt_handler.py`:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Default session
ACCESS_TOKEN_EXPIRE_DAYS_REMEMBER = 30  # Remember me session
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Default refresh
REFRESH_TOKEN_EXPIRE_DAYS_REMEMBER = 30  # Remember me refresh
```

## Testing

### Manual Testing
1. **Login with Remember Me unchecked**:
   - Login should work normally
   - Token should expire in 30 minutes
   - User should need to re-authenticate after token expires

2. **Login with Remember Me checked**:
   - Login should work normally
   - Token should expire in 30 days
   - User should stay logged in for extended period

3. **Signup with Remember Me**:
   - Same behavior as login
   - New users get extended sessions if they choose

### Automated Testing
- Unit tests can be added to verify token expiration times
- Integration tests can verify the full authentication flow
- API tests can verify the remember_me parameter handling

## Browser Compatibility

- Works with all modern browsers
- Uses standard HTML checkbox input
- No JavaScript dependencies beyond React
- Accessible with keyboard navigation

## Future Enhancements

### Potential Improvements
1. **User Preferences**: Allow users to set default remember me preference
2. **Session Management**: Add user dashboard to view active sessions
3. **Device Tracking**: Remember me per device instead of globally
4. **Security Notifications**: Email notifications for extended sessions

### Analytics
- Track remember me usage patterns
- Monitor session duration metrics
- Analyze user behavior with extended sessions

## Troubleshooting

### Common Issues
1. **Token not persisting**: Check browser localStorage settings
2. **Immediate logout**: Verify JWT secret and expiration logic
3. **API errors**: Ensure backend is running with updated code

### Debug Steps
1. Check browser developer tools for API responses
2. Verify JWT token expiration in jwt.io
3. Check backend logs for authentication errors
4. Test with both checked and unchecked remember me

## Conclusion

The Remember Me feature provides a seamless user experience while maintaining security best practices. Users can choose between convenience and security based on their preferences, with sensible defaults that prioritize security.
