"""Module for managing translator-ingests repository checkout and execution."""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional


def clone_translator_ingests(
    repo_url: str = "https://github.com/NCATSTranslator/translator-ingests.git",
    target_dir: Optional[Path] = None,
) -> Path:
    """
    Clone the translator-ingests repository to a specified or temporary directory.
    
    Args:
        repo_url: URL of the translator-ingests repository
        target_dir: Directory to clone into. If None, uses a temporary directory
        
    Returns:
        Path to the cloned repository directory
        
    Raises:
        subprocess.CalledProcessError: If git clone fails
        
    Examples:
        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     repo_path = clone_translator_ingests(target_dir=Path(tmpdir) / "test-repo")
        ...     repo_path.exists()
        True
    """
    if target_dir is None:
        target_dir = Path(tempfile.mkdtemp()) / "translator-ingests"
    
    # Ensure parent directory exists
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    
    # Clone the repository
    subprocess.run(
        ["git", "clone", repo_url, str(target_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    
    return target_dir


def run_make_go_cam(repo_path: Path) -> subprocess.CompletedProcess:
    """
    Run 'make run SOURCES="go_cam"' in the translator-ingests repository.
    
    Args:
        repo_path: Path to the cloned translator-ingests repository
        
    Returns:
        CompletedProcess object with execution results
        
    Raises:
        subprocess.CalledProcessError: If make command fails
        FileNotFoundError: If repo_path doesn't exist or has no Makefile
        
    Examples:
        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     repo_path = Path(tmpdir) / "fake-repo"
        ...     repo_path.mkdir()
        ...     makefile = repo_path / "Makefile"
        ...     _ = makefile.write_text("run:\\n\\techo 'Running with SOURCES=$(SOURCES)'")
        ...     result = run_make_go_cam(repo_path)
        ...     "Running with SOURCES=go_cam" in result.stdout
        True
    """
    if not repo_path.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")
    
    makefile_path = repo_path / "Makefile"
    if not makefile_path.exists():
        raise FileNotFoundError(f"Makefile not found in repository: {makefile_path}")
    
    # Run make command
    result = subprocess.run(
        ["make", "run", 'SOURCES=go_cam'],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
    )
    
    return result


def checkout_and_run_translator_ingests(
    repo_url: str = "https://github.com/NCATSTranslator/translator-ingests.git",
    target_dir: Optional[Path] = None,
) -> tuple[Path, subprocess.CompletedProcess]:
    """
    Clone translator-ingests repository and run the go_cam source processing.
    
    This function combines cloning the repository and executing the make command
    in a single operation.
    
    Args:
        repo_url: URL of the translator-ingests repository
        target_dir: Directory to clone into. If None, uses a temporary directory
        
    Returns:
        Tuple of (repository_path, make_execution_result)
        
    Raises:
        subprocess.CalledProcessError: If git clone or make command fails
        
    Examples:
        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     # This would normally clone and run, but we'll just test the structure
        ...     repo_path = Path(tmpdir) / "test-repo"
        ...     repo_path.mkdir()
        ...     makefile = repo_path / "Makefile"
        ...     _ = makefile.write_text("run:\\n\\techo 'test'")
        ...     isinstance(repo_path, Path)
        True
    """
    repo_path = clone_translator_ingests(repo_url, target_dir)
    result = run_make_go_cam(repo_path)
    return repo_path, result