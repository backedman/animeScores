# create a program that backups every file in a directory into google drive
import os.path
from this import d
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from apiclient.http import MediaFileUpload
from urllib.error import HTTPError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import pickle
import time
import io
import json
import datetime

import os

ROOT = -1  # id signifying that the directory is the root directory


class MyDrive():

    queue = []
    existing_dirs = {}  # dict of directories that exist in the drive along with their ids
    existing_files = {}  # dict of files that exist in the drive along with their ids
    file_hierchy = {}
    file_hierchy_local = {}

    def __init__(self):

        CLIENT_SECRETS_FILE = 'credentials.json'
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = None
        self.local_dir = os.path.dirname(os.path.abspath(__file__))

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            with open('token.json', 'rb') as token:
                creds = Credentials.from_authorized_user_file(
                    'token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRETS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)

    def update(self, file_hierchy_drive=None, file_hierchy_local=None, directory_name="", parent_dir_name="", parent_id=ROOT, ignore_list=[], whitelist=[]):
        '''update the local file hierarchy with the files on the drive'''

        # if the file hierarchy is not provided, get it from the drive
        if file_hierchy_drive == None:
            file_hierchy_drive = self.get_file_hierchy(
                file_name=parent_dir_name, file_id=parent_id)
        if file_hierchy_local == None:
            file_hierchy_local = self.get_file_hierchy_local(
                self.local_dir + "/" + directory_name)

        if(parent_id == ROOT):
            # set parent id to the directory_name's id
            parent_id = self.existing_dirs[parent_dir_name]

        # compare the two file hierarchies. try to upload every file in local
        # and try to download every file in drive. When trying to upload or download,
        # include the path to the file in the upload or download functions
        for key in file_hierchy_drive:

            if(key == 'type'):
                continue

            if(key == 'id'):
                continue

            if(key == 'modifiedTime'):
                continue

            if(key in ignore_list):
                continue

            if(key not in whitelist and len(whitelist) > 0):
                continue

            # if key is a file, download it from drive and save it locally into the correct directory
            if(file_hierchy_drive[key]['type'] == "file"):

                # only download if the file does not exist locally or if the file locally is older than the file on drive
                print(file_hierchy_local[key]['modifiedTime'])
                print(file_hierchy_drive[key]['modifiedTime'])
                if(key not in file_hierchy_local or file_hierchy_local[key]['modifiedTime'] < file_hierchy_drive[key]['modifiedTime']):
                    #difference in time between the file on drive and the file on local
                    print("modified time difference: " + str(file_hierchy_drive[key]['modifiedTime'] - file_hierchy_local[key]['modifiedTime']))
                    self.download(file_hierchy_drive[key]['id'], key, directory_name)

            # if key is a directory, create it locally and then update it
            elif(file_hierchy_drive[key]['type'] == "directory"):
                directory = directory_name + "/" + key

                exists = os.path.exists(directory)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    file_hierchy_local[key] = self.get_file_hierchy_local(
                        directory)

                self.update(file_hierchy_drive[key], file_hierchy_local[key],
                            directory, parent_id=file_hierchy_drive[key]['id'], ignore_list=ignore_list)

        for key in file_hierchy_local:
            # if key is a file, upload it to drive

            if(key == 'type'):
                continue

            if(key == 'id'):
                continue

            if(key in ignore_list):
                continue

            if(key not in whitelist and len(whitelist) > 0):
                continue

            if(file_hierchy_local[key]['type'] == "file"):

                # file
                file_path = directory_name + "/" + key

                # update the id of the file in the file_hierchy_local
                if(key in file_hierchy_drive):
                    file_hierchy_local[key]['id'] = file_hierchy_drive[key]['id']

                # only upload if the file does not exist on drive or if the file on drive is older than the file locally
                elif(key not in file_hierchy_drive or file_hierchy_drive[key]['modifiedTime'] < file_hierchy_local[key]['modifiedTime']):
                    # upload the file to the drive with the file_path as the name, the parent_id, and the modifiedTime of the file
                    if(key in file_hierchy_drive):
                        print("modified time difference: " + str(file_hierchy_drive[key]['modifiedTime'] - file_hierchy_local[key]['modifiedTime']))
                    
                    file_hierchy_local[key]['id'] = self.upload(
                        file_path, parent_id, file_hierchy_local[key]['modifiedTime'])

            # if key is a directory, create it on drive and then update it
            elif(file_hierchy_local[key]['type'] == "directory"):
                directory = directory_name + "/" + key
                id = self.create_folder(key, parent_id=parent_id)

                # update id of directory in file_hierchy_local
                file_hierchy_local[key]['id'] = id

                if key not in file_hierchy_drive:
                    file_hierchy_drive[key] = {}

                self.update(
                    file_hierchy_drive[key], file_hierchy_local[key], directory, parent_id=id, ignore_list=ignore_list)

    def download(self, file_id, file_name, directory_name):
        '''download a file from drive and save it locally'''

        file_path = self.local_dir + directory_name + "/" + file_name
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download {}%.".format(int(status.progress() * 100)))

        # print file downloaded
        print("Downloaded file: " + file_name)

        # return id
        return file_id

    def upload(self, file_name, parent_id, modified_time=None):
        '''upload a file to drive'''

        file_path = self.local_dir + "/" + file_name
        name = os.path.basename(file_name)

        file_metadata = {
            'name': name,
            'parents': [parent_id],
            'modifiedTime': self.convert_to_uploadable_dt(modified_time)
        }
        media = MediaFileUpload(file_path,
                                mimetype='text/plain',
                                resumable=True)
        file = self.service.files().create(body=file_metadata,
                                           media_body=media,
                                           fields='id').execute()

        # print file uploaded
        print("Uploaded file: " + file_name)

        return file.get('id')

    def get_file_hierchy(self, file_name, file_id=ROOT):
        '''get the list of the directory, its files, and its subdirectories
            and put them into a dict'''

        file_hierchy = {}

        if file_id == ROOT:
            # create the root directory
            file_id = self.create_folder(file_name)

        # get the files in the directory on the drive and include modified time
        try:
            files = self.service.files().list(q="'{}' in parents".format(
                file_id), fields='files(id, name, mimeType, parents, modifiedTime)').execute()
            
        except:  # if the directory does not exist, create it
            self.create_folder(file_name, parent_id=file_id)
            return self.get_file_hierchy(file_name, file_id)

        # if the directory is empty, return an empty dict
        if not files['files']:
            return file_hierchy

        # put the files in the directory into a dict
        for file in files['files']:

            # print(file)

            if(file['mimeType'] == 'application/vnd.google-apps.folder'):
                print("modifiedTime: " + str(file['modifiedTime']))
                self.existing_dirs[file['name']] = file['id']
                file_hierchy[file['name']] = self.get_file_hierchy(file_name = file['name'], file_id = file['id'])
                file_hierchy[file['name']].update({'type': 'directory', 'modifiedTime': file['modifiedTime'], 'id': file['id']})

            else:
                self.existing_files[file['name']] = file['id']
                print(file['modifiedTime'])
                file_hierchy[file['name']] = {
                    'name': file['name'], 'id': file['id'], 'modifiedTime': self.convert_to_datetime(file['modifiedTime'])}
                file_hierchy[file['name']].update({'type': 'file'})

        #self.file_hierchy = file_hierchy

        return file_hierchy

    def get_file_hierchy_local(self, file_name):
        '''get the list of the directory, its files, and its subdirectories
            and put them into a dict'''

        file_hierchy = {}
        # get the files in the directory on the drive and include modified time
        files = os.listdir(file_name)

        for file in files:
            if(os.path.isdir(file_name + "/" + file)):
                #self.existing_dirs[file] = file_name
                file_hierchy[file] = self.get_file_hierchy_local(
                    file_name + "/" + file)
                file_hierchy[file].update({'type': 'directory'})
            else:
                #self.existing_files[file] = file_name
                file_hierchy[file] = {'name': file, 'id': file_name, 'modifiedTime': self.convert_to_datetime(
                    os.path.getmtime(file_name + "/" + file))}
                file_hierchy[file].update({'type': 'file'})

        #self.file_hierchy_local = file_hierchy

        return file_hierchy

    def create_folder(self, file_name, parent_id=ROOT, replace=True):
        '''create a folder on drive'''


        file_metadata = {
            'name': file_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }

        # check if folder already exists
        if file_name in self.existing_dirs:
            exists = True
            file_id = self.existing_dirs[file_name]
        else:
            # check if folder exists in drive
            file_id = self.search_folder(file_name, parent_id)
            if(file_id == None):
                exists = False
            else:
                exists = True

        if(parent_id == ROOT or (replace and exists)):
            del file_metadata['parents']


        # if the folder already exists, replace it
        if(exists):
            if(replace):
                file = self.service.files().update(
                    fileId=self.existing_dirs[file_name], body=file_metadata, fields='id').execute()
                return file.get('id')
            else:
                return self.existing_dirs[file_name]
        else:
            file = self.service.files().create(body=file_metadata, fields='id').execute()
            self.existing_dirs[file_name] = file.get('id')
            return file.get('id')

    def search_folder(self, file_name, parent_id=ROOT):
        '''search for a folder in drive with given name and parent id (if given)'''

        # get the folder in the drive with the given name and parent id
        if(parent_id == ROOT):
            files = self.service.files().list(q="name = '{}' and mimeType = 'application/vnd.google-apps.folder'".format(file_name),
                                              fields='files(id, name, mimeType, parents)').execute()
        else:
            files = self.service.files().list(q="name = '{}' and mimeType = 'application/vnd.google-apps.folder' and '{}' in parents".format(file_name,
                                                                                                                                             parent_id), fields='files(id, name, mimeType, parents)').execute()

        # if the folder exists, put its id into the existing_dirs dict
        if files['files']:
            self.existing_dirs[file_name] = files['files'][0]['id']

        # return id of the folder if it exists
        if(file_name in self.existing_dirs):
            return self.existing_dirs[file_name]
        else:
            return None

    def convert_to_datetime(self, time):
        '''convert the modified time of the file to datetime'''


        if(type(time) == str):
            return datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')
        else:
            return datetime.datetime.fromtimestamp(time)

    def convert_to_uploadable_dt(self, time):
        '''converts the datetime to the format that google drive accepts'''

        return time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    def run_queue(self):
        '''run all the files in the queue in a batch request. This is to prevent the rate limit.
            The batch is split up if the combined requests are longer than 8000 characters or if there are over 90 requests in
            the queue.'''

        # split up the queue into batches
        batches = []
        batch = []
        for i in range(len(self.queue)):
            batch.append(self.queue[i])
            if len(batch) == 90 or len(batch) * len(batch[0]) > 8000:
                batches.append(batch)
                batch = []
        if len(batch) > 0:
            batches.append(batch)

        # run the batches
        for batch in batches:
            batch_request = self.service.new_batch_http_request()
            for request in batch:
                if request[0] == "upload":
                    file_path = request[2]
                    file_name = request[1]
                    parents = self.get_parents(os.path.dirname(file_name))
                    body = {'name': file_name, 'parents': parents}
                    media = MediaFileUpload(file_path, mimetype='text/plain')
                    batch_request.add(self.service.files().create(
                        body=body, media_body=media, fields='id'), request[1])
                elif request[0] == "download":
                    file_name = request[1]
                    file_path = request[2]
                    parents = self.get_parents(os.path.dirname(file_name))
                    request = self.service.files().get_media(
                        fileId=file_name, supportsTeamDrives=True)
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print("Download %d%%." % int(status.progress() * 100))
                    with open(file_path, 'wb') as f:
                        fh.seek(0)
                        f.write(fh.read())
                elif request[0] == "create_dir":
                    self.create_dir(request[2])

            batch_request.execute()

        self.queue = []


def main():

    # create a google drive object
    drive = MyDrive()

    # update but ignore the file data.txt and the directory pyenv with the parent directory
    # in the drive being named "animeScores"
    # ignore all files except the one in the directory Data and nnWeights
    drive.update(parent_dir_name="animeScores", ignore_list=["data.txt", "pyenv"], whitelist=["Data", "nnWeights"])

main()
