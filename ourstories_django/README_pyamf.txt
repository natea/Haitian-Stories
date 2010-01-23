


elementtree-1.2.6-20050316.tar.gz
fpconst-0.7.2.tar.gz
PyAMF-0.4.1.tar.gz
uuid-1.30.tar.gz



http://pyamf.org/wiki/DjangoHowto



$ ./manage.py shell
Python 2.5.2 (r252:60911, Oct  5 2008, 19:24:49) 
[GCC 4.3.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from pyamf.remoting.client import RemotingService
>>> gw = RemotingService('http://127.0.0.1:8000/gateway/')
>>> service = gw.getService('flv') # our stories flv recorder services
>>> print service.ping()
pong
>>> print service.getId()
22
>>> print service.setStatus(1,1)
True
>>> print service.setStatus(1,4) # there is no status 4
False
>>> exit()
$ 


