#!/usr/bin/env python3
import os
import subprocess
import time

import requests
from dotenv import load_dotenv

load_dotenv()


def update_dns_record():
    """Update DNS record to point to backup server"""
    backup_server_ip = os.getenv("BACKUP_SERVER_IP")
    domain_name = os.getenv("DOMAIN_NAME")

    # Using Cloudflare API (you'll need to add your API credentials)
    cloudflare_api_key = os.getenv("CLOUDFLARE_API_KEY")
    cloudflare_email = os.getenv("CLOUDFLARE_EMAIL")
    zone_id = os.getenv("CLOUDFLARE_ZONE_ID")

    if not all([cloudflare_api_key, cloudflare_email, zone_id]):
        print("Cloudflare credentials not configured, skipping DNS update")
        return

    headers = {
        "X-Auth-Email": cloudflare_email,
        "X-Auth-Key": cloudflare_api_key,
        "Content-Type": "application/json",
    }

    # Get DNS record ID
    response = requests.get(
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
        headers=headers,
        params={"name": domain_name},
    )

    if response.status_code == 200:
        records = response.json()["result"]
        if records:
            record_id = records[0]["id"]

            # Update DNS record
            update_data = {
                "type": "A",
                "name": domain_name,
                "content": backup_server_ip,
                "ttl": 300,
            }

            response = requests.put(
                f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}",
                headers=headers,
                json=update_data,
            )

            if response.status_code == 200:
                print(f"DNS updated successfully to point to {backup_server_ip}")
            else:
                print(f"Failed to update DNS: {response.text}")


def start_backup_server():
    """Start the backup server"""
    print("Starting backup server...")

    # SSH to backup server and start services
    backup_server_ip = os.getenv("BACKUP_SERVER_IP")

    # Run restore script first
    subprocess.run(
        ["ssh", f"root@{backup_server_ip}", "cd /app && ./scripts/restore.sh"],
        check=True,
    )

    # Start the application
    subprocess.run(
        ["ssh", f"root@{backup_server_ip}", "cd /app && docker-compose up -d"],
        check=True,
    )

    print("Backup server started successfully!")


def main():
    print("Starting failover process...")

    # Step 1: Start backup server
    start_backup_server()

    # Step 2: Wait for backup server to be ready
    backup_server_ip = os.getenv("BACKUP_SERVER_IP")
    max_retries = 30
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = requests.get(
                f"http://{backup_server_ip}:8000/health", timeout=10
            )
            if response.status_code == 200:
                print("Backup server is healthy!")
                break
        except:
            pass

        retry_count += 1
        time.sleep(10)

    if retry_count >= max_retries:
        print("Backup server failed to start properly!")
        return

    # Step 3: Update DNS
    update_dns_record()

    print("Failover completed successfully!")


if __name__ == "__main__":
    main()
