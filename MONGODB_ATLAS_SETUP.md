# MongoDB Atlas Setup Guide

## 🚀 Connecting Presenton to MongoDB Atlas

### 1. MongoDB Atlas Configuration

The project is configured to connect to MongoDB Atlas using the following connection string:

```
mongodb+srv://slido-wb:<webBuddy123>@slido.jelghs1.mongodb.net/presenton
```

### 2. Environment Variables

Create a `.env` file in the root directory with:

```env
# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://slido-wb:<webBuddy123>@slido.jelghs1.mongodb.net/presenton
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

### 8. Troubleshooting

#### SSL Certificate Issues
If you encounter SSL certificate errors, the connection is configured with:
```python
tlsAllowInvalidCertificates=True  # For development only
```

#### Authentication Errors
- Verify the username and password in the connection string
- Check MongoDB Atlas user permissions
- Ensure the database user has read/write access

#### Connection Timeouts
- Check your IP address is whitelisted in MongoDB Atlas
- Verify network connectivity
- Check firewall settings

### 9. Next Steps

1. ✅ Configure MongoDB Atlas connection
2. ✅ Set up environment variables
3. ✅ Test database connection
4. ✅ Deploy to production
5. ✅ Monitor database performance

## 🎉 Success!

Your Presenton application is now fully connected to MongoDB Atlas!
