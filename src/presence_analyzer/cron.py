"""
Fetching users.xml file from http://sargo.bolt.stxnext.pl/users.xml
"""
import os.path
import urllib2
from shutil import move

TMP_DATA_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'tmp_data.xml'
)

MAIN_DATA_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'sample_data.xml'
)


def fetch_xml_file(url):
    """
    Main procedure for fetching users.xml file
    """
    try:
        result = urllib2.urlopen(url)
        html = result.read()
        with open(TMP_DATA_XML, 'w+') as tmpfile:
            tmpfile.write(html)
            move(TMP_DATA_XML, MAIN_DATA_XML)
            return "OK"
    except urllib2.URLError, err:
        print err


if __name__ == '__main__':
    fetch_xml_file("http://sargo.bolt.stxnext.pl/users.xml")
