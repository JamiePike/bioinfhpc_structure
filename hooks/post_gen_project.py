import os
import shutil
from pathlib import Path

def clean_notebooks():
    """Removes unwanted notebook formats based on user selection."""
    choice = "{{ cookiecutter.notebook_type }}"
    notebook_dir = Path("docs/notebooks")
    
    keep_files = {
        "Quarto Markdown (.qmd / .md)": ["template_quarto.qmd"],
        "Jupyter Notebook (.ipynb)": ["template_jupyter.ipynb"],
        "R Markdown (.Rmd)": ["template_rmarkdown.Rmd"],
        "All / Hybrid": ["template_quarto.qmd", "template_jupyter.ipynb", "template_rmarkdown.Rmd"]
    }
    
    allowed = keep_files.get(choice, [])
    
    if choice != "All / Hybrid":
        for file in notebook_dir.iterdir():
            if file.name not in allowed and file.suffix in ['.qmd', '.ipynb', '.Rmd']:
                file.unlink()
                
        # Optional: Rename the remaining file to a generic starter file
        if choice == "Quarto Markdown (.qmd / .md)":
            os.rename(notebook_dir / "template_quarto.qmd", notebook_dir / "01_analysis.qmd")
        elif choice == "Jupyter Notebook (.ipynb)":
            os.rename(notebook_dir / "template_jupyter.ipynb", notebook_dir / "01_analysis.ipynb")
        elif choice == "R Markdown (.Rmd)":
            os.rename(notebook_dir / "template_rmarkdown.Rmd", notebook_dir / "01_analysis.Rmd")

def setup_hpc_scratch():
    """Crosses filesystems to build the scratch space and links it back."""
    scratch_base = Path("{{ cookiecutter.hpc_scratch_base }}")
    project_slug = "{{ cookiecutter.project_slug }}"
    
    # Define the isolated destination folder on scratch
    target_scratch = scratch_base / project_slug
    
    print(f"\n--- Setting up HPC Filesystem Bridge ---")
    print(f"Creating separate project scratch directory at: {target_scratch}")
    
    try:
        # Create the separate physical directories on scratch
        (target_scratch / "tmp").mkdir(parents=True, exist_ok=True)
        
        # Define the local symlink location in the home/project root
        local_symlink = Path("project_scratch")
        
        # Safeguard: if a file/folder exists where the symlink should be, remove it
        if local_symlink.exists() or local_symlink.is_symlink():
            if local_symlink.is_dir() and not local_symlink.is_symlink():
                shutil.rmtree(local_symlink)
            else:
                local_symlink.unlink()
                
        # Create the symbolic link pointing across filesystems
        os.symlink(target_scratch, local_symlink)
        print(f"Success: 'project_scratch' -> {target_scratch}")
        print(f"-----------------------------------------\n")
        
    except Exception as e:
        print(f"ERROR: Could not create scratch directories or symlink. Reason: {e}")
        print("You may need to manually link your scratch space using:")
        print(f"ln -s {target_scratch} project_scratch\n")
        
def setup_license():
    """Selects the user's preferred license and cleans up placeholders."""
    choice = "{{ cookiecutter.license_type }}"
    license_dir = Path("_licenses")
    target_license = Path("LICENSE")

    if choice == "None":
        # Delete the license folder and don't create a LICENSE file
        if license_dir.exists():
            shutil.rmtree(license_dir)
        return

    chosen_file = license_dir / f"{choice}.txt"
    
    if chosen_file.exists():
        # Move the chosen license file to the project root
        shutil.move(str(chosen_file), str(target_license))
    
    # Remove the temporary license directory entirely
    if license_dir.exists():
        shutil.rmtree(license_dir)

if __name__ == "__main__":
    clean_notebooks()
    setup_hpc_scratch()
    setup_license()  # Added to your main hook pipeline