#!/bin/bash
echo "=== ZETA BACKEND API TESTS ==="
echo "Base URL: http://20.234.16.216:8000"
echo ""

# Test 1: Health
echo "Test 1: Health Check"
start=$(date +%s%N)
response=$(timeout 5 curl -s -w "\n%{http_code}" http://20.234.16.216:8000/health 2>&1)
end=$(date +%s%N)
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | head -n -1)
elapsed=$(( (end - start) / 1000000 ))
echo "HTTP Code: $http_code | Response Time: ${elapsed}ms"
echo "Body: $body"
echo ""

# Test 2: Products search
echo "Test 2: Products Search (стул)"
start=$(date +%s%N)
response=$(timeout 5 curl -s -w "\n%{http_code}" "http://20.234.16.216:8000/products/search?query=стул&limit=10" 2>&1)
end=$(date +%s%N)
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | head -n -1)
elapsed=$(( (end - start) / 1000000 ))
echo "HTTP Code: $http_code | Response Time: ${elapsed}ms"
if [ "$http_code" = "200" ]; then
    echo "Products Found: $(echo "$body" | jq -r '. | length' 2>/dev/null || echo "N/A")"
fi
echo ""

# Test 3: Cities
echo "Test 3: Cities List"
start=$(date +%s%N)
response=$(timeout 5 curl -s -w "\n%{http_code}" http://20.234.16.216:8000/cities 2>&1)
end=$(date +%s%N)
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | head -n -1)
elapsed=$(( (end - start) / 1000000 ))
echo "HTTP Code: $http_code | Response Time: ${elapsed}ms"
if [ "$http_code" = "200" ]; then
    echo "Cities Found: $(echo "$body" | jq -r '. | length' 2>/dev/null || echo "N/A")"
fi
echo ""

# Test 4: Auth + Bot Config
echo "Test 4: Authentication + Bot Config"
start=$(date +%s%N)
token_response=$(timeout 5 curl -s -w "\n%{http_code}" -X POST http://20.234.16.216:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@zeta.local","password":"admin123"}' 2>&1)
end=$(date +%s%N)
http_code=$(echo "$token_response" | tail -1)
token_body=$(echo "$token_response" | head -n -1)
elapsed=$(( (end - start) / 1000000 ))
echo "Auth HTTP Code: $http_code | Response Time: ${elapsed}ms"

if [ "$http_code" = "200" ]; then
    TOKEN=$(echo "$token_body" | jq -r '.access_token' 2>/dev/null)
    if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
        echo "Token acquired: ${TOKEN:0:20}..."
        
        # Get bot config
        start=$(date +%s%N)
        config_response=$(timeout 5 curl -s -w "\n%{http_code}" http://20.234.16.216:8000/cities/1/bot-config \
          -H "Authorization: Bearer $TOKEN" 2>&1)
        end=$(date +%s%N)
        http_code=$(echo "$config_response" | tail -1)
        elapsed=$(( (end - start) / 1000000 ))
        echo "Bot Config HTTP Code: $http_code | Response Time: ${elapsed}ms"
    else
        echo "Failed to extract token"
    fi
else
    echo "Auth failed"
fi
echo ""

# Test 5: Analytics
echo "Test 5: Analytics (7 days)"
if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    start=$(date +%s%N)
    analytics_response=$(timeout 5 curl -s -w "\n%{http_code}" "http://20.234.16.216:8000/analytics?days=7" \
      -H "Authorization: Bearer $TOKEN" 2>&1)
    end=$(date +%s%N)
    http_code=$(echo "$analytics_response" | tail -1)
    body=$(echo "$analytics_response" | head -n -1)
    elapsed=$(( (end - start) / 1000000 ))
    echo "HTTP Code: $http_code | Response Time: ${elapsed}ms"
    if [ "$http_code" = "200" ]; then
        echo "Analytics events: $(echo "$body" | jq -r '.total_events // "N/A"' 2>/dev/null)"
    fi
else
    echo "Skipped (no token)"
fi
echo ""

echo "=== BACKEND API TESTS COMPLETE ==="
