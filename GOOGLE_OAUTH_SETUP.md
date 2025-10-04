# Google OAuth Setup Guide

This guide explains how to set up Google OAuth authentication for Presenton.

## Prerequisites

1. A Google Cloud Console account
2. Access to create OAuth 2.0 credentials

## Step 1: Create Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API (or Google Identity API)
4. Go to "Credentials" in the left sidebar
5. Click "Create Credentials" → "OAuth 2.0 Client IDs"
6. Choose "Web application" as the application type
7. Add authorized redirect URIs:
   - `http://localhost:3000/api/auth/google/callback` (for development)
   - `https://yourdomain.com/api/auth/google/callback` (for production)
8. Save the credentials and note down:
   - Client ID
   - Client Secret

## Step 2: Configure Environment Variables

Add the following variables to your `.env` file:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
NEXTAUTH_URL=http://localhost:3000
```

For production, update `NEXTAUTH_URL` to your production domain:
```env
NEXTAUTH_URL=https://yourdomain.com
```

## Step 3: Test the Integration

1. Start your development servers:
   ```bash
   # Terminal 1 - FastAPI backend
   cd servers/fastapi
   python server.py

   # Terminal 2 - Next.js frontend
   cd servers/nextjs
   npm run dev
   ```

2. Navigate to `http://localhost:3000/auth/login`
3. Click "Continue with Google" button
4. Complete the Google OAuth flow
5. You should be redirected to the upload page upon successful authentication

## Features

- **Seamless Integration**: Google OAuth works alongside email/password authentication
- **User Creation**: New users are automatically created when signing in with Google
- **Existing Users**: Users with existing accounts can sign in with Google using the same email
- **Token Management**: JWT tokens are created and managed the same way as regular authentication
- **Persistent Sessions**: Google OAuth sessions persist across browser refreshes

## Troubleshooting

### Common Issues

1. **"Google OAuth not configured" error**
   - Ensure `GOOGLE_CLIENT_ID` is set in your environment variables

2. **Redirect URI mismatch**
   - Verify the redirect URI in Google Cloud Console matches your callback URL
   - Check that `NEXTAUTH_URL` is correctly set

3. **"Invalid client" error**
   - Double-check your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
   - Ensure the OAuth consent screen is properly configured

4. **CORS issues**
   - Make sure your FastAPI backend is running and accessible
   - Check that the `FASTAPI_BASE_URL` environment variable is correctly set

### Development vs Production

- **Development**: Use `http://localhost:3000` as your `NEXTAUTH_URL`
- **Production**: Use your actual domain (e.g., `https://presenton.ai`)

## Security Notes

- Keep your `GOOGLE_CLIENT_SECRET` secure and never commit it to version control
- Use environment variables for all sensitive configuration
- Regularly rotate your OAuth credentials
- Monitor OAuth usage in Google Cloud Console

## Next Steps

After setting up Google OAuth:

1. Test both login and signup flows
2. Verify that users can access the presentation generation features
3. Test logout functionality
4. Consider adding other OAuth providers (GitHub, Microsoft, etc.)
