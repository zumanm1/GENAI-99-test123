#!/bin/bash

echo "==================================="
echo "Frontend-Backend Integration Test"
echo "==================================="

echo ""
echo "1. Testing Backend Health..."
BACKEND_HEALTH=$(curl -s http://localhost:5000/health)
if echo "$BACKEND_HEALTH" | grep -q "healthy"; then
    echo "✅ Backend Health: OK"
else
    echo "❌ Backend Health: FAILED"
fi

echo ""
echo "2. Testing Frontend Accessibility..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend: OK"
else
    echo "❌ Frontend: FAILED"
fi

echo ""
echo "3. Testing API Endpoints..."
API_STATUS=$(curl -s http://localhost:5000/api/network-operations/status)
if echo "$API_STATUS" | grep -q "active"; then
    echo "✅ Network Operations API: OK"
else
    echo "❌ Network Operations API: FAILED"
fi

API_CHAT=$(curl -s http://localhost:5000/api/chat/status)
if echo "$API_CHAT" | grep -q "active"; then
    echo "✅ Chat API: OK"
else
    echo "❌ Chat API: FAILED"
fi

echo ""
echo "4. Testing Frontend Pages..."
DEVICES_PAGE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/devices)
if [ "$DEVICES_PAGE" = "200" ]; then
    echo "✅ Devices Page: OK"
else
    echo "❌ Devices Page: FAILED"
fi

GENAI_PAGE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/genai)
if [ "$GENAI_PAGE" = "200" ]; then
    echo "✅ GENAI Page: OK"
else
    echo "❌ GENAI Page: FAILED"
fi

echo ""
echo "5. Testing API Documentation..."
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/docs)
if [ "$DOCS_STATUS" = "200" ]; then
    echo "✅ API Documentation: OK"
else
    echo "❌ API Documentation: FAILED"
fi

echo ""
echo "==================================="
echo "Integration Test Complete!"
echo "==================================="
echo ""
echo "Access URLs:"
echo "Frontend Dashboard: http://localhost:8001/"
echo "Backend Health: http://localhost:5000/health"
echo "API Documentation: http://localhost:5000/docs"
echo ""
