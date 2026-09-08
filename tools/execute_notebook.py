from pathlib import Path
import nbformat
from nbclient import NotebookClient
root = Path(__file__).resolve().parents[1]
path = root / "preprocessing/Eksperimen_DaudHidayatRamadhan.ipynb"
notebook = nbformat.read(path, as_version=4)
NotebookClient(notebook, timeout=900, kernel_name="python3", resources={"metadata": {"path": str(root)}}).execute()
nbformat.write(notebook, path)
assert not any(output.output_type == "error" for cell in notebook.cells if cell.cell_type == "code" for output in cell.get("outputs", []))
print("Executed notebook: all cells passed")
