#!/bin/bash

# Test script using curl to verify question creation with 5 options
# This script tests the POST /api/admin/tests/{test_id}/questions endpoint

echo "🧪 Testing Question Creation with 5 Options using curl"
echo "======================================================"

# Configuration
BASE_URL="http://localhost:8000"
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="adminpass123"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📋 Test Configuration:"
echo "   Base URL: $BASE_URL"
echo "   Admin Email: $ADMIN_EMAIL"
echo ""

# Step 1: Login as admin
echo "🔐 Step 1: Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}" \
  -c cookies.txt \
  -w "HTTPSTATUS:%{http_code}")

HTTP_STATUS=$(echo $LOGIN_RESPONSE | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
LOGIN_BODY=$(echo $LOGIN_RESPONSE | sed -e 's/HTTPSTATUS:.*//g')

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo -e "${GREEN}✅ Login successful${NC}"
else
    echo -e "${RED}❌ Login failed with status $HTTP_STATUS${NC}"
    echo "Response: $LOGIN_BODY"
    exit 1
fi

# Step 2: Create test question with 5 options (A-E)
echo ""
echo "📝 Step 2: Creating question with 5 options (A-E)..."

# Note: Using test_id=2 as specified in the requirements
# In a real scenario, you might need to create a test first or use an existing one
TEST_ID=2

QUESTION_DATA='{
  "text": "What is the capital of France?",
  "correct_answer": "B",
  "options": [
    {"label": "A", "text": "London"},
    {"label": "B", "text": "Paris"},
    {"label": "C", "text": "Berlin"},
    {"label": "D", "text": "Madrid"},
    {"label": "E", "text": "Rome"}
  ]
}'

echo "Question data:"
echo "$QUESTION_DATA" | jq '.' 2>/dev/null || echo "$QUESTION_DATA"
echo ""

QUESTION_RESPONSE=$(curl -s -X POST "$BASE_URL/api/admin/tests/$TEST_ID/questions" \
  -H "Content-Type: application/json" \
  -d "$QUESTION_DATA" \
  -b cookies.txt \
  -w "HTTPSTATUS:%{http_code}")

HTTP_STATUS=$(echo $QUESTION_RESPONSE | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
QUESTION_BODY=$(echo $QUESTION_RESPONSE | sed -e 's/HTTPSTATUS:.*//g')

echo "Response status: $HTTP_STATUS"

if [ "$HTTP_STATUS" -eq 200 ] || [ "$HTTP_STATUS" -eq 201 ]; then
    echo -e "${GREEN}✅ SUCCESS: Question with 5 options created successfully!${NC}"
    echo "Response:"
    echo "$QUESTION_BODY" | jq '.' 2>/dev/null || echo "$QUESTION_BODY"
    
    # Check if response contains all 5 options
    OPTION_COUNT=$(echo "$QUESTION_BODY" | jq '.options | length' 2>/dev/null || echo "unknown")
    if [ "$OPTION_COUNT" = "5" ]; then
        echo -e "${GREEN}✅ All 5 options are present in the response${NC}"
    else
        echo -e "${YELLOW}⚠️  Response contains $OPTION_COUNT options (expected 5)${NC}"
    fi
    
elif [ "$HTTP_STATUS" -eq 422 ]; then
    echo -e "${RED}❌ FAILED: Got 422 error - the issue is NOT fixed${NC}"
    echo "Response:"
    echo "$QUESTION_BODY" | jq '.' 2>/dev/null || echo "$QUESTION_BODY"
    
elif [ "$HTTP_STATUS" -eq 404 ]; then
    echo -e "${YELLOW}⚠️  Test ID $TEST_ID not found. You may need to create a test first.${NC}"
    echo "Response:"
    echo "$QUESTION_BODY" | jq '.' 2>/dev/null || echo "$QUESTION_BODY"
    
else
    echo -e "${RED}❌ FAILED: Unexpected status $HTTP_STATUS${NC}"
    echo "Response:"
    echo "$QUESTION_BODY" | jq '.' 2>/dev/null || echo "$QUESTION_BODY"
fi

# Cleanup
rm -f cookies.txt

echo ""
echo "======================================================"
if [ "$HTTP_STATUS" -eq 200 ] || [ "$HTTP_STATUS" -eq 201 ]; then
    echo -e "${GREEN}🎉 Test completed successfully! The 422 error has been FIXED.${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Test failed. The 422 error may still exist.${NC}"
    exit 1
fi