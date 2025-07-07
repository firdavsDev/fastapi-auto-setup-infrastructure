#!/usr/bin/env python3
import os
import subprocess
import time

import requests
from dotenv import load_dotenv

load_dotenv()

PRIMARY_SERVER = os.getenv("PRIMARY_SERVER_IP")
BACKUP_SERVER = os.getenv("BACKUP_SERVER_IP")
DOMAIN_NAME = os.getenv("DOMAIN_NAME")
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 60))
FAILOVER_TIMEOUT = int(os.getenv("FAILOVER_TIMEOUT", 600))


def check_server_health(server_ip):
    """Check if server is healthy"""
    try:
        response = requests.get(f"http://{server_ip}:8000/health", timeout=10)
        return response.status_code == 200
    except:
        return False


def trigger_failover():
    """Trigger failover to backup server"""
    print("Triggering failover to backup server...")

    # Call failover script
    subprocess.run(["/app/scripts/failover.py"], check=True)

    print("Failover completed!")


def main():
    consecutive_failures = 0
    max_failures = FAILOVER_TIMEOUT // HEALTH_CHECK_INTERVAL

    print(f"Starting health check monitoring...")
    print(f"Primary server: {PRIMARY_SERVER}")
    print(f"Backup server: {BACKUP_SERVER}")
    print(f"Check interval: {HEALTH_CHECK_INTERVAL} seconds")

    while True:
        try:
            if check_server_health(PRIMARY_SERVER):
                print(f"Primary server is healthy")
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                print(
                    f"Primary server check failed ({consecutive_failures}/{max_failures})"
                )

                if consecutive_failures >= max_failures:
                    print("Primary server is down! Initiating failover...")
                    trigger_failover()
                    break

        except Exception as e:
            print(f"Health check error: {e}")
            consecutive_failures += 1

        time.sleep(HEALTH_CHECK_INTERVAL)


if __name__ == "__main__":
    main()
