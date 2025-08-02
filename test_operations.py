#!/usr/bin/env python3
"""
Test script for GENAI Network Operations
Tests the new features and WebSocket integration
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_api_endpoints():
    """Test the main API endpoints"""
    
    print("🧪 Testing GENAI Network Operations API Endpoints")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Health Check
        print("\n1. Testing Health Check...")
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                result = await response.json()
                print(f"   ✅ Health check: {result}")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
        
        # Test 2: Get Operations
        print("\n2. Testing Get Operations...")
        try:
            async with session.get(f"{BASE_URL}/api/operations") as response:
                result = await response.json()
                print(f"   ✅ Operations list retrieved: {len(result)} operations")
        except Exception as e:
            print(f"   ❌ Get operations failed: {e}")
        
        # Test 3: Get Devices
        print("\n3. Testing Get Devices...")
        try:
            async with session.get(f"{BASE_URL}/api/devices") as response:
                result = await response.json()
                print(f"   ✅ Devices list retrieved: {len(result)} devices")
                return result  # Return devices for further testing
        except Exception as e:
            print(f"   ❌ Get devices failed: {e}")
            return []

async def test_operations_features(devices):
    """Test the GENAI operations features"""
    
    if not devices:
        print("\n⚠️  No devices available for testing operations")
        return
    
    print("\n🚀 Testing GENAI Operations Features")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Start Audit
        print("\n1. Testing Configuration Audit...")
        try:
            device_ids = [devices[0]['id']] if devices else []
            audit_data = {
                "device_ids": device_ids,
                "audit_type": "comprehensive",
                "audit_options": {}
            }
            
            async with session.post(
                f"{BASE_URL}/api/operations/audit/start",
                json=audit_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                if response.status == 200:
                    print(f"   ✅ Audit started: {result.get('audit_session_id', 'No session ID')}")
                    audit_id = result.get('audit_session_id')
                    
                    # Test audit status
                    if audit_id:
                        await asyncio.sleep(1)
                        async with session.get(f"{BASE_URL}/api/operations/audit/{audit_id}/status") as status_response:
                            status_result = await status_response.json()
                            print(f"   ✅ Audit status: {status_result.get('status', 'Unknown')}")
                else:
                    print(f"   ❌ Audit failed: {result}")
        except Exception as e:
            print(f"   ❌ Audit test failed: {e}")
        
        # Test 2: Start Troubleshooting
        print("\n2. Testing AI Troubleshooter...")
        try:
            troubleshoot_data = {
                "problem_description": "Network connectivity issues between VLANs",
                "problem_domain": "connectivity",
                "affected_devices": [devices[0]['id']] if devices else [],
                "symptoms": ["High latency", "Packet loss"]
            }
            
            async with session.post(
                f"{BASE_URL}/api/operations/troubleshoot/start",
                json=troubleshoot_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                if response.status == 200:
                    print(f"   ✅ Troubleshooting started: {result.get('session_id', 'No session ID')}")
                    print(f"   📝 Analysis: {result.get('initial_analysis', {}).get('analysis', 'No analysis')[:100]}...")
                else:
                    print(f"   ❌ Troubleshooting failed: {result}")
        except Exception as e:
            print(f"   ❌ Troubleshooting test failed: {e}")
        
        # Test 3: Create Baseline
        print("\n3. Testing Baseline Creation...")
        try:
            baseline_data = {
                "name": f"Test Baseline {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test baseline for GENAI operations",
                "device_ids": [devices[0]['id']] if devices else [],
                "baseline_type": "golden",
                "environment": "test"
            }
            
            async with session.post(
                f"{BASE_URL}/api/operations/baseline/create",
                json=baseline_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                if response.status == 200:
                    print(f"   ✅ Baseline created: {result.get('baseline_id', 'No baseline ID')}")
                    print(f"   📊 Status: {result.get('creation_status', 'Unknown')}")
                else:
                    print(f"   ❌ Baseline creation failed: {result}")
        except Exception as e:
            print(f"   ❌ Baseline test failed: {e}")

async def test_websocket():
    """Test WebSocket connectivity"""
    
    print("\n🔌 Testing WebSocket Connection")
    print("=" * 60)
    
    try:
        import websockets
        
        async with websockets.connect(f"ws://localhost:8000/ws/operations") as websocket:
            print("   ✅ WebSocket connected successfully")
            
            # Send subscription message
            subscribe_msg = {
                "type": "subscribe",
                "operation_type": "audit"
            }
            await websocket.send(json.dumps(subscribe_msg))
            print("   📡 Subscription message sent")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                message = json.loads(response)
                print(f"   ✅ Received response: {message.get('type', 'Unknown type')}")
            except asyncio.TimeoutError:
                print("   ⏰ No response received (timeout)")
                
    except ImportError:
        print("   ⚠️  websockets library not installed, skipping WebSocket test")
        print("   💡 Install with: pip install websockets")
    except Exception as e:
        print(f"   ❌ WebSocket test failed: {e}")

async def main():
    """Main test function"""
    
    print("🎯 GENAI Network Operations - Integration Test")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing against: {BASE_URL}")
    
    try:
        # Test API endpoints
        devices = await test_api_endpoints()
        
        # Test operations features
        await test_operations_features(devices)
        
        # Test WebSocket
        await test_websocket()
        
        print("\n" + "=" * 60)
        print("🎉 Test suite completed!")
        print("💡 Visit http://localhost:8000/operations to test the UI")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
