import urllib2
import urllib
data = {}
data['msg'] = 'reqest from tigal'
data['num'] = 'my super number'
url_values = urllib.urlencode(data)
print url_values
url = 'https://192.168.0.101:8090/wsgiserver.py'
full_url = url + '?' + url_values
data = urllib2.urlopen(full_url)
