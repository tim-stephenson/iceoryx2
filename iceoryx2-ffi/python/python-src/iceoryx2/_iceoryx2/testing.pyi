from . import FileName, FilePath, NodeName, Path, ServiceName
from .config import Config

__all__ = ["create_test_directory", "generate_file_name", "generate_file_path", "generate_isolated_config", "generate_node_name", "generate_service_name", "test_directory"]

def create_test_directory() -> None:
    """
    creates a test directory to store anything
    """

def generate_file_name() -> FileName:
    """
    generate a random and unique file name
    """

def generate_file_path() -> FilePath:
    """
    generate a random and unique file path located inside the test directory
    """

def generate_isolated_config() -> Config:
    """
    generates a iceoryx2 `Config` that does not overlap with any other configuration
    """

def generate_node_name() -> NodeName:
    """
    generates a system-wide unique `NodeName`
    """

def generate_service_name() -> ServiceName:
    """
    generates a system-wide unique `ServiceName`
    """

def test_directory() -> Path:
    """
    returns the path to the test directory
    """
