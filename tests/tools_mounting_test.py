# Copyright 2026 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Integration tests for dynamic tool mounting and namespacing based on configuration."""

import unittest
from unittest.mock import patch
from fastmcp import FastMCP
from ads_mcp.coordinator import initialize_and_mount_tools
from ads_mcp.config import ToolsConfig


class TestToolsMounting(unittest.IsolatedAsyncioTestCase):
    """Verifies that tools are mounted and namespaced according to ToolsConfig."""

    @patch("ads_mcp.config.ToolsConfig.load")
    async def test_mounting_all_enabled_default_prefixes(self, mock_load):
        """Tests mounting with all categories enabled and default namespace prefixes."""
        # Mock config to enable everything with defaults
        mock_load.return_value = ToolsConfig(
            {
                "namespaces": {
                    "customers": True,
                    "search": True,
                    "metadata": True,
                }
            }
        )

        parent = FastMCP("Test Parent")
        initialize_and_mount_tools(parent)

        tools = await parent.list_tools()
        tool_names = [t.name for t in tools]

        # Expected tools with default prefixes
        self.assertIn("customers_list_accessible_customers", tool_names)
        self.assertIn("search_search", tool_names)
        self.assertIn("metadata_get_resource_metadata", tool_names)

    @patch("ads_mcp.config.ToolsConfig.load")
    async def test_mounting_disabled_namespaces(self, mock_load):
        """Tests that disabled namespaces are completely excluded."""
        # Mock config: disable search and metadata
        mock_load.return_value = ToolsConfig(
            {
                "namespaces": {
                    "customers": True,
                    "search": False,
                    "metadata": False,
                }
            }
        )

        parent = FastMCP("Test Parent")
        initialize_and_mount_tools(parent)

        tools = await parent.list_tools()
        tool_names = [t.name for t in tools]

        self.assertIn("customers_list_accessible_customers", tool_names)
        self.assertNotIn("search_search", tool_names)
        self.assertNotIn("metadata_get_resource_metadata", tool_names)

    @patch("ads_mcp.config.ToolsConfig.load")
    async def test_mounting_custom_prefixes(self, mock_load):
        """Tests namespaces with custom prefixes."""
        mock_load.return_value = ToolsConfig(
            {
                "namespaces": {
                    "customers": "accounts",
                    "search": "query",
                    "metadata": "info",
                }
            }
        )

        parent = FastMCP("Test Parent")
        initialize_and_mount_tools(parent)

        tools = await parent.list_tools()
        tool_names = [t.name for t in tools]

        self.assertIn("accounts_list_accessible_customers", tool_names)
        self.assertIn("query_search", tool_names)
        self.assertIn("info_get_resource_metadata", tool_names)

    @patch("ads_mcp.config.ToolsConfig.load")
    async def test_mounting_fine_grained_tool_enablement(self, mock_load):
        """Tests disabling individual tools under an enabled namespace."""
        mock_load.return_value = ToolsConfig(
            {
                "namespaces": {
                    "customers": {
                        "enabled": True,
                        "prefix": "accounts",
                        "enabled_tools": [
                            {
                                "list_accessible_customers": False
                            }  # Explicitly disable this tool
                        ],
                    },
                    "search": True,
                }
            }
        )

        parent = FastMCP("Test Parent")
        initialize_and_mount_tools(parent)

        tools = await parent.list_tools()
        tool_names = [t.name for t in tools]

        self.assertNotIn("accounts_list_accessible_customers", tool_names)
        self.assertIn("search_search", tool_names)
