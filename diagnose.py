#!/usr/bin/env python3
"""
Quick diagnosis script to identify why bot cannot connect to Telegram API.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get('TELEGRAM_TOKEN')
print("=" * 60)
print("TELEGRAM BOT DIAGNOSTICS")
print("=" * 60)

# 1. Check token
print(f"\n1. Token Status:")
if TOKEN:
    print(f"   ✓ TOKEN found (length: {len(TOKEN)})")
    if TOKEN.startswith("8374506549:"):
        print(f"   ✓ Token format looks correct")
    else:
        print(f"   ⚠ Token prefix unexpected (should start with bot_user_id:)")
else:
    print(f"   ✗ TOKEN not found in .env")
    sys.exit(1)

# 2. Test network connectivity to Telegram
print(f"\n2. Network Connectivity Test:")
try:
    import socket
    result = socket.create_connection(("api.telegram.org", 443), timeout=5)
    result.close()
    print(f"   ✓ TCP connection to api.telegram.org:443 successful")
except socket.timeout:
    print(f"   ✗ TCP connection TIMEOUT (network/firewall issue)")
    sys.exit(1)
except socket.gaierror as e:
    print(f"   ✗ DNS resolution failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Connection error: {type(e).__name__}: {e}")
    sys.exit(1)

# 3. Test HTTP request to Telegram API
print(f"\n3. Telegram API Test (getMe):")
try:
    import httpx
    url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    with httpx.Client(timeout=10.0) as client:
        response = client.get(url)
        if response.status_code == 200:
            import json
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                bot_name = bot_info.get('first_name', 'Unknown')
                bot_username = bot_info.get('username', 'Unknown')
                print(f"   ✓ API request successful")
                print(f"   ✓ Bot Name: {bot_name}")
                print(f"   ✓ Bot Username: @{bot_username}")
            else:
                error_msg = data.get('description', 'Unknown error')
                print(f"   ✗ API returned error: {error_msg}")
                sys.exit(1)
        elif response.status_code == 401:
            print(f"   ✗ Unauthorized (401): Token is invalid or expired")
            sys.exit(1)
        else:
            print(f"   ✗ HTTP {response.status_code}: {response.text[:200]}")
            sys.exit(1)
except ImportError:
    print(f"   ⚠ httpx not installed (trying urllib instead)...")
    try:
        import urllib.request
        import json
        url = f"https://api.telegram.org/bot{TOKEN}/getMe"
        response = urllib.request.urlopen(url, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        if data.get('ok'):
            bot_info = data.get('result', {})
            bot_username = bot_info.get('username', 'Unknown')
            print(f"   ✓ API request successful (using urllib)")
            print(f"   ✓ Bot Username: @{bot_username}")
        else:
            print(f"   ✗ API error: {data.get('description')}")
            sys.exit(1)
    except Exception as e:
        print(f"   ✗ urllib request failed: {e}")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Connection error: {type(e).__name__}: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL CHECKS PASSED - Bot should be able to connect!")
print("=" * 60)
print("\nNow run: python bot.py")
print("Expected output: Bot is running...")
