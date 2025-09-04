"""Tests for translator_ingest module."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from gocam_modular.translator_ingest import (
    clone_translator_ingests,
    run_make_go_cam,
    checkout_and_run_translator_ingests,
)


class TestCloneTranslatorIngests:
    """Test cases for clone_translator_ingests function."""

    @patch("subprocess.run")
    def test_clone_with_default_url(self, mock_run):
        """Test cloning with default repository URL."""
        mock_run.return_value = Mock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / "test-repo"
            result = clone_translator_ingests(target_dir=target_dir)
            
            mock_run.assert_called_once_with(
                ["git", "clone", "https://github.com/NCATSTranslator/translator-ingests.git", str(target_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
            assert result == target_dir

    @patch("subprocess.run")
    def test_clone_with_custom_url(self, mock_run):
        """Test cloning with custom repository URL."""
        mock_run.return_value = Mock()
        custom_url = "https://github.com/custom/repo.git"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / "custom-repo"
            result = clone_translator_ingests(repo_url=custom_url, target_dir=target_dir)
            
            mock_run.assert_called_once_with(
                ["git", "clone", custom_url, str(target_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
            assert result == target_dir

    @patch("subprocess.run")
    def test_clone_to_temp_directory(self, mock_run):
        """Test cloning to temporary directory when target_dir is None."""
        mock_run.return_value = Mock()
        
        result = clone_translator_ingests()
        
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0][0] == "git"
        assert args[0][1] == "clone"
        assert args[0][2] == "https://github.com/NCATSTranslator/translator-ingests.git"
        assert "translator-ingests" in str(result)

    @patch("subprocess.run")
    def test_clone_subprocess_error(self, mock_run):
        """Test that subprocess errors are propagated."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / "test-repo"
            with pytest.raises(subprocess.CalledProcessError):
                clone_translator_ingests(target_dir=target_dir)


class TestRunMakeGoCam:
    """Test cases for run_make_go_cam function."""

    def test_run_make_success(self):
        """Test successful make execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            makefile = repo_path / "Makefile"
            makefile.write_text("run:\n\techo 'Running with SOURCES=$(SOURCES)'")
            
            result = run_make_go_cam(repo_path)
            
            assert result.returncode == 0
            assert "Running with SOURCES=go_cam" in result.stdout

    def test_run_make_nonexistent_repo(self):
        """Test error when repository path doesn't exist."""
        nonexistent_path = Path("/nonexistent/path")
        
        with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
            run_make_go_cam(nonexistent_path)

    def test_run_make_no_makefile(self):
        """Test error when Makefile doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            with pytest.raises(FileNotFoundError, match="Makefile not found"):
                run_make_go_cam(repo_path)

    @patch("subprocess.run")
    def test_run_make_subprocess_error(self, mock_run):
        """Test that subprocess errors are propagated."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "make")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            makefile = repo_path / "Makefile"
            makefile.write_text("run:\n\tfalse")  # Command that fails
            
            with pytest.raises(subprocess.CalledProcessError):
                run_make_go_cam(repo_path)


class TestCheckoutAndRunTranslatorIngests:
    """Test cases for checkout_and_run_translator_ingests function."""

    @patch("gocam_modular.translator_ingest.run_make_go_cam")
    @patch("gocam_modular.translator_ingest.clone_translator_ingests")
    def test_checkout_and_run_success(self, mock_clone, mock_run):
        """Test successful checkout and run operation."""
        mock_repo_path = Path("/tmp/test-repo")
        mock_result = Mock(returncode=0, stdout="success")
        
        mock_clone.return_value = mock_repo_path
        mock_run.return_value = mock_result
        
        repo_path, result = checkout_and_run_translator_ingests()
        
        mock_clone.assert_called_once_with(
            "https://github.com/NCATSTranslator/translator-ingests.git", None
        )
        mock_run.assert_called_once_with(mock_repo_path)
        
        assert repo_path == mock_repo_path
        assert result == mock_result

    @patch("gocam_modular.translator_ingest.run_make_go_cam")
    @patch("gocam_modular.translator_ingest.clone_translator_ingests")
    def test_checkout_and_run_with_custom_params(self, mock_clone, mock_run):
        """Test checkout and run with custom parameters."""
        custom_url = "https://github.com/custom/repo.git"
        custom_dir = Path("/custom/path")
        mock_repo_path = Path("/tmp/custom-repo")
        mock_result = Mock(returncode=0, stdout="custom success")
        
        mock_clone.return_value = mock_repo_path
        mock_run.return_value = mock_result
        
        repo_path, result = checkout_and_run_translator_ingests(
            repo_url=custom_url, target_dir=custom_dir
        )
        
        mock_clone.assert_called_once_with(custom_url, custom_dir)
        mock_run.assert_called_once_with(mock_repo_path)
        
        assert repo_path == mock_repo_path
        assert result == mock_result

    @patch("gocam_modular.translator_ingest.clone_translator_ingests")
    def test_checkout_and_run_clone_error(self, mock_clone):
        """Test error handling when clone fails."""
        mock_clone.side_effect = subprocess.CalledProcessError(1, "git")
        
        with pytest.raises(subprocess.CalledProcessError):
            checkout_and_run_translator_ingests()

    @patch("gocam_modular.translator_ingest.run_make_go_cam")
    @patch("gocam_modular.translator_ingest.clone_translator_ingests")
    def test_checkout_and_run_make_error(self, mock_clone, mock_run):
        """Test error handling when make fails."""
        mock_repo_path = Path("/tmp/test-repo")
        mock_clone.return_value = mock_repo_path
        mock_run.side_effect = subprocess.CalledProcessError(1, "make")
        
        with pytest.raises(subprocess.CalledProcessError):
            checkout_and_run_translator_ingests()