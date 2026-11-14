#!/usr/bin/env python3
"""Pre-flight verification script to check API environment connectivity and health."""

import sys
from pathlib import Path

# Add project root and src to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "src"))

from api_framework.clients.auth_client import AuthClient
from api_framework.clients.base_client import BaseAPIClient
from api_framework.clients.health_client import HealthClient
from config.settings import get_settings


def main() -> int:
    settings = get_settings()
    print(f"=== Environment Pre-Flight Check: [{settings.environment.upper()}] ===")
    print(f"Base URL: {settings.base_url}")
    print(f"Configured Timeout: {settings.timeout}s")

    client = BaseAPIClient(base_url=settings.base_url, timeout=settings.timeout)
    health_client = HealthClient(client)
    auth_client = AuthClient(client)

    # 1. Health check
    try:
        print("1. Checking service health (/ping)... ", end="", flush=True)
        ping_resp = health_client.ping()
        if ping_resp.status_code == 201:
            print(f"SUCCESS [HTTP {ping_resp.status_code}] (Latency: {ping_resp.elapsed_seconds:.3f}s)")
        else:
            print(f"UNEXPECTED STATUS [HTTP {ping_resp.status_code}] Body: {ping_resp.text}")
    except Exception as exc:
        print(f"FAILED: {exc}")
        return 1

    # 2. Authentication check
    try:
        print("2. Checking admin authentication (/auth)... ", end="", flush=True)
        auth_resp = auth_client.create_token(
            username=settings.auth.username,
            password=settings.auth.password,
        )
        if auth_resp.status_code == 200 and "token" in auth_resp.json():
            token = auth_resp.json()["token"]
            print(f"SUCCESS [HTTP 200] (Token acquired: {token[:4]}***{token[-4:]})")
        else:
            print(f"FAILED [HTTP {auth_resp.status_code}] Body: {auth_resp.text}")
            return 1
    except Exception as exc:
        print(f"FAILED: {exc}")
        return 1

    # 3. Collection read check
    try:
        print("3. Checking booking collection access (/booking)... ", end="", flush=True)
        list_resp = client.get("/booking")
        if list_resp.status_code == 200:
            count = len(list_resp.json())
            print(f"SUCCESS [HTTP 200] (Total bookings visible: {count})")
        else:
            print(f"FAILED [HTTP {list_resp.status_code}] Body: {list_resp.text}")
            return 1
    except Exception as exc:
        print(f"FAILED: {exc}")
        return 1

    print("\n✓ Environment is ONLINE, responsive, and ready for test automation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
