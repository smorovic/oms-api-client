import os

import requests
from urllib.parse import urlparse, urljoin
from xml.etree import ElementTree

DEFAULT_CERT_FILENAME = "usercert.pem"
DEFAULT_KEY_FILENAME = "userkey.pem"
DEFAULT_CERT_LOCATIONS = ["private", ".globus"] # ~/private and ~/.glogus

def get_user_cert():
    """ Returns user certificate paths """

    home = os.getenv("HOME")

    for location in DEFAULT_CERT_LOCATIONS:
        usercert = os.path.join(home, location, DEFAULT_CERT_FILENAME)
        userkey = os.path.join(home, location, DEFAULT_KEY_FILENAME)

        if os.path.isfile(usercert) and os.path.isfile(userkey):
            print("Certificate location: " + os.path.join(home, location))
            return usercert, userkey
    
    raise FileNotFoundError("Can't find certificates in default location")

def get_cookies(url, usercert, userkey, verify=True):
    """ Get CERN SSO cookies

        Args:
            url: CERN URL (https://cmsoms.cern.ch)
            usercert: full path to certificate file
            userkey: full path to certificate key file
            verify: should client verify host certificate?
    """

    if verify:
        # Path to CERN CA bundle
        verify = os.path.join(os.path.dirname(__file__), "cern_cacert.pem")

    with requests.Session() as session:
        session.cert = (usercert, userkey)

        # SSO redirects to Auth URL
        redirect = session.get(url, verify=verify)
        redirect.raise_for_status()

        # Auth URL        
        base = urljoin(redirect.url, "auth/sslclient/")
        query = urlparse(redirect.url).query
        auth_url = "{}?{}".format(base, query)

        # Auth response
        auth_resp = session.get(auth_url, verify=verify)
        auth_resp.raise_for_status()

        # Parse login form
        tree = ElementTree.fromstring(auth_resp.content)

        action = tree.findall("body/form")[0].get("action")
        form_data = dict(
            (
                (element.get("name"), element.get("value"))
                for element in tree.findall("body/form/input")
            )
        )
        
        session.post(url=action, data=form_data, verify=verify)

        return session.cookies
