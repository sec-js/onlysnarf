#!/usr/bin/python
# 3/28/2019: Skeetzo

import random
import os
import shutil
import datetime
import json
import sys
import pathlib
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from . import settings

###################
##### Globals #####
###################

DRIVE = None

##################
##### Config #####
##################

CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.json')
try:
    with open(CONFIG_FILE) as config_file:    
        config = json.load(config_file)
except FileNotFoundError:
    print('Missing Config, run `onlysnarf-config`')
    sys.exit(0)

OnlyFans_VIDEOS_FOLDER = config['videos_folder']
OnlyFans_IMAGES_FOLDER = config['images_folder']
OnlyFans_GALLERIES_FOLDER = config['galleries_folder']
OnlyFans_POSTED_FOLDER = config['posted_folder']

###################
##### Helpers #####
###################

# debugging
def maybePrint(text):
    if settings.DEBUG:
        print(text);

# mkdir /tmp
def getTmp():
    tmp = os.getcwd()
    global MOUNT_PATH
    if settings.MOUNT_PATH:
        tmp = os.path.join(settings.MOUNT_PATH, "tmp")
    else:
        tmp = os.path.join(tmp, "tmp")
    if not os.path.exists(str(tmp)):
        os.mkdir(str(tmp))
    return tmp

def authGoogle():
    print('Authenticating Google...')
    try:
        GOOGLE_CREDS = os.path.join(os.path.dirname(os.path.realpath(__file__)),'google_creds.txt')
        # Google Auth
        gauth = GoogleAuth()
        # Try to load saved client credentials
        gauth.LoadCredentialsFile(GOOGLE_CREDS)
        maybePrint('Loaded: Google Credentials')
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved creds
            gauth.Authorize()
        # Save the current credentials to a file
        gauth.SaveCredentialsFile(GOOGLE_CREDS)
        global DRIVE
        DRIVE = GoogleDrive(gauth)
    except:
        maybePrint(sys.exc_info()[0])
        print('...Authentication Failure!')
        return False
    print('...Authentication Success!') 
    return True

# Downloads random video from Google Drive
def get_random_video():
    print('Getting Random Video...')
    global DRIVE
    random_folders = DRIVE.ListFile({'q': "'"+OnlyFans_VIDEOS_FOLDER+"' in parents and trashed=false and mimeType contains 'application/vnd.google-apps.folder'"}).GetList()
    video_list = []
    random_video = None
    for folder in random_folders:
        print('checking folder: '+folder['title'],end="")
        video_list_tmp = DRIVE.ListFile({'q': "'"+folder['id']+"' in parents and trashed=false and mimeType contains 'video/mp4'"}).GetList()
        if len(video_list_tmp)>0:
            video_list.append(folder)
            print(" -> added")
        else:
            print(" -> empty")
    if len(video_list)==0:
        print('No video file found!')
        return
    random_video = random.choice(video_list)
    folder_name = random_video['title'];
    print('Random Folder: '+random_video['title'])
    random_video = DRIVE.ListFile({'q': "'"+random_video['id']+"' in parents and trashed=false and mimeType contains 'video/mp4'"}).GetList()
    random_video = random.choice(random_video)
    print('Random Video: '+random_video['title'])
    return [random_video, folder_name]

# Downloads random image from Google Drive
def get_random_image():
    print('Getting Random Image...')
    global DRIVE
    random_folders = DRIVE.ListFile({'q': "'"+OnlyFans_IMAGES_FOLDER+"' in parents and trashed=false and mimeType contains 'application/vnd.google-apps.folder'"}).GetList()
    images_list = []
    random_image = None
    for folder in random_folders:
        if settings.DEBUG:
            print('checking folder: '+folder['title'],end="")
        images_list_tmp = DRIVE.ListFile({'q': "'"+folder['id']+"' in parents and trashed=false and (mimeType contains \'image/jpeg\' or mimeType contains \'image/jpg\' or mimeType contains \'image/png\')"}).GetList()      
        if len(images_list_tmp)>0:
            video_list.append(folder)
            maybePrint(" -> added")
        else:
            maybePrint(" -> empty")
    if len(images_list)==0:
        print('No image file found!')
        return
    random_image = random.choice(images_list)
    folder_name = random_image['title'];
    print('Random Folder: '+random_image['title'])
    random_image = DRIVE.ListFile({'q': "'"+random_image['id']+"' in parents and trashed=false and (mimeType contains \'image/jpeg\' or mimeType contains \'image/jpg\' or mimeType contains \'image/png\')"}).GetList()
    random_image = random.choice(random_image)
    print('Random Image: '+random_image['title'])
    return [random_image, folder_name]

