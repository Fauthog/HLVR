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
    print("create", directory, url)

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
                file_list[file]= {"filename":file, "hash":hash, "size":os.path.getsize(file_path), "url":url_file}
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


def buildManifest():
    # read config
    config_path = "config.ini"  # Replace with your file path
    config = read_ini_config(config_path)

 

     
    # check if manifest exists
    manifest_path = os.path.join(config["media"], "ServerMedia.json")
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


    # build dictionaries of current files
    url="192.168.2.200/HLVR/media/"
    media_directory = config["media"]    
    media_dictionary = createDictionary(media_directory, url)  


    manifest={}
    current_datetime = datetime.now().strftime('%d%m%Y_%H%M%S')
    media_dictionary["version"]="2.0." + current_datetime

    # manifest["media"]=media_dictionary  
  
        
        
    with open(manifest_path, 'w') as file:
        json.dump(media_dictionary, file)
        print("Manifest written")


    


if __name__ == "__main__":
    buildManifest()
