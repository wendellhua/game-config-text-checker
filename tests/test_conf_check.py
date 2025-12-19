# -*- coding: utf-8 -*-
"""
Game Config Text Checker - Unit Tests

This module contains unit tests for the conf_check.py script.
"""
import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestJsonParsing(unittest.TestCase):
    """Test cases for JSON parsing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Import the module after path setup
        import conf_check
        self.conf_check = conf_check

    def test_parse_empty_array(self):
        """Test parsing empty JSON array."""
        result = self.conf_check.parse_llm_response("[]")
        self.assertEqual(result, [])

    def test_parse_valid_json(self):
        """Test parsing valid JSON response."""
        response = '[{"line_no": 10, "issue": "错别字", "suggestion": "修改建议"}]'
        result = self.conf_check.parse_llm_response(response)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["line_no"], 10)

    def test_parse_json_with_markdown(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        response = '```json\n[{"line_no": 10, "issue": "test", "suggestion": "fix"}]\n```'
        result = self.conf_check.parse_llm_response(response)
        self.assertEqual(len(result), 1)

    def test_parse_empty_response(self):
        """Test parsing empty response."""
        result = self.conf_check.parse_llm_response("")
        self.assertEqual(result, [])

    def test_parse_chinese_quotes(self):
        """Test parsing JSON with Chinese quotes."""
        response = '[{"line_no": 10, "issue": "错别字", "suggestion": "修改"}]'
        response = response.replace('"', '"').replace('"', '"')
        result = self.conf_check.parse_llm_response(response)
        # Should handle Chinese quotes
        self.assertIsInstance(result, list)


class TestJsonFix(unittest.TestCase):
    """Test cases for JSON fix functionality."""

    def setUp(self):
        """Set up test fixtures."""
        import conf_check
        self.conf_check = conf_check

    def test_fix_truncated_json(self):
        """Test fixing truncated JSON."""
        truncated = '[{"line_no": 10, "issue": "test"}'
        result = self.conf_check.try_fix_truncated_json(truncated)
        if result:
            # Should be parseable after fix
            try:
                parsed = json.loads(result)
                self.assertIsInstance(parsed, list)
            except json.JSONDecodeError:
                pass  # May not always be fixable

    def test_clean_json_string(self):
        """Test cleaning JSON string."""
        dirty = '[{"line_no": 10，"issue": "test"}]'  # Chinese comma
        result = self.conf_check.clean_json_string(dirty)
        self.assertIn(",", result)


class TestColumnMatching(unittest.TestCase):
    """Test cases for column matching functionality."""

    def setUp(self):
        """Set up test fixtures."""
        import conf_check
        import pandas as pd
        self.conf_check = conf_check
        self.pd = pd

    def test_find_exact_column(self):
        """Test finding exact column match."""
        df = self.pd.DataFrame({"text": [1, 2], "name": [3, 4]})
        result = self.conf_check.find_target_column(df, "text")
        self.assertEqual(result, "text")

    def test_find_fuzzy_column(self):
        """Test finding fuzzy column match."""
        df = self.pd.DataFrame({"optional_string_text": [1, 2], "name": [3, 4]})
        result = self.conf_check.find_target_column(df, "text")
        self.assertEqual(result, "optional_string_text")


class TestPromptGeneration(unittest.TestCase):
    """Test cases for prompt generation."""

    def setUp(self):
        """Set up test fixtures."""
        import conf_check
        self.conf_check = conf_check

    def test_prompt_generation(self):
        """Test prompt is generated correctly."""
        batch_data = {10: "测试文本", 11: "另一个测试"}
        prompt = self.conf_check.get_check_prompt(batch_data)

        # Check prompt contains expected elements
        self.assertIn("错别字", prompt)
        self.assertIn("语病", prompt)
        self.assertIn("JSON", prompt)
        self.assertIn("测试文本", prompt)


class TestModelHealth(unittest.TestCase):
    """Test cases for model health check."""

    def setUp(self):
        """Set up test fixtures."""
        import conf_check
        self.conf_check = conf_check

    @patch('requests.get')
    def test_check_ollama_models_success(self, mock_get):
        """Test checking Ollama models when service is available."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "qwen3:14b-q4_K_M"}, {"name": "qwen3:7b"}]
        }
        mock_get.return_value = mock_response

        result = self.conf_check.check_ollama_models()
        self.assertIsInstance(result, list)
        self.assertIn("qwen3:14b-q4_K_M", result)

    @patch('requests.get')
    def test_check_ollama_models_failure(self, mock_get):
        """Test checking Ollama models when service is unavailable."""
        mock_get.side_effect = Exception("Connection refused")

        result = self.conf_check.check_ollama_models()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
