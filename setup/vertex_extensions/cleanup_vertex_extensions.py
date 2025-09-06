#!/usr/bin/env python3
"""
Simple script to clean up Vertex AI Code Interpreter extensions.
"""

import argparse
import sys
from typing import Any, Dict, List

from utils import get_access_token
from utils import get_project_id
from utils import make_api_request


def list_vertex_extensions(project_id: str, region: str = "us-central1") -> List[Dict[str, Any]]:
    """List all Vertex AI extensions in the project."""
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    url = f"https://{region}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{region}/extensions"

    print(f"Listing extensions in project {project_id}...")
    response = make_api_request("GET", url, headers)

    if "error" in response:
        return []

    return response.get("extensions", [])


def filter_code_interpreter_extensions(extensions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter to only Code Interpreter extensions."""
    code_interpreter_extensions = []

    for ext in extensions:
        display_name = ext.get("displayName", "").lower()
        description = ext.get("description", "").lower()

        if "code interpreter" in display_name or "code interpreter" in description:
            code_interpreter_extensions.append(ext)

    return code_interpreter_extensions


def delete_extension(project_id: str, region: str, extension_id: str, dry_run: bool = False) -> bool:
    """Delete a specific extension."""
    if dry_run:
        print(f"[DRY RUN] Would delete extension {extension_id}")
        return True

    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    url = f"https://{region}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{region}/extensions/{extension_id}"

    print(f"Deleting extension {extension_id}...")
    response = make_api_request("DELETE", url, headers)

    if "error" in response:
        print(f"✗ Failed to delete extension {extension_id}")
        return False

    print(f"✓ Successfully deleted extension {extension_id}")
    return True


def extract_extension_id(extension_name: str) -> str:
    """Extract extension ID from the full resource name."""
    return extension_name.split("/")[-1]


def main():
    """Main function to clean up extensions."""
    parser = argparse.ArgumentParser(
        description="Clean up Vertex AI Code Interpreter extensions")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would be deleted without actually deleting")
    parser.add_argument("--keep-id", required=True,
                        help="Extension ID to keep")

    args = parser.parse_args()

    print("Vertex AI Extension Cleanup Tool")
    print("=" * 50)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No actual deletions")
        print()

    # Get project ID
    project_id = get_project_id()
    region = "us-central1"

    print(f"Project: {project_id}")
    print(f"Extension to keep: {args.keep_id}")
    print()

    # List all extensions
    extensions = list_vertex_extensions(project_id, region)

    if not extensions:
        print("No extensions found.")
        return

    # Filter for Code Interpreter extensions
    code_interpreter_extensions = filter_code_interpreter_extensions(
        extensions)

    if not code_interpreter_extensions:
        print("No Code Interpreter extensions found.")
        return

    print(
        f"Found {len(code_interpreter_extensions)} Code Interpreter extensions:")
    print()

    # Process extensions
    extensions_to_delete = []
    keep_extension_found = False

    for ext in code_interpreter_extensions:
        ext_id = extract_extension_id(ext.get("name", ""))
        display_name = ext.get("displayName", "N/A")

        print(f"ID: {ext_id} - {display_name}")

        if ext_id == args.keep_id:
            print("  Status: ✓ KEEPING")
            keep_extension_found = True
        else:
            print(
                f"  Status: ✗ {'WOULD DELETE' if args.dry_run else 'WILL DELETE'}")
            extensions_to_delete.append(ext_id)

    if not extensions_to_delete:
        print("\nNo extensions to delete.")
        return

    print(f"\nTotal to delete: {len(extensions_to_delete)}")

    if args.dry_run:
        print("\nTo actually delete, run without --dry-run")
        return

    # Confirm deletion
    response = input("\nProceed with deletion? (yes/no): ").lower().strip()

    if response not in ["yes", "y"]:
        print("Cancelled.")
        return

    # Delete extensions
    print("\nDeleting...")
    for ext_id in extensions_to_delete:
        delete_extension(project_id, region, ext_id, args.dry_run)

    print("\n✓ Cleanup completed!")


if __name__ == "__main__":
    main()
