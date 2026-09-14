BASE_URL="http://localhost:8000"

# 1. Register & store tokens
REGISTER_RES=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_'$(date +%s)'@example.com",
    "password": "testpassword123",
    "username": "testuser"
  }')

ACCESS_TOKEN=$(echo "$REGISTER_RES" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
REFRESH_TOKEN=$(echo "$REGISTER_RES" | grep -o '"refresh_token":"[^"]*' | cut -d'"' -f4)

echo "Access Token: $ACCESS_TOKEN"
echo "Refresh Token: $REFRESH_TOKEN"

# 2. Get current user
echo "\n--- Current User ---"
curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 3. Test protected route
echo "\n--- Protected Lessons Route ---"
curl -s -X GET "$BASE_URL/lessons" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 4. Refresh token
echo "\n--- Refresh Tokens ---"
REFRESH_RES=$(curl -s -X POST "$BASE_URL/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")
echo "$REFRESH_RES"
NEW_REFRESH_TOKEN=$(echo "$REFRESH_RES" | grep -o '"refresh_token":"[^"]*' | cut -d'"' -f4)

# 5. Logout
echo "\n--- Logout ---"
curl -s -i -X POST "$BASE_URL/auth/logout" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$NEW_REFRESH_TOKEN\"}"

