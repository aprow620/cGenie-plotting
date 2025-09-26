##=============== Unpack Tar ===================##
import os
import tarfile
from pathlib import Path
import xarray as xr

#custom function to identify tar files and save into local memory and then delete temporaty file

import os
import tarfile
import xarray as xr
from pathlib import Path

def unpak_single_tar(path, to_folder="temp"):
    """
    Open cGENIE biogem outputs from either:
      - A .tar/.tar.gz archive
      - An already-extracted folder
    Returns:
      data_2d, data_3d, path_2d, path_3d
    """
    path = Path(path)

    # Case 1: it's a tarball
    if path.is_file() and tarfile.is_tarfile(path):
        parent_dir = path.parent
        with tarfile.open(path, "r:*") as tar:
            tar.extractall(path=parent_dir)
        # after extraction, use tar's stem as folder name
        base_name = path.name
        for suffix in [".tar.gz", ".tar.bz2", ".tar.xz", ".tar"]:
            if base_name.endswith(suffix):
                base_name = base_name[: -len(suffix)]
                break
        extract_dir = parent_dir / base_name

    # Case 2: it's already an extracted folder
    elif path.is_dir():
        extract_dir = path

    else:
        raise ValueError(f"Path {path} is neither a tar archive nor a directory.")

    # Search inside for files
    found_2d, found_3d = None, None
    for root, dirs, files in os.walk(extract_dir):
        if "fields_biogem_2d.nc" in files:
            found_2d = Path(root) / "fields_biogem_2d.nc"
        if "fields_biogem_3d.nc" in files:
            found_3d = Path(root) / "fields_biogem_3d.nc"
        if found_2d and found_3d:
            break

    if not found_2d or not found_3d:
        raise FileNotFoundError("Could not locate fields_biogem_2d.nc or fields_biogem_3d.nc")

    return xr.open_dataset(found_2d), xr.open_dataset(found_3d), str(found_2d), str(found_3d)