# Downloads random gallery from Google Drive
def get_random_gallery():
    print('Getting Random Gallery...')
    global DRIVE
    random_folders = DRIVE.ListFile({'q': "'"+OnlyFans_GALLERIES_FOLDER+"' in parents and trashed=false and mimeType contains 'application/vnd.google-apps.folder'"}).GetList()
    folder_list = []
    gallery_list = []
    random_gallery = None
    for folder in random_folders:
        if settings.DEBUG:
            print('checking galleries: '+folder['title'],end="")
        gallery_list_tmp = DRIVE.ListFile({'q': "'"+folder['id']+"' in parents and trashed=false and mimeType contains 'application/vnd.google-apps.folder'"}).GetList()
        if len(gallery_list_tmp)>0:
            folder_list.append(folder)
            maybePrint(" -> added")
        else:
            maybePrint(" -> empty")
    random.shuffle(folder_list)
    for folder in folder_list:
        if settings.DEBUG:
            print('checking gallery: '+folder['title'],end="")
        gallery_list_tmp = DRIVE.ListFile({'q': "'"+folder['id']+"' in parents and trashed=false and mimeType contains 'application/vnd.google-apps.folder'"}).GetList()
        random_gallery_tmp = random.choice(gallery_list_tmp)
        gallery_list_tmp_tmp = DRIVE.ListFile({'q': "'"+random_gallery_tmp['id']+"' in parents and trashed=false and (mimeType contains \'image/jpeg\' or mimeType contains \'image/jpg\' or mimeType contains \'image/png\')"}).GetList()
        if len(gallery_list_tmp_tmp)>0:
            folder_name = folder['title']
            random_gallery = random_gallery_tmp
            maybePrint(" -> found")
        else:
            maybePrint(" -> empty")
    if not random_gallery:
        print('No gallery folders found!')
        return
    print('Random Gallery: '+random_gallery['title'])
    return [random_gallery, folder_name]

# Download File
def download_file(file):
    print('Downloading Video...')
    tmp = getTmp()
    # download file
    ext = os.path.splitext(file['title'])[1]
    if not ext:
        ext = '.mp4'
        maybePrint('ext (default): '+str(ext))
    else:
        maybePrint('ext: '+str(ext))
    tmp += "/uploadMe"+str(ext)
    maybePrint('path: '+str(tmp))
    file.GetContentFile(tmp)
    if os.path.getsize(tmp) == 0:
        maybePrint('size: '+str(os.path.getsize(tmp)))
        print('Download Failure')
        return
    print('Download Complete')
    return tmp

# Download Gallery
def download_gallery(folder):
    print('Downloading Gallery...')
    tmp = getTmp()
    # download folder
    global DRIVE
    file_list = DRIVE.ListFile({'q': "'"+folder['id']+"' in parents and trashed=false and (mimeType contains \'image/jpeg\' or mimeType contains \'image/jpg\' or mimeType contains \'image/png\')"}).GetList()
    folder_size = len(file_list)
    maybePrint('Folder size: '+str(folder_size))
    maybePrint('Upload limit: '+str(settings.IMAGE_UPLOAD_LIMIT))
    if int(folder_size) == 0:
        print('Error: Empty Folder')
        return
    file_list_random = []
    for x in range(settings.IMAGE_UPLOAD_LIMIT):
        random_file = random.choice(file_list)
        file_list.remove(random_file)
        file_list_random.append(random_file)
    i = 1
    for file in sorted(file_list_random, key = lambda x: x['title']):
        print('Downloading {} from GDrive ({}/{})'.format(file['title'], i, folder_size))
        maybePrint('filePath: '+tmp+"/"+str(file['title']))
        file.GetContentFile(tmp+"/"+str(file['title']))
        i+=1
    print('Download Complete')
    return [file_list_random, tmp]

# Deletes online file
def delete_file(file):
    if not settings.DELETING or settings.DELETING == "False":
        print("Skipping Delete")
        return
    print('Trashing Google Video')
    if settings.DEBUG:
        print('skipping Google delete')
        return
    file.Trash()
    print('Google Video Trashed')

# Archives posted file / folder
def move_file(file):
    if settings.DEBUG or not settings.BACKING_UP or settings.BACKING_UP == "False":
        print('Skipping Google Backup: '+file['title'])
        return
    file['parents'] = [{"kind": "drive#fileLink", "id": OnlyFans_POSTED_FOLDER}]
    file.Upload()
    print('Google File Backed Up: '+file['title'])

def move_files(folderName, files):
    if settings.DEBUG or not settings.BACKING_UP or settings.BACKING_UP == "False":
        print('Skipping Google Backup: '+folderName)
        return
    title = folderName+" - "+datetime.datetime.now().strftime("%d-%m-%I-%M")
    print('title: '+title)
    global DRIVE
    tmp_folder = DRIVE.CreateFile({'title':title, 'parents':[{"kind": "drive#fileLink", "id": OnlyFans_POSTED_FOLDER}],'mimeType':'application/vnd.google-apps.folder'})
    tmp_folder.Upload()
    for file in files:
        file['parents'] = [{"kind": "drive#fileLink", "id": tmp_folder['id']}]
        file.Upload()
    print('Google Files Backed Up')