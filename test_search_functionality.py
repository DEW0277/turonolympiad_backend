#!/usr/bin/env python3
"""
Simple test script to verify search functionality is working.
This script tests the API endpoints with search parameters.
"""

import asyncio
import aiohttp
import json

async def test_search_endpoints():
    """Test the search functionality on all endpoints."""
    base_url = "http://localhost:8000"
    
    # Test data - you may need to adjust these based on your actual data
    test_cases = [
        {
            "endpoint": "/api/admin/subjects",
            "params": {"search": "math", "limit": 10},
            "description": "Search subjects for 'math'"
        },
        {
            "endpoint": "/api/admin/levels",
            "params": {"subject_id": 1, "search": "basic", "limit": 10},
            "description": "Search levels for 'basic' in subject 1"
        },
        {
            "endpoint": "/api/admin/tests",
            "params": {"level_id": 1, "search": "test", "limit": 10},
            "description": "Search tests for 'test' in level 1"
        },
        {
            "endpoint": "/api/admin/questions",
            "params": {"test_id": 1, "search": "what", "limit": 10},
            "description": "Search questions for 'what' in test 1"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for test_case in test_cases:
            try:
                print(f"\n🔍 {test_case['description']}")
                print(f"   URL: {base_url}{test_case['endpoint']}")
                print(f"   Params: {test_case['params']}")
                
                async with session.get(
                    f"{base_url}{test_case['endpoint']}", 
                    params=test_case['params']
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Success: Found {data.get('total', 0)} items")
                        if data.get('items'):
                            print(f"   📝 First item: {data['items'][0].get('name', data['items'][0].get('text', 'N/A'))}")
                    else:
                        print(f"   ❌ Error: {response.status}")
                        error_text = await response.text()
                        print(f"   📄 Response: {error_text}")
                        
            except Exception as e:
                print(f"   💥 Exception: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Search Functionality")
    print("=" * 50)
    asyncio.run(test_search_endpoints())
    print("\n✨ Test completed!")