import os
import shutil
from pathlib import Path
import re

def extract_identifier(filename):
    """Extract the identifier before .jpg from a filename, ignoring the last 5 digits."""
    match = re.search(r'(\d+)\.jpg$', filename)
    if match:
        full_id = match.group(1)
        # Return all but the last 5 digits
        if len(full_id) > 5:
            return full_id[:-5]
        return full_id
    return None

def find_matching_images(source_folder, folder1, folder2, destination_folder):
    """
    Find images in folder1 and folder2 that match the identifier in source_folder images
    (ignoring the last 5 digits) and copy all three to the destination folder.
    The order of groups is preserved based on the order of files in the source folder.
    """
    # Create destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)
    
    # Get all jpg files from the source folder in their original order
    source_files = [f for f in sorted(os.listdir(source_folder)) if f.lower().endswith('.jpg')]
    
    # Build dictionaries of files from folder1 and folder2, organized by truncated identifier
    folder1_dict = {}
    for root, _, files in os.walk(folder1):
        for file in files:
            if file.lower().endswith('.jpg'):
                truncated_id = extract_identifier(file)
                if truncated_id:
                    if truncated_id not in folder1_dict:
                        folder1_dict[truncated_id] = []
                    folder1_dict[truncated_id].append(os.path.join(root, file))
    
    folder2_dict = {}
    for root, _, files in os.walk(folder2):
        for file in files:
            if file.lower().endswith('.jpg'):
                truncated_id = extract_identifier(file)
                if truncated_id:
                    if truncated_id not in folder2_dict:
                        folder2_dict[truncated_id] = []
                    folder2_dict[truncated_id].append(os.path.join(root, file))
    
    # Process each source file, keeping track of the original order
    matches_found = 0
    for index, source_file in enumerate(source_files):
        source_path = os.path.join(source_folder, source_file)
        truncated_id = extract_identifier(source_file)
        
        if not truncated_id:
            print(f"Could not extract identifier from {source_file}")
            continue
        
        # Check if matching files exist in folder1 and folder2
        if truncated_id in folder1_dict and truncated_id in folder2_dict:
            # Since there could be multiple matches per truncated ID, we'll take the first one from each folder
            folder1_path = folder1_dict[truncated_id][0]
            folder2_path = folder2_dict[truncated_id][0]
            
            if len(folder1_dict[truncated_id]) > 1 or len(folder2_dict[truncated_id]) > 1:
                print(f"Multiple matches found for {truncated_id}, using the first one from each folder")
            
            # Get the folder names to use as identifiers in the new filenames
            source_folder_name = os.path.basename(os.path.normpath(source_folder))
            folder1_name = os.path.basename(os.path.normpath(os.path.dirname(folder1_path)))
            folder2_name = os.path.basename(os.path.normpath(os.path.dirname(folder2_path)))
            
            # Use the source file's index to ensure the groups are in the same order as the source folder
            # Format: {index:04d}_{group_position}_{folder_name}.jpg
            # The index ensures the groups stay in the same order as the source folder
            # The group_position ensures the 3 files of each group stay together
            new_source_name = f"{index:04d}_1_{source_folder_name}_{os.path.basename(source_path)}"
            new_folder1_name = f"{index:04d}_2_{folder1_name}_{os.path.basename(folder1_path)}"
            new_folder2_name = f"{index:04d}_3_{folder2_name}_{os.path.basename(folder2_path)}"
            
            # Copy all three files to the same destination folder with the new names
            shutil.copy2(source_path, os.path.join(destination_folder, new_source_name))
            shutil.copy2(folder1_path, os.path.join(destination_folder, new_folder1_name))
            shutil.copy2(folder2_path, os.path.join(destination_folder, new_folder2_name))
            
            matches_found += 1
            print(f"Matched and copied files with truncated identifier: {truncated_id}")
        else:
            print(f"No match found for truncated identifier: {truncated_id}")
    
    print(f"Total matches found and processed: {matches_found}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Find and copy matching images across folders (ignoring last 5 digits)")
    parser.add_argument("source_folder", help="Folder containing the source images")
    parser.add_argument("folder1", help="First folder to search for matching images")
    parser.add_argument("folder2", help="Second folder to search for matching images")
    parser.add_argument("destination_folder", help="Folder to save matched images")
    
    args = parser.parse_args()
    
    find_matching_images(args.source_folder, args.folder1, args.folder2, args.destination_folder)