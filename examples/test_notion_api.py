#!/usr/bin/env python3
"""
Example usage of the Notion API client

This demonstrates how to use notion_api.py for basic operations.
"""

import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from notion_api import NotionAPIClient, NotionAPIError


def example_fetch_page(client, page_id):
    """Example: Fetch a page and print its content"""
    print(f"\n=== Fetching page {page_id} ===")

    try:
        result = client.fetch_page(page_id)

        print(f"Title: {result['title']}")
        print(f"Parent: {result['parent_title'] or '(workspace root)'}")
        print(f"Number of blocks: {len(result['blocks'])}")
        print(f"\nContent preview (first 500 chars):")
        print("-" * 60)
        print(result['content'][:500])
        if len(result['content']) > 500:
            print("\n... (truncated)")
        print("-" * 60)

    except NotionAPIError as e:
        print(f"Error: {e}")
        if e.status_code:
            print(f"Status code: {e.status_code}")


def example_search(client, query):
    """Example: Search the workspace"""
    print(f"\n=== Searching for '{query}' ===")

    try:
        result = client.search(query)

        print(f"Found {len(result['results'])} results:")
        for item in result['results'][:10]:  # Show first 10
            print(f"  [{item['type']}] {item['title']}")
            print(f"    ID: {item['id']}")
            print(f"    URL: {item['url']}")
            print()

    except NotionAPIError as e:
        print(f"Error: {e}")


def example_create_page(client, title, content, parent_id):
    """Example: Create a new page"""
    print(f"\n=== Creating page '{title}' ===")

    try:
        result = client.create_page(title, content, parent_id)

        print(f"Success! Created page:")
        print(f"  ID: {result['id']}")
        print(f"  URL: {result['url']}")

        return result['id']

    except NotionAPIError as e:
        print(f"Error: {e}")
        return None


def example_update_page(client, page_id, content):
    """Example: Update a page"""
    print(f"\n=== Updating page {page_id} ===")

    try:
        result = client.update_page(page_id, content)

        if result['success']:
            print(f"Success! Updated page {result['id']}")

    except NotionAPIError as e:
        print(f"Error: {e}")


def main():
    """Main example runner"""

    # Get API key from environment or command line
    api_key = os.environ.get('NOTION_API_KEY')

    if not api_key and len(sys.argv) > 1:
        api_key = sys.argv[1]

    if not api_key:
        print("Usage: python test_notion_api.py <api_key>")
        print("Or set NOTION_API_KEY environment variable")
        sys.exit(1)

    # Initialize client
    print("Initializing Notion API client...")
    client = NotionAPIClient(api_key)

    # Example 1: Search
    example_search(client, "documentation")

    # Example 2: Fetch a page (you'll need a valid page ID)
    # Uncomment and provide a page ID:
    # example_fetch_page(client, "your-page-id-here")

    # Example 3: Create a page (you'll need a valid parent page ID)
    # Uncomment and provide a parent page ID:
    # markdown_content = """
# # Welcome
    #
    # This is a test page created via the API.
    #
    # ## Features
    #
    # - **Bold text**
    # - *Italic text*
    # - `Code snippets`
    #
    # ## Code Example
    #
    # ```python
    # def hello():
    #     print("Hello, Notion!")
    # ```
    #
    # > This is a quote
    #
    # ---
    #
    # That's all!
    # """
    # new_page_id = example_create_page(
    #     client,
    #     "Test Page from API",
    #     markdown_content,
    #     "your-parent-page-id-here"
    # )

    # Example 4: Update the page we just created
    # if new_page_id:
    #     updated_content = """
# # Updated Page
    #
    # This content has been updated!
    #
    # - [x] First item
    # - [ ] Second item
    # """
    #     example_update_page(client, new_page_id, updated_content)

    print("\n=== Examples complete ===")
    print("\nTo run specific examples:")
    print("1. Uncomment the example code above")
    print("2. Provide valid page IDs")
    print("3. Run the script again")


if __name__ == "__main__":
    main()
