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

    video180_directory = config["video180"]  
    video180_dictionary = createDictionary(video180_directory, url)
   



    
    # check if manifest exists
    manifest_path = os.path.join(config["output"], "BuildManifest.json")
    keys_to_delete=[]
    # print(manifest_path)
    if os.path.exists(manifest_path):
        print("File exists.")
        with open(manifest_path, 'r') as file:
            manifest= json.load(file)

        update = False

        for entry in manifest["android"]:
            if entry not in android_dictionary:
                file_path=os.path.join(config["output"], manifest["android"][entry]["filename"])
                try:
                    os.remove(file_path)
                    print("File deleted successfully.")
                except FileNotFoundError:
                    print("The file does not exist.")
                except PermissionError:
                    print("You do not have permission to delete this file.")
                except Exception as e:
                    print(f"An error occurred while deleting the file: {e}")
                keys_to_delete.append(entry)
            else:
                if manifest["android"][entry]["hash"] != android_dictionary[entry]["hash"]:
                    update=True
                    version=int(manifest["android"][entry]["version"]) + 1
                    android_dictionary[entry]["version"]=version

                    file_path=os.path.join(config["output"], manifest["android"][entry]["filename"])
                    try:
                        os.remove(file_path)
                        print("File deleted successfully.")
                    except FileNotFoundError:
                        print("The file does not exist.")
                    except PermissionError:
                        print("You do not have permission to delete this file.")
                    except Exception as e:
                        print(f"An error occurred while deleting the file: {e}")
                    manifest["android"][entry]=android_dictionary[entry]

        for entry in android_dictionary:
            if entry not in manifest["android"]:
                manifest["android"][entry]=android_dictionary[entry]
                update = True


        for entry in manifest["windows"]:
            if entry not in windows_dictionary:
                file_path=os.path.join(config["output"], manifest["windows"][entry]["filename"])
                try:
                    os.remove(file_path)
                    print("File deleted successfully.")
                except FileNotFoundError:
                    print("The file does not exist.")
                except PermissionError:
                    print("You do not have permission to delete this file.")
                except Exception as e:
                    print(f"An error occurred while deleting the file: {e}")
                    keys_to_delete.append(entry)
            else:
                if manifest["windows"][entry]["hash"] != windows_dictionary[entry]["hash"]:
                    update=True
                    version=int(manifest["windows"][entry]["version"]) + 1
                    windows_dictionary[entry]["version"]=version

                    file_path=os.path.join(config["output"], manifest["windows"][entry]["filename"])
                    try:
                        os.remove(file_path)
                        print("File deleted successfully.")
                    except FileNotFoundError:
                        print("The file does not exist.")
                    except PermissionError:
                        print("You do not have permission to delete this file.")
                    except Exception as e:
                        print(f"An error occurred while deleting the file: {e}")
                    manifest["windows"][entry]=windows_dictionary[entry]

        for entry in windows_dictionary:
            if entry not in manifest["windows"]:
                manifest["windows"][entry]=windows_dictionary[entry]
                update = True
        
        for entry in manifest["video180"]:
            if entry not in video180_dictionary:
                file_path=os.path.join(config["output"], manifest["video180"][entry]["filename"])
                try:
                    os.remove(file_path)
                    print("File deleted successfully1.")
                except FileNotFoundError:
                    print("The file does not exist.")
                except PermissionError:
                    print("You do not have permission to delete this file.")
                except Exception as e:
                    print(f"An error occurred while deleting the file: {e}")
                    keys_to_delete.append(entry)
            else:
                if manifest["video180"][entry]["hash"] != video180_dictionary[entry]["hash"]:
                    update=True
                    version=int(manifest["video180"][entry]["version"]) + 1
                    windows_dictionary[entry]["version"]=version

                    file_path=os.path.join(config["output"], manifest["video180"][entry]["filename"])
                    try:
                        os.remove(file_path)
                        print("File deleted successfully2.")
                    except FileNotFoundError:
                        print("The file does not exist.")
                    except PermissionError:
                        print("You do not have permission to delete this file.")
                    except Exception as e:
                        print(f"An error occurred while deleting the file: {e}")
                    manifest["video180"][entry]=windows_dictionary[entry]
        
        for entry in video180_dictionary:
            if entry not in manifest["video180"]:
                manifest["video180"][entry]=windows_dictionary[entry]
                update = True

        if keys_to_delete is not None:
            update=True
            for key in keys_to_delete:
                if key in manifest["android"]:
                    manifest["android"].pop(key)
                if key in manifest["windows"]:
                    manifest["windows"].pop(key)

        if update:
            current_datetime = datetime.now().strftime('%d%m%Y_%H%M%S')
            manifest["version"] = "2.0." + current_datetime

        
            for entry in manifest["android"]:            
                if "path" in manifest["android"][entry]:
                    copy_file(manifest["android"][entry]["path"], config["output"])
                    manifest["android"][entry].pop("path")

            for entry in manifest["windows"]:            
                if "path" in manifest["windows"][entry]:
                    copy_file(manifest["windows"][entry]["path"], config["output"])
                    manifest["windows"][entry].pop("path")

            for entry in manifest["video180"]:            
                if "path" in manifest["video180"][entry]:
                    copy_file(manifest["video180"][entry]["path"], config["output"])
                    manifest["video180"][entry].pop("path")
                
            with open(manifest_path, 'w') as file:
                json.dump(manifest, file)
        
        else:
            print("no update to manifest")

    else:
        print("File does not exist.")
        manifest={}
        manifest["version"]="2.0.0"
        manifest["android"]=android_dictionary   
        # manifest["android"].update(experiment_dictionary) 
        # print(manifest)
        for entry in manifest["android"]: 
            copy_file(manifest["android"][entry]["path"], config["output"])
            manifest["android"][entry].pop("path")
            manifest["android"][entry]["version"]="1"

        
        manifest["windows"]=windows_dictionary
        # manifest["windows"].update(experiment_dictionary)    
        for entry in manifest["windows"]:            
            if "path" in manifest["windows"][entry]:
                copy_file(manifest["windows"][entry]["path"], config["output"])
                manifest["windows"][entry].pop("path")
            manifest["windows"][entry]["version"]="1"

        manifest["video180"]=video180_dictionary
        for entry in manifest["video180"]:
            if "path" in manifest["video180"][entry]:
                copy_file(manifest["video180"][entry]["path"], config["output"])
                manifest["video180"][entry].pop("path")
            manifest["video180"][entry]["version"]="1"

        
        
        with open(manifest_path, 'w') as file:
            json.dump(manifest, file)


  


if __name__ == "__main__":
    main()
