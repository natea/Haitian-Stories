# To trigger automatic updates of story feeds, you'll need a cron job like
# this.  Make sure to modify any paths to point at wherever app is installed.
# m h  dom mon dow   command
*/10 *  *   *   *     (cd /var/local/ourstories_staging/ourstories_django;./manage.py update_feeds)
