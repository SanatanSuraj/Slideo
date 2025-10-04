# MongoDB Migration Guide

This document outlines the complete migration from SQLite/SQLModel to MongoDB for the Presenton project.

## 🎯 Migration Overview

The Presenton backend has been completely migrated from SQLite/SQLModel to MongoDB, providing:

- **Unified Database**: All entities (users, presentations, slides, templates, tasks, assets) in MongoDB
- **User Authentication**: JWT-based authentication system with user management
- **Scalable Architecture**: MongoDB's horizontal scaling capabilities
- **Modern Stack**: Motor (async MongoDB driver) with Pydantic models

## 📊 Database Schema

### Collections

1. **users** - User accounts and authentication
2. **presentations** - Presentation metadata and content
3. **slides** - Individual slide data
4. **templates** - Reusable presentation templates
5. **tasks** - Async job tracking
6. **assets** - File and image metadata
7. **vectors** - Embeddings for semantic search (replaces ChromaDB)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd servers/fastapi
pip install -r requirements.txt
```

### 2. Start MongoDB

```bash
# Option 1: Local MongoDB
mongod --dbpath ./data/mongodb

# Option 2: Docker
docker run -d -p 27017:27017 --name presenton-mongodb mongo:latest
```

### 3. Configure Environment

Create `.env` file:

```env
# Database Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=presenton

# JWT Configuration
JWT_SECRET=your-jwt-secret-key-change-in-production

# LLM Configuration
LLM=openai
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o

# Other configurations...
```

### 4. Start the Server

```bash
uvicorn api.main:app --reload
```

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me` - Update current user
- `DELETE /api/v1/auth/me` - Delete current user

### Presentations
- `POST /api/v1/presentations/` - Create presentation
- `GET /api/v1/presentations/` - List user presentations
- `GET /api/v1/presentations/{id}` - Get presentation
- `PUT /api/v1/presentations/{id}` - Update presentation
- `DELETE /api/v1/presentations/{id}` - Delete presentation
- `GET /api/v1/presentations/search/` - Search presentations

### Slides
- `POST /api/v1/slides/` - Create slide
- `GET /api/v1/slides/presentation/{id}` - Get slides for presentation
- `GET /api/v1/slides/{id}` - Get slide
- `PUT /api/v1/slides/{id}` - Update slide
- `DELETE /api/v1/slides/{id}` - Delete slide

## 🏗️ Architecture Changes

### Before (SQLite + SQLModel)
```
├── services/database.py (SQLAlchemy)
├── models/sql/ (SQLModel schemas)
├── app_data/fastapi.db (SQLite file)
└── chroma/ (ChromaDB vector store)
```

### After (MongoDB)
```
├── db/mongo.py (MongoDB connection)
├── models/mongo/ (Pydantic schemas)
├── crud/ (MongoDB CRUD operations)
├── auth/ (JWT authentication)
└── api/v1/ (RESTful endpoints)
```

## 📝 Key Features

### User Management
- JWT-based authentication
- Password hashing with bcrypt
- User profiles and settings
- Account management

### Data Models
- **User**: Authentication, profile, subscription plan
- **Presentation**: Content, metadata, user ownership
- **Slide**: Individual slide data with rich content
- **Template**: Reusable presentation layouts
- **Task**: Async job tracking and status
- **Asset**: File metadata and storage info
- **Vector**: Embeddings for semantic search

### Security
- JWT tokens with expiration
- Password hashing
- User ownership validation
- CORS configuration

## 🔄 Migration Process

The migration script (`migrate_to_mongodb.py`) automatically:

1. ✅ Removes old SQLite files
2. ✅ Cleans up ChromaDB directories
3. ✅ Creates MongoDB data directories
4. ✅ Updates environment configuration
5. ✅ Sets up new project structure

## 🧪 Testing

### Test User Registration
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

### Test User Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

## 🚨 Breaking Changes

1. **Database**: SQLite → MongoDB
2. **ORM**: SQLModel → Pydantic + Motor
3. **Authentication**: Added JWT-based auth
4. **Vector Search**: ChromaDB → MongoDB vectors collection
5. **File Structure**: Reorganized models and services

## 🔧 Troubleshooting

### MongoDB Connection Issues
```bash
# Check MongoDB status
mongosh --eval "db.runCommand('ping')"

# Check connection string
echo $MONGODB_URI
```

### Authentication Issues
```bash
# Check JWT secret
echo $JWT_SECRET

# Test token validation
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/auth/me
```

## 📈 Performance Benefits

- **Scalability**: MongoDB horizontal scaling
- **Flexibility**: Schema-less document storage
- **Performance**: Indexed queries and aggregation
- **Consistency**: Single database for all entities
- **Modern**: Async/await throughout

## 🎉 Success!

Your Presenton backend is now fully migrated to MongoDB with:

- ✅ User authentication system
- ✅ Unified data storage
- ✅ RESTful API endpoints
- ✅ Modern async architecture
- ✅ Scalable database design

Happy coding! 🚀
