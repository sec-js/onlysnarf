# OnlySnarf

`pip3 install OnlySnarf`  
or  
`git clone git@github.com:skeetzo/onlysnarf && sudo python3 setup.py install`

## Description

OnlySnarf is a python based automation tool to assist with uploading content to OnlyFans. OnlySnarf is capable of downloading and uploading a file (image or video) or gallery of files (images) from a Google Drive folder as specified by run time arguments to an OnlyFans account.

## Menu
[Menu](https://github.com/skeetzo/onlysnarf/blob/master/OnlySnarf/menu.md)

## Preview
![preview](https://github.com/skeetzo/onlysnarf/blob/master/OnlySnarf/images/preview.jpeg)

## Scripts
First run:  
  * `(sudo) onlysnarf-config`
Then from within project's OnlySnarf directory either:  
  * `(sudo) onlysnarf [args]`
  * `(sudo) onlysnarfpy (-debug) -type image|gallery|video`
  * or directly via `python3 onlysnarf.py (-debug) -type image|gallery|video`

## args

-debug  
  `python3 onlysnarf.py -debug`  
Tests configuration. Does not upload or remove from Google Drive.

-image  
  `python3 onlysnarf.py -type image`  
Uploads an image labeled: 'imageName - %d%m%y'  

-gallery  
  `python3 onlysnarf.py -type gallery`  
Uploads a gallery labeled: 'folderName - %d%m%y'  

-video  
  `python3 onlysnarf.py -type video`  
Uploads a video labeled: 'folderName - %d%m%y'  

-text  
  `python3 onlysnarf.py -type video -text "your mom"`  
Uploads a video labeled: 'your mom - %d%m%y'  

-show-window
  `python3 onlysnarf.py -show-window`
Shows the Chromium browser

**more available in menu**

Or include a 'config.conf' file located at '/etc/onlysnarf/config.conf' to set variables at runtime without using arguments. An example file has been provided. Please be sure to follow the key:value pattern. A starting # denotes a comment.

## Authentication  
--------------
The use of this package requires configuring a Google App with *PyDrive* for access to your Google Drive. The Drive API requires OAuth2.0 for authentication.
###### from [Auth Quickstart](https://raw.githubusercontent.com/gsuitedevs/PyDrive/master/docs/quickstart.rst)
1. Go to `APIs Console`_ and make your own project.
2. Search for 'Google Drive API', select the entry, and click 'Enable'.
3. Select 'Credentials' from the left menu, click 'Create Credentials', select 'OAuth client ID'.
4. Now, the product name and consent screen need to be set -> click 'Configure consent screen' and follow the instructions. Once finished:

 a. Select 'Application type' to be *Web application*.
 b. Enter an appropriate name.
 c. Input *http://localhost:8080* for 'Authorized JavaScript origins'.
 d. Input *http://localhost:8080/* for 'Authorized redirect URIs'.
 e. Click 'Create'.

5. Click 'Download JSON' on the right side of Client ID to download **client_secret_<really long ID>.json**.

**Rename the file to "client_secrets.json" and place it into your installed OnlySnarf directory.**
To update your installation with the new file, run `onlysnarf-config`, select 'Update Google Creds', and enter the location of your "client_secret.json" file.

## Config
##### config.conf  
Path: /etc/onlysnarf/config.conf
Create or update the "config.conf" file with the following values:
  * username -> the Twitter connected to your OnlyFans's username  
  * password -> the Twitter conencted to your OnlyFans's password  

###### Why Twitter credentials?
OnlyFans uses a captcha to prevent malicious bots from accessing user accounts. However, this captcha is only necessary when logging in with your OnlyFans username and password. Logging in with the provided Twitter authentication does not provide a captcha and thus allows a more accessible automated entrance.

##### google_creds.txt   
Generated by Google Drive's authentication process. Saves Google authentication for repeat access.

##### settings.yaml  
Used to facilitate Google Drive's python authentication. Requires generating an app w/ credentials via Google Console. Credentials are authenticated once and then saved to "google_creds.txt".

## Example Crons  

Upload a random image once a day at noon:  
  `* 12 * * * onlysnarfpy -type image`

Upload a random gallery of images every Wednesday at 2:30pm:  
  `30 14 * * 3 onlysnarfpy -type gallery`

Upload a random video every Friday in the month of June at 6:00pm:  
  `00 18 * 6 5 onlysnarfpy -type video`

Text will be generated if not provided with `-text`
  `* 12 * * * onlysnarfpy -type image -text "Your mother is a dirty whore"`

## Dependencies
  ### Google Chrome -> `sudo apt install -y google-chrome-beta`