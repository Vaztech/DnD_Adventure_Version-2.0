import os

def get_project_root():
    """
    Returns the absolute path to the project root directory (C:/Users/Vaz/Desktop/dnd_adventure).
    Walks up the directory tree from the location of this file to find the top-most 'dnd_adventure' directory.
    """
    current_dir = os.path.abspath(os.path.dirname(__file__))
    dnd_adventure_dirs = []
    
    while current_dir != os.path.dirname(current_dir):  # Stop at the root directory
        if os.path.basename(current_dir) == "dnd_adventure":
            dnd_adventure_dirs.append(current_dir)
        current_dir = os.path.dirname(current_dir)
    
    if not dnd_adventure_dirs:
        raise RuntimeError("Could not find project root directory 'dnd_adventure'.")
    
    # Return the top-most 'dnd_adventure' directory (closest to filesystem root, last in the list)
    return dnd_adventure_dirs[-1]

def get_resource_path(filename: str) -> str:
    """
    Returns the absolute path to a resource file in the resources/ directory.
    Args:
        filename: Name of the resource file (e.g., 'graphics.json').
    Returns:
        Absolute path to the resource file.
    """
    project_root = get_project_root()
    resource_path = os.path.join(project_root, "resources", filename)
    if not os.path.exists(resource_path):
        raise FileNotFoundError(
            f"Resource file '{filename}' not found at '{resource_path}'. "
            "Please ensure it exists in the resources/ directory."
        )
    return resource_path