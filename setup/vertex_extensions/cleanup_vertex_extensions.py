#!/usr/bin/env python3
"""
Clean up Vertex AI Code Interpreter extensions.

Lists all Code Interpreter extensions in the project and deletes all except
the one specified by --keep-id. Use --dry-run to preview changes first.

Usage:
    uv run python setup/vertex_extensions/cleanup_vertex_extensions.py \\
        --dry-run --keep-id EXTENSION_ID

    uv run python setup/vertex_extensions/cleanup_vertex_extensions.py \\
        --keep-id EXTENSION_ID
"""

import argparse
import os
import sys
from typing import Any

# Allow running from project root: add this script's directory to sys.path so
# that "from utils import ..." resolves correctly regardless of working directory.
sys.path.insert(0, os.path.dirname(__file__))

from utils import get_access_token  # noqa: E402
from utils import get_project_id  # noqa: E402
from utils import make_api_request  # noqa: E402


def list_vertex_extensions(
    project_id: str, region: str = "us-central1"
) -> list[dict[str, Any]]:
    """List all Vertex AI extensions in the project.

    Args:
        project_id: GCP project ID.
        region: GCP region (default: us-central1).

    Returns:
        List of extension resource dicts.
    """
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    url = (
        f"https://{region}-aiplatform.googleapis.com/v1beta1"
        f"/projects/{project_id}/locations/{region}/extensions"
    )

    print(f"Listing extensions in project {project_id}...")
    response = make_api_request("GET", url, headers)

    if "error" in response:
        return []

    return response.get("extensions", [])


def filter_code_interpreter_extensions(
    extensions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Filter to only Code Interpreter extensions.

    Args:
        extensions: Full list of extension resource dicts.

    Returns:
        Subset matching Code Interpreter by displayName or description.
    """
    result = []
    for ext in extensions:
        display_name = ext.get("displayName", "").lower()
        description = ext.get("description", "").lower()
        if "code interpreter" in display_name or "code interpreter" in description:
            result.append(ext)
    return result


def delete_extension(
    project_id: str, region: str, extension_id: str, dry_run: bool = False
) -> bool:
    """Delete a specific extension.

    Args:
        project_id: GCP project ID.
        region: GCP region.
        extension_id: The numeric extension ID to delete.
        dry_run: If True, only prints what would be deleted.

    Returns:
        True on success (or dry-run), False on error.
    """
    if dry_run:
        print(f"  [DRY RUN] Would delete extension {extension_id}")
        return True

    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    url = (
        f"https://{region}-aiplatform.googleapis.com/v1beta1"
        f"/projects/{project_id}/locations/{region}/extensions/{extension_id}"
    )

    print(f"  Deleting extension {extension_id}...")
    response = make_api_request("DELETE", url, headers)

    if "error" in response:
        print(f"  FAILED to delete extension {extension_id}: {response['error']}")
        return False

    print(f"  Deleted extension {extension_id}.")
    return True


def extract_extension_id(extension_name: str) -> str:
    """Extract the numeric extension ID from a full resource name.

    Args:
        extension_name: Full resource name, e.g.
            projects/123/locations/us-central1/extensions/456789

    Returns:
        The numeric ID portion (e.g. "456789").
    """
    return extension_name.split("/")[-1]


def main() -> None:
    """List and selectively delete Code Interpreter extensions."""
    parser = argparse.ArgumentParser(
        description="Clean up Vertex AI Code Interpreter extensions"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be deleted without actually deleting",
    )
    parser.add_argument(
        "--keep-id",
        required=True,
        help="Numeric extension ID to keep (all others will be deleted)",
    )
    args = parser.parse_args()

    print("Vertex AI Extension Cleanup")
    print("=" * 50)

    if args.dry_run:
        print("DRY RUN MODE -- no actual deletions will occur")
        print()

    project_id = get_project_id()
    region = "us-central1"

    print(f"Project          : {project_id}")
    print(f"Extension to keep: {args.keep_id}")
    print()

    extensions = list_vertex_extensions(project_id, region)

    if not extensions:
        print("No extensions found.")
        return

    code_interpreter_extensions = filter_code_interpreter_extensions(extensions)

    if not code_interpreter_extensions:
        print("No Code Interpreter extensions found.")
        return

    print(f"Found {len(code_interpreter_extensions)} Code Interpreter extension(s):")
    print()

    extensions_to_delete = []
    for ext in code_interpreter_extensions:
        ext_id = extract_extension_id(ext.get("name", ""))
        display_name = ext.get("displayName", "N/A")
        if ext_id == args.keep_id:
            status = "KEEP"
        else:
            status = "WOULD DELETE" if args.dry_run else "WILL DELETE"
            extensions_to_delete.append(ext_id)
        print(f"  {ext_id}  {display_name}  [{status}]")

    if not extensions_to_delete:
        print("\nNothing to delete.")
        return

    print(f"\nTotal to delete: {len(extensions_to_delete)}")

    if args.dry_run:
        print("Re-run without --dry-run to execute the deletion.")
        return

    response = input("\nProceed with deletion? (yes/no): ").lower().strip()
    if response not in ("yes", "y"):
        print("Cancelled.")
        return

    print("\nDeleting...")
    for ext_id in extensions_to_delete:
        delete_extension(project_id, region, ext_id, dry_run=False)

    print("\nCleanup complete.")


if __name__ == "__main__":
    main()
