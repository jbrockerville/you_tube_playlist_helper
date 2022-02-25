# YouTube Playlist Helper

A simple command line tool for manipulating YouTube playlists. Its purpose is
to provide missing playlist operations such as sorting and randomizing.

## Prerequisites
- Python 3
- [Google Cloud Platform](https://console.cloud.google.com/) project

## Usage
- Create a new *Google Cloud Platform* project
    - The name does not matter
- Add the *YouTube Data API v3*
- Configure the *OAuth consent screen*
    - Set *Publishing status* to `In production`
    - Set *User type* to `External`
    - These settings may not be necessary, but it does make it easier
- Add *OAuth 2.0 Client IDs* credentials
    - Download the `client_secret_{client_id}.json` file
    - Move and rename the client secret file as `{script_location}/secrets/client_secret.json`
- Run the script
- Create a new user
    - Name is just a unique identifier for multiple stored creds in the `secrets/users.json` file
    - Authorize and all that
- Cache your playlists
- Select an action(s)
- Update your playlist(s)
- Hitting *Enter* on an empty prompt returns you to the previous prompt or exits

## Resources
- [Python YouTube Data API](https://developers.google.com/resources/api-libraries/documentation/youtube/v3/python/latest/)
- [Python Google API Client](https://github.com/googleapis/google-api-python-client)
- [YouTube Data API and OAuth2](https://developers.google.com/youtube/v3/guides/authentication)
