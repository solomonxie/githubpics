# -*- coding: utf-8 -*-

"""
MAC ONLY.
This if for convenience of writing markdown notes:
Send screenshots to github and get the raw url, 
then paste in markdown file as a permanent image link.
BTW, it has minimum logging and error control.

REQUIREMENT:
    pip install pyobjc        # FOR MAKING IT PYTHONIC WAY
    brew install pngpaste     # FOR CALLING COMMAND LINE TOOL
    brew install osascript    # TERMINAL TOOL FOR RUNNING APPLESCRIPT

CONFIGURATION:
    Github repository address
    Github Personal Access Token
    
"""

import os
import sys
import time
import json
import base64
import requests

# PyObjc library > Appkit > NSPasteboard (main class for clipboard) and file type classes
from AppKit import NSPasteboard, NSPasteboardTypePNG, NSPasteboardTypeTIFF, NSPasteboardTypeString


def main():
    """
    Main entry of this app
    """
    print 'Start...'

    #filepath = get_pasteboard_img()
    #filepath = get_pasteboard_png()
    filepath = get_pasteboard_img_or_filepath()

    if not filepath or os.path.exists(filepath) is False:
        print 'Process incomplete due to invalid pasteboard data.'
        return

    print 'Saved image path is %s' % filepath

    bs64 = img_to_bs64(filepath)              # convert img file to base64 string
    url  = upload_to_github(filepath, bs64)   # call github api to upload img

    if not url:
        print 'Failed to upload file to github.'
        return

    # Store img url with markdown format
    markdown = '![Title](%s)' % url
    os.system('echo "%s" | pbcopy' % markdown)
    print 'Uploaded.\nNow copy image url[%s] to clipboard...' % url

    # Show notifications on mac (Applescript)
    os.system('osascript -e "display notification \\"Now you can paste url link to makrdown: %s\\""' % markdown)



def get_pasteboard_img_or_filepath():
    """
    Mix `pngpaste` cli tool and `NSPasteboard` python mudule
    for reading both img files or file path from pasteboard
    """
    pb = NSPasteboard.generalPasteboard()  # Get data object from clipboard 
    data_type = pb.types()                 # Get type of the data

    # Recognize data type for furher processing 
    if NSPasteboardTypePNG in data_type or \
            NSPasteboardTypeTIFF in data_type:      # Get data content by data type
        filepath = '/tmp/%d.png' % int(time.time() * 1000)
        os.system('pngpaste %s' % filepath)         # save img to local file
    elif NSPasteboardTypeString in data_type:    
        # Text: if it's already a filepath then just return it
        filepath = str(pb.dataForType_(NSPasteboardTypeString))
    else: 
        return None

    return filepath if os.path.exists(filepath) else None


def get_pasteboard_img():
    """
    Get image from pasteboard/clipboard and save to file 
    DEPRECATED: FOR THE REASON IT ONLY GENERATES TIFF IMAGE FROM CLIPBOARD
    WHICH MAKES TO BE NEEDED ONE MORE FUNCTION TO CONVERT IMAGE TO PNG
    """
    pb = NSPasteboard.generalPasteboard()  # Get data object from clipboard 
    data_type = pb.types()                 # Get type of the data

    # Recognize data type for furher processing 
    if NSPasteboardTypePNG in data_type:         # PNG:
        # Get data content by data type
        data = pb.dataForType_(NSPasteboardTypePNG)
        filename = '%d.png' % int(time.time() * 1000)
    elif NSPasteboardTypeTIFF in data_type:      # TIFF: most probablly it's tiff
        data = pb.dataForType_(NSPasteboardTypeTIFF)
        filename = '%d.tiff' % int(time.time() * 1000)
    elif NSPasteboardTypeString in data_type:    # Text: if it's already a filepath then just return it
        data = str(pb.dataForType_(NSPasteboardTypeString))
        return data if os.path.exists(data) else None
    else: 
        return None

    # Write data to a local file
    filepath = '/tmp/%s' % filename
    success = data.writeToFile_atomically_(filepath, False)

    return filepath if success else None


def get_pasteboard_png():
    """
    Get png from pasteboard by commandline tool `pngpaste`, and save to file
    """
    filepath = '/tmp/%d.png' % int(time.time() * 1000)

    os.system('pngpaste %s' % filepath)

    return filepath if os.path.exists(filepath) else None



def upload_to_github(path, fcontent):
    """
    Upload local image file to github repo via Github API
    """
    filename = os.path.basename(path)

    # Read token string from a file outside repo
    with open('/Users/solomonxie/Workspace/etc/configs/github-token-for-gpcis', 'r') as f:
        token = f.read().strip('\n\t\r')

    # prepare request for Gihut API
    api = 'https://api.github.com/repos/solomonxie/user_content_media/contents/markdown-images/%s' % filename
    headers = {'authorization': 'token %s' % token}
    payload = '{"message": "auto uploaded by python", "content": "%s"}' % fcontent

    # upload image data to github
    print 'Uploading an image onto Github repository...'
    r = requests.request("PUT", url=api, data=payload, headers=headers, timeout=10)

    print 'Response Code: %d' % r.status_code
    #print 'Response body:\n%s' % r.content

    if r.status_code is not 201:
        print 'Requesting of uploading failed...'
        return

    # Get the file's raw url on Github
    info = r.json()

    return info['content']['download_url']



def img_to_bs64(path):
    """
    Convert an image file to base64 string
    Github API: to create a content, the file has to be encoded with base64
    """
    with open(path, 'rb') as f:
        encoded = base64.b64encode(f.read())

    print 'Encoded an image into a base64 string. [%d]' % len(encoded)
    return encoded



def test_getClipboardFiles():
    import pdb;pdb.set_trace()
    import AppKit
    pb = NSPasteboard.generalPasteboard()
    if pb.availableTypeFromArray_( [AppKit.NSFilenamesPboardType] ):
        files = pb.propertyListForType_( AppKit.NSFilenamesPboardType )
        return [ unicode( filename ) for filename in files ]
    else:
        return []

if __name__ == "__main__":
    main()
