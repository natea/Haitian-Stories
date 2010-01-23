""" video.py 
Quick 'n dirty video encoding functions. These require ImageMagick, ffmpeg and mencoder to be installed;
the paths to these executables are set in the top-level django settings.py module.

@note: no video uploading functions of any kind are defined/performed in this module (as they do not belong here)
      - see the youtube.py module for those.

@todo: replace the ImageMagick stuff with the Python Imaging Library (PIL)
"""

import os
import tempfile

from ourstories_django.settings import VIDEO_IMAGEMAGICK_CONVERT_BIN, VIDEO_FFMPEG_BIN, VIDEO_MENCODER_BIN

def createVideo(imageFilename, audioFilename, duration, fps=30):
    """ Creates a youtube-uploadable video from the specified image, with the audio track contained
    in <audioFilename> as narration (so it's really more like a narrated one-picture slideshow)
    
    @param fps: frames per second for the resulting video
    @type fps: int 
    
    @raise IOError: if any of the specified files do not exist
    
    @return: The resulting video clip's absolute filename
    @rtype: str
    """
    # Check if files actually exist
    for filename in (imageFilename, audioFilename):
        if not os.path.exists(filename):
            raise IOError, 'File does not exist: %s' % filename
    # Convert the image and audio track to suitable formats...
    convImageFilename = convertImage(imageFilename)
    convAudioFilename = convertAudio(audioFilename)
    # ...and combine them into a .avi video file
    tempFilename = tempfile.mkstemp(prefix='_created_', suffix='.avi')[1] # the destination filename for the video clip
    mencoderCmd = '%s mf://%s -mf fps=%f -vf harddup -ovc lavc -lavcopts vbitrate=100 -audiofile %s -oac copy -ofps %d -o %s' % (VIDEO_MENCODER_BIN, convImageFilename, 1.0/float(duration), convAudioFilename, fps, tempFilename)
    #TODO: perhaps use popen for these type of things, so that we can track status
    if os.system(mencoderCmd) != 0:
        raise Exception, 'Video creation failed'
    # Clean up temporary files
    for filename in (convImageFilename, convAudioFilename):
        os.remove(filename)
    return tempFilename

def convertImage(imageFilename):
    """ Converts the image with the specified filename to a 320x240 jpeg (best resolution for youtube)
    using ImageMagick binaries
    @return: The resulting file's absolute filename
    @rtype: str
    """
    tempFilename = tempfile.mkstemp(prefix='_converted_', suffix='.jpg')[1] # the destination filename for the converted image
    resizeCmd = '%s -adaptive-resize 320x240 %s %s' % (VIDEO_IMAGEMAGICK_CONVERT_BIN, imageFilename, tempFilename)
    #TODO: perhaps use popen for these type of things, so that we can track status
    if os.system(resizeCmd) != 0:
        raise Exception, 'Image conversion failed'
    print '>>>   image output:', tempFilename
    return tempFilename

def convertAudio(audioFilename):
    """ Converts the audio clip with the specified filename to mp3
    @return: The resulting file's absolute filename
    @rtype: str
    """
    tempFilename = tempfile.mkstemp(prefix='_converted_', suffix='.mp3')[1] # the destination filename for the converted audio clip
    convertCmd = '%s -y -i %s %s' % (VIDEO_FFMPEG_BIN, audioFilename, tempFilename)
    #TODO: perhaps use popen for these type of things, so that we can track status
    if os.system(convertCmd) != 0:
        raise Exception, 'Audio conversion failed'
    print '>>>   audio output:',tempFilename
    return tempFilename
