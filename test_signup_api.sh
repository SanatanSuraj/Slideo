#!/bin/bash

# Test script for signup API endpoint
echo "🧪 Testing signup API endpoint..."

# Test data
TEST_DATA='{
  "name": "Test User",
  "email": "test@example.com",
  "password": "testpassword123",
  "remember_me": false
}'

echo "📤 Sending signup request..."
echo "Data: $TEST_DATA"

# Make the request
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "$TEST_DATA" \
  -w "\nHTTP_CODE:%{http_code}")

# Extract response body and HTTP code
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

echo "📥 Response:"
echo "$RESPONSE_BODY"
echo ""
echo "🔢 HTTP Code: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Signup test passed!"
else
    echo "❌ Signup test failed with HTTP $HTTP_CODE"
fi
