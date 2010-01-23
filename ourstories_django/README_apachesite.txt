# OurStories example configuration for Apache2 + mod_python

PythonPath "['/var/local/ourstories_staging','/var/local/ourstories_staging/ourstories_django'] + sys.path" 

<VirtualHost *:80>
    ServerName ourstories-staging.jazkarta.com
    ErrorLog /var/log/apache2/ourstories-error_log
    CustomLog /var/log/apache2/ourstories-access_log combined
    SetEnv DJANGO_SETTINGS_MODULE settings
    LimitRequestBody 102400000
    SetHandler python-program
    PythonHandler django.core.handlers.modpython
    PythonDebug Off
    Alias /static /var/local/ourstories_staging/ourstories_django/static
    Alias /media /usr/share/python-support/python-django/django/contrib/admin/media
    <Location "/static">
       SetHandler default-handler
    </Location>
    <Location "/media">
       SetHandler default-handler
    </Location>
</VirtualHost>
