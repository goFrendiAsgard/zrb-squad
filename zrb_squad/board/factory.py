"""
Factory functions for creating board instances.
"""
from .file_board import FileBoard
from .any_board import AnyBoard


def create_board(file_path: str = "zrb_squad_board.json") -> AnyBoard:
    """
    Create a default file-based board.
    
    Args:
        file_path: Path to the JSON file for storage
    
    Returns:
        An instance of FileBoard
    """
    return FileBoard(file_path)