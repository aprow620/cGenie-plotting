## Packages
import os
import tarfile
from pathlib import Path
import xarray as xr
import glob
import matplotlib.pyplot as plt
import numpy as np


##=============== Unpack Tar ===================##
#custom function to identify tar files and save into local memory and then delete temporaty file

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

#---------------------------------------------------------------------------------------------
# untar an ensemble

def untar_all_to_temp(from_folder, to_folder="temp"):
    os.makedirs(to_folder, exist_ok=True)  # Create temp directory if needed

    all_items = glob.glob(os.path.join(from_folder, "*"))  # Grab everything in from_folder

    for item_path in all_items:
        name = os.path.basename(item_path) #extracts last component of given path

        # Case 1: item is a file
        if os.path.isfile(item_path):
            if tarfile.is_tarfile(item_path):
                print(f"Extracting {name} to {to_folder}")
                try:
                    with tarfile.open(item_path, 'r:*') as tar:
                        tar.extractall(path=to_folder)
                except Exception as e:
                    print(f"Failed to extract {name}: {e}")
            else:
                print(f"Copying file {name} to {to_folder}")
                try:
                    shutil.copy2(item_path, to_folder)
                except Exception as e:
                    print(f"Failed to copy file {name}: {e}")

        # Case 2: item is a directory (not a tar file)
        elif os.path.isdir(item_path):
            print(f"Copying contents of directory {name} to {to_folder}")
            try:
                for root, dirs, files in os.walk(item_path):
                    # relative path inside the directory
                    rel_path = os.path.relpath(root, from_folder)
                    dest_dir = os.path.join(to_folder, rel_path)
        
                    os.makedirs(dest_dir, exist_ok=True)
        
                    for file in files:
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(dest_dir, file)
                        shutil.copy2(src_file, dst_file)
            except Exception as e:
                print(f"Failed to copy directory {name}: {e}")
            
#=======================
# By Alexandre Pohl

#!/usr/bin/env python
# zorder defined as an optional argument following https://linux.die.net/diveintopython/html/power_of_introspection/optional_arguments.html

def stepped_coastline_cGENIE(lon_data, lat_data, datacrs_data, topo_bathy_file,linewidthdata, zorder=40):
    # land outline... the hard part
    # for each point of the cropped area, determine if it is a coastal point and plot (or not) accordingly
    land_outline_linewidth = linewidthdata
    landseamask = np.ma.masked_where(topo_bathy_file < 0,topo_bathy_file)
    if landseamask.mask.any() != False:
        for ilon in np.arange(0,topo_bathy_file.shape[1]-1):
            for ilat in np.arange(0,topo_bathy_file.shape[0]-1):
                # is there an ocean to the East or to the West?
                if (landseamask.mask[ilat,ilon] != landseamask.mask[ilat,ilon+1]):
                        lat1 = lat_data[ilat]
                        lat2 = lat_data[ilat+1]
                        lon1 = lon_data[ilon+1]
                        lon2 = lon_data[ilon+1]
                        latpts = [lat1, lat2]; #print latpts
                        lonpts = [lon1, lon2]; #print lonpts
                        plt.plot(lonpts,latpts,'-',linewidth=land_outline_linewidth, color='k',zorder=zorder,transform=datacrs_data)
                # is there an ocean to the North or to the South?
                if (landseamask.mask[ilat,ilon] != landseamask.mask[ilat+1,ilon]):
                        lat1 = lat_data[ilat+1]
                        lat2 = lat_data[ilat+1]
                        lon1 = lon_data[ilon]
                        lon2 = lon_data[ilon+1]
                        latpts = [lat1, lat2]; #print latpts
                        lonpts = [lon1, lon2]; #print lonpts
                        plt.plot(lonpts,latpts,'-',linewidth=land_outline_linewidth, color='k',zorder=zorder,transform=datacrs_data)
        # last point / nort pole
        for ilon in np.arange(0,topo_bathy_file.shape[1]-1):
            for ilat in np.arange(topo_bathy_file.shape[0]-1, topo_bathy_file.shape[0]):
                # is there an ocean to the East or to the West?
                if (landseamask.mask[ilat,ilon] != landseamask.mask[ilat,ilon+1]):
                        lat1 = lat_data[ilat]
                        lat2 = lat_data[ilat+1]
                        lon1 = lon_data[ilon+1]
                        lon2 = lon_data[ilon+1]
                        latpts = [lat1, lat2]; #print latpts
                        lonpts = [lon1, lon2]; #print lonpts
                        plt.plot(lonpts,latpts,'-',linewidth=land_outline_linewidth, color='k',zorder=zorder,transform=datacrs_data)
        # deadling with the modulo
        for ilat in np.arange(0,topo_bathy_file.shape[0]-1):
            # is there an ocean to the East or to the West?
            if ((landseamask.mask[ilat,0] == True) != (landseamask.mask[ilat,-1])):
                    lat1 = lat_data[ilat]
                    lat2 = lat_data[ilat+1]
                    lon1 = lon_data[0]
                    lon2 = lon_data[0]
                    latpts = [lat1, lat2]; #print latpts
                    lonpts = [lon1, lon2]; #print lonpts
                    plt.plot(lonpts,latpts,'-',linewidth=land_outline_linewidth, color='k',zorder=zorder,transform=datacrs_data)
            # is there an ocean to the North or to the South?
            if (landseamask.mask[ilat,-1] != landseamask.mask[ilat+1,-1]):
                    lat1 = lat_data[ilat+1]
                    lat2 = lat_data[ilat+1]
                    lon1 = lon_data[-2]
                    lon2 = lon_data[-1]
                    latpts = [lat1, lat2]; #print latpts
                    lonpts = [lon1, lon2]; #print lonpts
                    plt.plot(lonpts,latpts,'-',linewidth=land_outline_linewidth, color='k',zorder=zorder,transform=datacrs_data)


