import os
import sys
import random
import argparse
import concurrent.futures


def secure_delete(file_path, passes=3):
    with open(file_path, "ba+") as f:
        length = f.tell()
    for _ in range(passes):
        with open(file_path, "br+") as f:
            f.seek(0)
            f.write(os.urandom(length))
    os.remove(file_path)


def clean_directory(dir_path, file_ext, num_workers, remove_subdirs=False, secure_delete_flag=False, skip_confirm=False):
    count_files = 0
    count_dirs = 0
    file_paths = []
    dir_paths = []
    
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            if not f.endswith(file_ext):
                file_paths.append(os.path.join(root, f))
                count_files += 1
        if remove_subdirs:
            for d in dirs:
                dir_paths.append(os.path.join(root, d))
                count_dirs += 1

    print(f"Target directory: {dir_path}")
    print(f"Number of files to be deleted: {count_files}")
    if remove_subdirs:
        print(f"Number of subdirectories to be deleted: {count_dirs}")

    if skip_confirm:
        print("Skipping confirmation check.")
    else:
        confirm = input("Are you sure you want to proceed with the deletion? (y/n): ")
        if confirm.lower() != 'y':
            print("Aborted.")
            return

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for file_path in file_paths:
            if secure_delete_flag:
                future = executor.submit(secure_delete, file_path)
            else:
                future = executor.submit(os.remove, file_path)
            futures.append(future)
        for dir_path in dir_paths:
            future = executor.submit(os.rmdir, dir_path)
            futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except OSError as e:
                print(f"Error deleting file/directory: {e}")

    print(f"Total {count_files} files deleted.")
    if remove_subdirs:
        print(f"Total {count_dirs} subdirectories deleted.")


# def main(args):
#     parser = argparse.ArgumentParser(description="Clean directory by removing all files except files with specified extension")
#     parser.add_argument("dir_path", type=str, help="The directory path to clean")
#     parser.add_argument("--file-ext", type=str, default=".py", help="The file extension to keep (default: .py)")
#     parser.add_argument("--num-workers", type=int, default=5, help="The number of worker threads to use (default: 5)")
#     parser.add_argument("--remove-subdirs", action="store_true", help="Remove all subdirectories in the given directory")
#     parser.add_argument("--secure-delete", action="store_true", help="Securely delete files using DoD 5220.22-M standard")
#     parser.add_argument("--skip-confirm", type=str, default="n", help="Skip confirmation check before deleting files (default: n)")
#     parsed_args = parser.parse_args(args)
#
#     if not os.path.isdir(parsed_args.dir_path):
#         print(f"Error: {parsed_args.dir_path} is not a directory.")
#         return
#     else:
#         if parsed_args.skip_confirm.lower() == 'y':
#             clean_directory(parsed_args.dir_path, parsed_args.file_ext, parsed_args.num_workers, parsed_args.remove_subdirs, parsed_args.secure_delete, skip_confirm=True)
#         else:
#             clean_directory(parsed_args.dir_path, parsed_args.file_ext, parsed_args.num_workers, parsed_args.remove_subdirs, parsed_args.secure_delete, skip_confirm=False)
#
#
# if __name__ == "__main__":
#     main(sys.argv[1:])
