

INSTALL RED5 ON UBUNTU LINUX 8.10

1. Install Java 6.

user@host:$ sudo apt-get install openjdk-6-jdk
user@host:$ java -version
java version "1.6.0_0"
IcedTea6 1.3.1 (6b12-0ubuntu6.4) Runtime Environment (build 1.6.0_0-b12)
OpenJDK Client VM (build 1.6.0_0-b12, mixed mode, sharing)

2. Download and start Red5.
http://jira.red5.org/confluence/display/downloads/Red5+v0.8.0+Release+Candidate+2+02.03.2009

user@host:$ cd /opt
user@host:/opt$ sudo wget http://www.red5.org/downloads/red5/0_8_RC2/red5-0.8.RC2-java6.tar.gz
user@host:/opt$ sudo tar xzvf red5-0.8.RC2-java6.tar.gz
user@host:/opt$ sudo mv red5-0.8.RC2-build-hudson-red5_jdk6_stable-27 red5
user@host:/opt/red5$ cd /opt/red5

Now start Red5.

user@host:/opt/red5$ sudo ./red5.sh

3. Optionally, create /etc/init.d/red5 start/stop script.
http://osflash.org/red5/suse

4. ourstories_flash currently uses oflaDemo app.  Install oflaDemo app, Java 6
version, via Red5 installer app.  If necessary, replace localhost with your host.  
http://localhost:5080/installer/

On Linux, Flash may display "You are trying to install Adobe Flash Player 
on an unsupported operating system."

5. Symlink the oflaDemo streams folder into Django MEDIA_ROOT flv folder.  
In this example, /var/local/ourstories_staging/ourstories_django/static 
is Django's MEDIA_ROOT.  

user@host:/var/local/ourstories_staging/ourstories_django/static$ sudo ln -s /opt/red5/webapps/oflaDemo/streams flv

Now Django may serve static 1.flv, 2.flv files recorded by Red5 oflaDemo. 
http://localhost:8000/static/flv/1.flv

6. Look at FLV_ROOT and RED5_STREAMS_ROOT in ourstories_django settings.py .

# FLV_ROOT is a symlink to RED5_STREAMS_ROOT
# django knows the FLV_ROOT
# red5 knows the RED5_STREAMS_ROOT
FLV_ROOT = os.path.join(MEDIA_ROOT,'flv')
RED5_STREAMS_ROOT = '/opt/red5/webapps/oflaDemo/streams'

7. Ensure that the ourstories_config.xml file served at
/static/swf/ourstories_config.xml is configured to point at the correct
server URLs.  For example,
http://ourstories.jazkarta.com/static/swf/ourstories_config.xml would need
to include these lines:

    <red5_nc_url>rtmp:/oflaDemo</red5_nc_url>
    <amf_nc_url>http://ourstories.jazkarta.com/gateway/</amf_nc_url>
    <flv_url>http://ourstories.jazkarta.com/static/flv/</flv_url>
    <story_url>http://ourstories.jazkarta.com/story/</story_url>
    <story_record_url>http://ourstories.jazkarta.com/story/record/</story_record_url>

