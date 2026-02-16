import os
import json
import time
from typing import Optional
from pathlib import Path
from notion_client import Client as NotionAPI
from notion_client.errors import APIResponseError

class NotionClient:
    """Shared Notion API client for syncing markdown content"""

    def __init__(self):
        """Initialize NotionClient from environment variables only"""
        # Warn about obsolete config file
        config_path = Path(__file__).parent.parent / 'config' / 'notion_config.json'
        if config_path.exists():
            print("[Notion] ⚠️  WARNING: config/notion_config.json is no longer used")
            print("[Notion] ⚠️  Please use environment variables instead")
            print("[Notion] ⚠️  See docs/notion-migration-guide.md for help")

        # Load master switch
        self.enabled = os.environ.get('NOTION_ENABLED', 'false').lower() == 'true'

        if not self.enabled:
            self.api_key = None
            self.debug = False
            self.dry_run = False
            self.delete_duplicates = True
            self._log("Notion sync disabled (NOTION_ENABLED=false)")
            return  # Early return, skip other initialization

        # Only load these if enabled
        self.api_key = os.environ.get('NOTION_API_KEY')
        self.debug = os.environ.get('NOTION_DEBUG', 'false').lower() == 'true'
        self.dry_run = os.environ.get('NOTION_DRY_RUN', 'false').lower() == 'true'
        self.delete_duplicates = os.environ.get('NOTION_DELETE_DUPLICATES', 'true').lower() == 'true'

        # Validate API key if enabled
        if not self.api_key:
            print("[Notion] ⚠️  NOTION_ENABLED=true but NOTION_API_KEY not set")
            print("[Notion] ⚠️  Notion sync will be skipped")

    def is_available(self) -> bool:
        """Check if Notion client is properly configured"""
        # Check master switch
        if not self.enabled:
            self._log("Notion sync disabled by NOTION_ENABLED")
            return False

        # Check API key
        if not self.api_key:
            self._log("NOTION_API_KEY not configured")
            return False

        return True

    def _get_database_id(self, task_id: str) -> Optional[str]:
        """
        Get database ID for a task from environment variable.

        Args:
            task_id: Task identifier (e.g., 'tech_insights')

        Returns:
            Database ID string or None if not configured
        """
        # Check environment variable
        env_var_name = f'NOTION_DB_{task_id.upper()}'
        db_id = os.environ.get(env_var_name)

        if db_id:
            self._log(f"Using database ID from {env_var_name}")
            return db_id

        # Not found
        self._log(f"No database ID configured for {task_id} (NOTION_DB_{task_id.upper()})")
        return None

    def _get_parent_page_id(self, task_id: str) -> Optional[str]:
        """
        Get parent page ID for a task from environment variable.

        Args:
            task_id: Task identifier (e.g., 'tech_insights')

        Returns:
            Parent page ID string or None if not configured
        """
        # Check environment variable
        env_var_name = f'NOTION_PAGE_{task_id.upper()}'
        page_id = os.environ.get(env_var_name)

        if page_id:
            self._log(f"Using parent page ID from {env_var_name}")
            return page_id

        # Not found
        self._log(f"No parent page ID configured for {task_id} (NOTION_PAGE_{task_id.upper()})")
        return None

    def _log(self, message: str):
        """Print debug message if debug mode is enabled"""
        if self.debug:
            print(f"[Notion] {message}")

    def sync_markdown(self, task_id: str, markdown_content: str, date: str) -> bool:
        """
        Sync markdown content to Notion database.

        Args:
            task_id: Task identifier (e.g., 'tech_insights')
            markdown_content: Full markdown content to sync
            date: Date string in YYYY-MM-DD format

        Returns:
            bool: True if sync succeeded, False otherwise
        """
        try:
            self._log(f"Syncing {task_id} for {date}")

            # Dry run mode
            if self.dry_run:
                print(f"[Notion] DRY RUN: Would sync {task_id} for {date}")
                print(f"[Notion] Content length: {len(markdown_content)} chars")
                return True

            # 1. Check configuration
            database_id = self._get_database_id(task_id)
            if not database_id:
                print(f"[Notion] No database configured for {task_id}")
                return False

            # 2. Check API key
            if not self.api_key:
                print(f"[Notion] NOTION_API_KEY not configured")
                return False

            # 3. Detect database type (Published Markdown vs standard)
            notion = NotionAPI(auth=self.api_key)
            db_info = notion.databases.retrieve(database_id)

            # Check if it's a Published Markdown database (has data_sources)
            is_published_markdown = 'data_sources' in db_info and db_info['data_sources']

            if is_published_markdown:
                self._log("Detected Published Markdown data source")
                # Extract data source ID
                ds_id = db_info['data_sources'][0]['id'].replace('-', '')
                return self._sync_to_published_markdown(ds_id, database_id, markdown_content, date)
            else:
                self._log("Detected standard database")
                # Use standard database API
                # 3a. Delete existing entry for this date
                if self.delete_duplicates:
                    self._find_and_delete_existing(database_id, date)

                # 4a. Create new entry
                self._create_new_entry(database_id, markdown_content, date)

                print(f"[Notion] ✓ Successfully synced {task_id} for {date}")
                return True

        except Exception as e:
            print(f"[Notion] ✗ Sync failed for {task_id}: {str(e)}")
            return False

    def _find_and_delete_existing(self, database_id: str, date: str):
        """
        Find and delete existing pages matching the date.
        """
        try:
            notion = NotionAPI(auth=self.api_key)

            # Query database for pages with matching date
            response = notion.databases.query(
                database_id=database_id,
                filter={
                    "property": "Date",
                    "date": {
                        "equals": date
                    }
                }
            )

            # Delete each matching page (archive it)
            for page in response.get('results', []):
                page_id = page['id']
                # Notion API uses archived=True to delete/archive pages
                notion.pages.update(page_id, archived=True)
                self._log(f"Deleted existing page: {page_id}")

        except APIResponseError as e:
            print(f"[Notion] API error while deleting: {e}")
            raise
        except Exception as e:
            print(f"[Notion] Failed to delete existing entries: {e}")
            # Don't raise - we want to continue to creation

    def _create_new_entry(self, database_id: str, markdown_content: str, date: str):
        """
        Create a new page in Notion with the markdown content.
        """
        try:
            notion = NotionAPI(auth=self.api_key)

            # Create new page
            notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Title": {
                        "title": [
                            {
                                "text": {
                                    "content": date
                                }
                            }
                        ]
                    },
                    "Date": {
                        "date": {
                            "start": date
                        }
                    },
                    "Source": {
                        "select": {
                            "name": "github-schedule"
                        }
                    }
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": markdown_content
                                    }
                                }
                            ]
                        }
                    }
                ]
            )

            self._log(f"Created new page for {date}")

        except APIResponseError as e:
            print(f"[Notion] API error while creating page: {e}")
            raise
        except Exception as e:
            print(f"[Notion] Failed to create new entry: {e}")
            raise

    def _create_sub_page(self, parent_page_id: str, markdown_content: str, date: str) -> bool:
        """
        Create a new page under a parent page with markdown content.

        Args:
            parent_page_id: ID of the parent page
            markdown_content: Full markdown content
            date: Date string for page title

        Returns:
            bool: True if successful

        Raises:
            Exception: If API call fails (except in dry run)
        """
        # Dry run mode
        if self.dry_run:
            print(f"[Notion] DRY RUN: Would create sub-page '{date}' under parent {parent_page_id}")
            print(f"[Notion] Content length: {len(markdown_content)} chars")
            return True

        try:
            notion = NotionAPI(auth=self.api_key)

            # Create new page under parent
            notion.pages.create(
                parent={"page_id": parent_page_id},
                properties={
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": date
                                }
                            }
                        ]
                    }
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": markdown_content
                                    }
                                }
                            ]
                        }
                    }
                ]
            )

            self._log(f"Created sub-page '{date}' under parent {parent_page_id}")
            return True

        except APIResponseError as e:
            print(f"[Notion] API error while creating sub-page: {e}")
            raise
        except Exception as e:
            print(f"[Notion] Failed to create sub-page: {e}")
            raise

    def _delete_existing_sub_pages(self, parent_page_id: str, date: str):
        """
        Find and delete existing child pages with matching date title.

        Args:
            parent_page_id: ID of the parent page
            date: Date string to match in page titles

        Returns:
            None
        """
        # Dry run mode
        if self.dry_run:
            print(f"[Notion] DRY RUN: Would delete existing sub-pages '{date}' under parent {parent_page_id}")
            return

        try:
            notion = NotionAPI(auth=self.api_key)

            # Search for child pages with matching title
            # Note: Notion search API doesn't support filtering by parent directly
            # We'll search by title and verify parent in results
            response = notion.pages.search(
                query=date,
                filter={
                    "property": "object",
                    "value": "page"
                }
            )

            # Filter results to only pages under our parent
            child_pages = []
            for page in response.get('results', []):
                page_id = page['id']
                # Check if this page is a child of our parent
                # The parent info is in page['parent']
                if page.get('parent', {}).get('page_id') == parent_page_id:
                    # Also verify the title matches
                    title = page['properties']['Name']['title'][0]['text']['content']
                    if title == date:
                        child_pages.append(page)

            # Delete each matching page (archive it)
            for page in child_pages:
                page_id = page['id']
                notion.pages.update(page_id, archived=True)
                self._log(f"Deleted existing sub-page: {page_id}")

        except APIResponseError as e:
            print(f"[Notion] API error while deleting sub-pages: {e}")
            # Don't raise - we want to continue to creation
        except Exception as e:
            print(f"[Notion] Failed to delete existing sub-pages: {e}")
            # Don't raise - we want to continue to creation

    def _sync_to_published_markdown(self, data_source_id: str, database_id: str, markdown_content: str, date: str):
        """
        Sync content to a Published Markdown data source.
        Published Markdown databases use different property types and APIs.
        """
        try:
            notion = NotionAPI(auth=self.api_key)

            # 1. Delete existing entry for this date
            if self.delete_duplicates:
                self._find_and_delete_in_published_markdown(data_source_id, date)

            # 2. Create new entry in Published Markdown format
            # Published Markdown uses rich_text for Title and Source, not title/select
            notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": date
                                }
                            }
                        ]
                    },
                    "Title": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": date
                                }
                            }
                        ]
                    },
                    "Date": {
                        "date": {
                            "start": date
                        }
                    },
                    "Source": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "github-schedule"
                                }
                            }
                        ]
                    }
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": markdown_content
                                    }
                                }
                            ]
                        }
                    }
                ]
            )

            print(f"[Notion] ✓ Successfully synced to Published Markdown for {date}")
            return True

        except APIResponseError as e:
            print(f"[Notion] API error while syncing to Published Markdown: {e}")
            raise
        except Exception as e:
            print(f"[Notion] Failed to sync to Published Markdown: {e}")
            raise

    def _find_and_delete_in_published_markdown(self, data_source_id: str, date: str):
        """
        Find and delete existing pages in a Published Markdown data source.
        """
        try:
            notion = NotionAPI(auth=self.api_key)

            # Query the data source for pages with matching date
            response = notion.data_sources.query(
                data_source_id=data_source_id,
                filter={
                    "property": "Date",
                    "date": {
                        "equals": date
                    }
                }
            )

            # Delete each matching page (archive it)
            for page in response.get('results', []):
                page_id = page['id']
                # Notion API uses archived=True to delete/archive pages
                notion.pages.update(page_id, archived=True)
                self._log(f"Deleted existing page from Published Markdown: {page_id}")

        except APIResponseError as e:
            print(f"[Notion] API error while deleting from Published Markdown: {e}")
            raise
        except Exception as e:
            print(f"[Notion] Failed to delete existing entries from Published Markdown: {e}")
            # Don't raise - we want to continue to creation

