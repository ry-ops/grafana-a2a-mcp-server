"""
Example usage of the Grafana MCP Server client directly
This demonstrates how to use the GrafanaClient programmatically
"""

import asyncio
import os
from dotenv import load_dotenv
from grafana_mcp import GrafanaClient, GrafanaConfig


async def main():
    """Example usage of Grafana client"""
    # Load environment variables
    load_dotenv()

    # Create configuration
    config = GrafanaConfig(
        base_url=os.getenv("GRAFANA_URL", "http://localhost:3000"),
        api_key=os.getenv("GRAFANA_API_KEY"),
    )

    # Create client
    client = GrafanaClient(config)

    try:
        # Health check
        print("Performing health check...")
        health = await client.health_check()
        print(f"Health status: {health}")

        # Get current user
        print("\nGetting current user...")
        user = await client.get_current_user()
        print(f"Current user: {user.get('login')}")

        # List dashboards
        print("\nListing dashboards...")
        dashboards = await client.list_dashboards()
        print(f"Found {len(dashboards)} dashboards")
        for dash in dashboards[:5]:  # Show first 5
            print(f"  - {dash.get('title')} (UID: {dash.get('uid')})")

        # List datasources
        print("\nListing datasources...")
        datasources = await client.list_datasources()
        print(f"Found {len(datasources)} datasources")
        for ds in datasources:
            print(f"  - {ds.get('name')} (Type: {ds.get('type')})")

        # List folders
        print("\nListing folders...")
        folders = await client.list_folders()
        print(f"Found {len(folders)} folders")
        for folder in folders:
            print(f"  - {folder.get('title')} (UID: {folder.get('uid')})")

        # Example: Create a folder
        print("\nCreating example folder...")
        try:
            new_folder = await client.create_folder("MCP Test Folder")
            print(f"Created folder: {new_folder.get('title')}")
        except Exception as e:
            print(f"Note: {e}")

        # Example: Create an annotation
        print("\nCreating example annotation...")
        try:
            annotation = await client.create_annotation(
                text="Test annotation from MCP server",
                tags=["mcp", "test", "automation"],
            )
            print(f"Created annotation with ID: {annotation.get('id')}")
        except Exception as e:
            print(f"Note: {e}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Clean up
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
