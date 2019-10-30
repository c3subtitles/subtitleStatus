"""This file provides a client to interact with youtube, trying to abstract their garbage API
"""

import os

import httplib2
from apiclient.discovery import build
from apiclient.http import MediaFileUpload

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage


class UploadError(Exception):
    """An error occured while uploading
    """
    pass


class YouTubeClient:
    """Provide API interfaces to interact with YouTube
    """
    # This OAuth 2.0 access scope allows an application to upload files to the
    # authenticated user's YouTube channel, but doesn't allow other types of access.
    YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    # This variable defines a message to display if the secrets_path is
    # missing.
    MISSING_CLIENT_SECRETS_MESSAGE = """
    WARNING: Please configure OAuth 2.0

    To make this sample run you will need to populate the client_secrets.json file
    found at:

       %s

    with information from the API Console
    https://console.developers.google.com/

    For more information about the client_secrets.json file format, please visit:
    https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
    """ % os.path.abspath(os.path.join(os.path.dirname(__file__), 'client_secrets.json'))

    def __init__(self, secrets_path='client_secrets.json'):
        """Initialize and set up an authenticated client

        Keyword Arguments:
            secrets_path {str} -- Path to the google api client secrets (default: {'client_secrets.json'})
        """
        flow_from_clientsecrets(secrets_path, scope=self.YOUTUBE_UPLOAD_SCOPE, message=self.MISSING_CLIENT_SECRETS_MESSAGE)

        self.storage = Storage("ytc-oauth2.json")
        credentials = self.storage.get()

        if credentials is None or credentials.invalid:
            raise ValueError('No client secret specified')

        self.credentials = credentials

        self.client = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, http=self.credentials.authorize(httplib2.Http()))

    def upload(self, video_file: str, title: str, description: str) -> str:
        """Upload a video to youtube (always as private)

        Arguments:
            video_file {str} -- Path to the video
            title {str} -- Title of the new video
            description {str} -- Description to be used

        Raises:
            UploadError: The upload failed

        Returns:
            str -- The video ID
        """

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': None,
                'categoryId': 22
            },
            'status': {
                'privacyStatus': 'private'
            }
        }

        # Call the API's videos.insert method to create and upload the video.
        insert_request = self.client.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
        )

        # Now upload
        response = None
        try:
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    return response['id']
            raise UploadError
        except:
            raise UploadError
