# MongoDB Atlas Setup Guide

## 🚀 Connecting Presenton to MongoDB Atlas

### 1. MongoDB Atlas Configuration

The project is configured to connect to MongoDB Atlas using the following connection string format:

```
mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/presenton?retryWrites=true&w=majority
```

### 2. Environment Variables

Create a `.env` file in the root directory with:

```env
# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/presenton?retryWrites=true&w=majority
MONGODB_DATABASE=presenton

# JWT Configuration
JWT_SECRET=your-jwt-secret-key-change-in-production

# LLM Configuration
LLM=openai
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o

# Image Generation
IMAGE_PROVIDER=dall-e-3
```

### 3. Database Collections

The following collections will be created automatically:

- **users** - User accounts and authentication
- **presentations** - Presentation metadata and content
- **slides** - Individual slide data
- **templates** - Presentation templates
- **tasks** - Async task management
- **assets** - Image and file assets
- **vectors** - Embedding vectors for search
- **webhooks** - Webhook subscriptions

### 4. Testing the Connection

#### Option A: Using the FastAPI Server

```bash
cd servers/fastapi
uvicorn api.main:app --reload
```

Visit: `http://localhost:8000/api/v1/db_status/`

#### Option B: Using the Test Script

```bash
python test_mongodb_atlas.py
```

### 5. API Endpoints

All endpoints now use MongoDB Atlas:

- **Authentication**: `/api/v1/auth/`
- **Presentations**: `/api/v1/presentations/`
- **Slides**: `/api/v1/slides/`
- **Database Status**: `/api/v1/db_status/`

### 6. Security Notes

⚠️ **Important**: 
- Never commit the `.env` file to version control
- Use environment variables in production
- Rotate database credentials regularly
- Enable IP whitelisting in MongoDB Atlas

### 7. Production Deployment

For production deployment:

1. Set environment variables in your deployment platform
2. Update the MongoDB Atlas connection string
3. Configure proper SSL certificates
4. Set up database backups
5. Monitor connection limits

### 8. MongoDB Atlas Setup Steps

#### Step 1: Create Database User
1. Go to MongoDB Atlas Dashboard
2. Navigate to "Database Access" in the left sidebar
3. Click "Add New Database User"
4. Choose "Password" authentication
5. Create a username and strong password
6. Set privileges to "Read and write to any database"
7. Click "Add User"

#### Step 2: Whitelist Your IP Address
1. Go to "Network Access" in the left sidebar
2. Click "Add IP Address"
3. Choose "Add Current IP Address" or "Allow Access from Anywhere" (0.0.0.0/0)
4. Click "Confirm"

#### Step 3: Get Connection String
1. Go to "Database" in the left sidebar
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Select "Python" and version "3.6 or later"
5. Copy the connection string
6. Replace `<password>` with your database user password
7. Replace `<dbname>` with `presenton`

#### Step 4: Update Environment Variables
1. Copy `env.example` to `.env`
2. Update `MONGODB_URI` with your connection string
3. Ensure `MONGODB_DATABASE=presenton`
4. Restart the FastAPI server

### 9. Troubleshooting

#### Authentication Errors ("bad auth : authentication failed")
1. **Verify Database User Credentials:**
   - Check username and password in MongoDB Atlas
   - Ensure the user has read/write permissions
   - Verify the user is not expired or disabled

2. **Check IP Whitelist:**
   - Go to "Network Access" in MongoDB Atlas
   - Add your current IP address
   - Wait 1-2 minutes for changes to propagate

3. **Verify Database Name:**
   - Ensure the database name in the URI matches your Atlas database
   - Default database name should be `presenton`

4. **Check Connection String Format:**
   ```bash
   # Correct format:
   mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/presenton?retryWrites=true&w=majority
   
   # Common issues:
   # - Missing database name at the end
   # - Special characters in password not URL-encoded
   # - Wrong cluster name
   ```

#### SSL Certificate Issues
If you encounter SSL certificate errors, the connection is configured with:
```python
tlsAllowInvalidCertificates=True  # For development only
```

#### Connection Timeouts
- Check your IP address is whitelisted in MongoDB Atlas
- Verify network connectivity
- Check firewall settings
- Ensure MongoDB Atlas cluster is running

### 9. Next Steps

1. ✅ Configure MongoDB Atlas connection
2. ✅ Set up environment variables
3. ✅ Test database connection
4. ✅ Deploy to production
5. ✅ Monitor database performance

## 🎉 Success!

Your Presenton application is now fully connected to MongoDB Atlas!
