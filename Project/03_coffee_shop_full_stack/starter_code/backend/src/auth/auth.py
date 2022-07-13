import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'udacity-fsnd.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'dev'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    #Check if authorization is in the request
    if 'Authorization' not in request.headers:
        raise AuthError({
            'code':'invalid_header',
            'description':'Authorization header is missing'
            },401)
    #get the token
    auth_header = request.headers['Authorization']
    auth_header_parts = auth_header.split(' ')
    #checking if the test is valid
    if len(auth_header_parts) !=2:
        raise AuthError({
            'code':'invalid_header',
            'description':'The header is malformed'},401)
    
    elif auth_header_parts[0].lower() != 'bearer':
        raise AuthError({
            'code':'invalid_header',
            'description':'Bearer not available'},401)
        
    return auth_header_parts[1]


'''
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    if 'permission' not in payload:
        raise Exception({
                'code': 'Invalid header',
                'description': 'This header doesnt include a header.'
            },401)
    if permission is not payload['permission']:
        raise Exception({
                'code': 'Permission not included',
                'description': 'Not authorized to access this service.'
            })

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    #GET PUBLIC KEY FROM THE AUTH 0 SERVICE
    json_url = urlopen(f'https://{AUTH0_DOMAIN}/well-known/jwks.json')
    jwks = json.loads(json_url.read())

    #GET INFO FROM THE HEADER
    header_to_verify = jwt.get_unverified_header(token)
    #CHOOSING KEYS TO USE
    rsa_key = {}
    if 'kid' not in header_to_verify:
        raise AuthError({
             'code':'invalid_header',
            'description':'The header is malformed'},401)
    
    for key in jwks['keys']:
        if key['kid'] == header_to_verify['kid']:
            rsa_key = {
                'kry' : key['kry'],
                'kid' : key['kid'],
                'use' :  key['use'],
                'n' :   key['n'],
                'e' :   key['e']

            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://'+ AUTH0_DOMAIN + '/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code':'Expired signature',
                'description':'The token has expired'
            },401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'code':'Invalid signature',
                'description':'Invalid signature'
            },401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'This authentication token cannot be parsed .'
            }, 400)
        
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)    

        
    

    
   

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator