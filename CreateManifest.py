import configparser
import os
import hashlib
import json
import shutil
from datetime import datetime

def read_ini_config(file_path):
    """
    Read configuration from an INI file.
    
    :param file_path: Path to the INI configuration file.
    :return: A dictionary containing the configuration parameters.
    """
    config = configparser.ConfigParser()
    config.read(file_path)
    
    # Create a dictionary to store the configuration values
    config_dict = {}
    for section in config.sections():
        for key, value in config.items(section):
            config_dict[key] = value
    return config_dict


def createDictionary(directory, url):

    hasher = hashlib.sha256()
    file_list = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if "pakchunk0" not in file:
                # print(file)
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    chunk_size = 65536  # Read the file in chunks of 64KB
                    while True:
                        data = f.read(chunk_size)
                        if not data:
                            break
                        hasher.update(data)
                hash = hasher.hexdigest()
                url_file=url + str(file)
                file_list[file]= {"filename":file, "path":file_path, "hash":hash, "size":os.path.getsize(file_path), "url":url_file}
    return file_list


def list_files(directory):
    """
    List all files in a directory and its subdirectories.
    
    :param directory: The path to the directory you want to search.
    :return: A list of file paths.
    """
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    return file_list


def copy_file(source_path, destination_folder):
    # Ensure the destination folder ends with a '/' or '\' if you are using Windows paths
    if not destination_folder.endswith('/') and not destination_folder.endswith('\\'):
        destination_folder += '/'
    
    # Get the filename from the source path
    filename = os.path.basename(source_path)
    
    # Create the full destination path
    destination_path = os.path.join(destination_folder, filename)
    
    try:
        shutil.copy2(source_path, destination_path)
        # print("File copied successfully.")
    except Exception as e:
        print(f"An error occurred while copying the file: {e}")


def main():
    # read config
    config_path = "config.ini"  # Replace with your file path
    config = read_ini_config(config_path)

    # build dictionaries of current files
    url="192.168.2.200/HLVR/"
    windows_directory = config["base"] + config["windows"]    
    windows_dictionary = createDictionary(windows_directory, url)

    android_directory = config["base"] + config["android"]    
    android_dictionary = createDictionary(android_directory, url)   

    experiment_directory = config["base"] + config["experiment"]    
    experiment_dictionary = createDictionary(experiment_directory, url)
    
    windows_dictionary.update(experiment_dictionary) 
    android_dictionary.update(experiment_dictionary) 

    
    # check if manifest exists
    manifest_path = os.path.join(config["output"], "BuildManifest.json")
    keys_to_delete=[]
    # print(manifest_path)
    if os.path.exists(manifest_path):
        print("File exists.")
        try:
            os.remove(manifest_path)
            print("File deleted successfully.", manifest_path)
        except FileNotFoundError:
            print("The file does not exist.")
        except PermissionError:
            print("You do not have permission to delete this file.")
        except Exception as e:
            print(f"An error occurred while deleting the file: {e}")       

        


    manifest={}
    current_datetime = datetime.now().strftime('%d%m%Y_%H%M%S')
    manifest["version"]="2.0." + current_datetime

    manifest["android"]=android_dictionary 
    manifest["windows"]=windows_dictionary 

    for entry in manifest["android"]: 
        entry_path = os.path.join(config["output"], entry)
        if os.path.exists(entry_path):
            if os.path.getsize(entry_path) == manifest["android"][entry]["size"]:
                hasher = hashlib.sha256()
                with open(entry_path, 'rb') as f:
                    chunk_size = 65536  # Read the file in chunks of 64KB
                    while True:
                        data = f.read(chunk_size)
                        if not data:
                            break
                        hasher.update(data)
                hash = hasher.hexdigest()
                # print("hash", hash, manifest["android"][entry]["hash"], entry)
                if hash == manifest["android"][entry]["hash"]:
                    continue
                    # print("same hash")
                else:
                    # print("different hash")
                    try:
                        os.remove(entry_path)
                        print("File deleted successfully.", entry_path)
                    except FileNotFoundError:
                        print("The file does not exist.")
                    except PermissionError:
                        print("You do not have permission to delete this file.")
                    except Exception as e:
                        print(f"An error occurred while deleting the file: {e}")
                
                    copy_file(manifest["android"][entry]["path"], config["output"])

            else:
                # print("different size")
                try:
                    os.remove(entry_path)
                    print("File deleted successfully.", entry_path)
                except FileNotFoundError:
                    print("The file does not exist.")
                except PermissionError:
                    print("You do not have permission to delete this file.")
                except Exception as e:
                    print(f"An error occurred while deleting the file: {e}")
                
                copy_file(manifest["android"][entry]["path"], config["output"])
        else:
            copy_file(manifest["android"][entry]["path"], config["output"])

   
    for entry in manifest["windows"]:        
        entry_path = os.path.join(config["output"], entry)
        if os.path.exists(entry_path):
            if os.path.getsize(entry_path) == manifest["windows"][entry]["size"]:
                hasher = hashlib.sha256()

                with open(entry_path, 'rb') as f:
                    chunk_size = 65536  # Read the file in chunks of 64KB
                    while True:
                        data = f.read(chunk_size)
                        if not data:
                            break
                        hasher.update(data)
                hash = hasher.hexdigest()
                # print("hash", hash, manifest["windows"][entry]["hash"], entry)
                if hash == manifest["windows"][entry]["hash"]:
                    # print("same hash")
                    continue
                else:
                    # print("different hash")
                    try:
                        os.remove(entry_path)
                        print("File deleted successfully.", entry_path)
                    except FileNotFoundError:
                        print("The file does not exist.")
                    except PermissionError:
                        print("You do not have permission to delete this file.")
                    except Exception as e:
                        print(f"An error occurred while deleting the file: {e}")
                
                    copy_file(manifest["windows"][entry]["path"], config["output"])

            else:
                # print("different size")
                try:
                    os.remove(entry_path)
                    print("File deleted successfully.", entry_path)
                except FileNotFoundError:
                    print("The file does not exist.")
                except PermissionError:
                    print("You do not have permission to delete this file.")
                except Exception as e:
                    print(f"An error occurred while deleting the file: {e}")
                
                copy_file(manifest["windows"][entry]["path"], config["output"])
        else:
            copy_file(manifest["windows"][entry]["path"], config["output"])

    
    for entry in manifest["android"]:
        if "path" in manifest["android"][entry]:
            # print("deleted path")
            manifest["android"][entry].pop("path")     

    for entry in manifest["windows"]:
        if "path" in manifest["windows"][entry]:
            # print("deleted path")
            manifest["windows"][entry].pop("path")
    

#    cleaning up not used files
    output_dictionary = createDictionary(config["output"], url)
    for entry in output_dictionary:
        if (entry in manifest["android"]) or (entry in manifest["windows"]):
            continue
        else:
            entry_path = os.path.join(config["output"], entry)
            print("cleanup", entry)
            try:
                os.remove(entry_path)
                print("File deleted successfully.", entry_path)
            except FileNotFoundError:
                    print("The file does not exist.")
            except PermissionError:
                    print("You do not have permission to delete this file.")
            except Exception as e:
                    print(f"An error occurred while deleting the file: {e}")

      



        
        
    with open(manifest_path, 'w') as file:
        json.dump(manifest, file)
        print("Manifest written")


    


if __name__ == "__main__":
    main()
