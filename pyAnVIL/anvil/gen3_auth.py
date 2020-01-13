import logging
import requests
from datetime import datetime
from subprocess import Popen, PIPE
from requests.auth import AuthBase

PRODUCTION_TERRA_FENCETOKEN_URL = "https://broad-bond-prod.appspot.com/api/link/v1/fence/accesstoken"
DEVELOPMENT_TERRA_FENCETOKEN_URL = "https://firecloud-orchestration.dsde-dev.broadinstitute.org/api/link/v1/fence/accesstoken"


class AnVILAuthError(Exception):
    """Reports problem accessing terra token."""
    pass


class Gen3TerraAuth(AuthBase):
    """Gen3 auth helper class for use with requests auth.

    Implements requests.auth.AuthBase in order to support JWT authentication.
    Queries terra endpoint for fence access_token.
    Generates access tokens from the provided refresh token file or string.
    Automatically refreshes access tokens when they expire.

    Args:
        terra_auth_url (str): The URL of the terra endpoint.

    Examples:
        This generates the Gen3Auth class pointed at the sandbox commons while
        using the credentials.json downloaded from the commons profile page.

        # prod
        >>> auth = Gen3TerraAuth("https://broad-bond-prod.appspot.com/api/link/v1/fence/accesstoken")
        # staging
        >>> auth = Gen3TerraAuth("https://firecloud-orchestration.dsde-dev.broadinstitute.org/")



    """

    def __init__(self, terra_auth_url=DEVELOPMENT_TERRA_FENCETOKEN_URL, user_email=None):
        """Initializes properties."""
        self._access_token = None
        self._terra_auth_url = terra_auth_url
        assert self._terra_auth_url, "MUST have _terra_auth_url"
        self._user_email = user_email

    def __call__(self, request):
        """Adds authorization header to the request

        This gets called by the python.requests package on outbound requests
        so that authentication can be added.

        Args:
            request (object): The incoming request object

        """
        logging.debug(f'__call__, {request.url} adding Authorization header')
        request.headers["Authorization"] = self._get_auth_value()
        request.register_hook("response", self._handle_401)
        return request

    def _handle_401(self, response, **kwargs):
        """Handles failed requests when authorization failed.

        This gets called after a failed request when an HTTP 401 error
        occurs. This then tries to refresh the access token in the event
        that it expired.

        Args:
            request (object): The failed request object

        """
        if not response.status_code == 401 and not response.status_code == 403:
            return response

        # Free the original connection
        response.content
        response.close()

        # copy the request to resend
        newreq = response.request.copy()

        self._access_token = None
        logging.debug("_handle_401, cleared _access_token, retrying with new token")

        newreq.headers["Authorization"] = self._get_auth_value()

        _response = response.connection.send(newreq, **kwargs)
        _response.history.append(response)
        _response.request = newreq

        return _response

    def _get_auth_value(self):
        """Returns the Authorization header value for the request

        This gets called when added the Authorization header to the request.
        This fetches the access token from the refresh token if the access token is missing.

        """
        if not self._access_token:
            try:
                # get the local access token using gcloud
                cmd = ['gcloud', 'auth', 'print-access-token']
                if self._user_email:
                    cmd.append(self._user_email)

                logging.debug(f"get gcloud_access_token {cmd}")
                p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                gcloud_access_token, stderr = p.communicate()
                gcloud_access_token = gcloud_access_token.decode("utf-8").rstrip()
                assert len(gcloud_access_token) > 0, 'MUST have an access token'
                logging.debug(f"gcloud_access_token {gcloud_access_token}")
                # authenticate to terra, ask for fence/accesstoken
                headers = {'Authorization': f'Bearer {gcloud_access_token}'}
                r = requests.get(self._terra_auth_url, headers=headers)
                assert r.status_code == 200, f'MUST respond with 200 {self._terra_auth_url}'

                terra_access_token = r.json()
                assert len(terra_access_token['token']) > 0, 'MUST have an access token'
                assert len(terra_access_token['expires_at']) > 0, 'MUST have an expires_at '

                expires_at = datetime.fromisoformat(terra_access_token['expires_at'])
                now = datetime.now()
                assert expires_at > now, 'expires_at MUST be in the future'
                logging.debug(f'Terra access token expires in {str(expires_at - now)}')

                self._access_token = terra_access_token['token']
                logging.debug(self._access_token)
            except Exception as e:
                raise AnVILAuthError(
                    "Failed to authenticate to {}\n{}".format(self._terra_auth_url, str(e))
                )

        return "Bearer " + self._access_token
