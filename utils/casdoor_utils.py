import secrets
import requests
from urllib.parse import urlencode
from flask import session, current_app

def get_casdoor_config(role):
    if role == 'teacher':
        return {
            'client_id': current_app.config['CASDOOR_TEACHER_CLIENT_ID'],
            'client_secret': current_app.config['CASDOOR_TEACHER_CLIENT_SECRET'],
            'org_name': current_app.config['CASDOOR_TEACHER_ORG']
        }
    elif role == 'student':
        return {
            'client_id': current_app.config['CASDOOR_STUDENT_CLIENT_ID'],
            'client_secret': current_app.config['CASDOOR_STUDENT_CLIENT_SECRET'],
            'org_name': current_app.config['CASDOOR_STUDENT_ORG']
        }
    elif role == 'developer':
        return {
            'client_id': current_app.config['CASDOOR_DEVELOPER_CLIENT_ID'],
            'client_secret': current_app.config['CASDOOR_DEVELOPER_CLIENT_SECRET'],
            'org_name': current_app.config['CASDOOR_DEVELOPER_ORG']
        }
    else:
        return None

def get_casdoor_auth_url(role='student'):
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    session['login_role'] = role
    
    config = get_casdoor_config(role)
    if not config:
        raise ValueError(f"不支持的登录角色: {role}")
    
    params = {
        'client_id': config['client_id'],
        'response_type': 'code',
        'redirect_uri': current_app.config['CASDOOR_REDIRECT_URI'],
        'scope': 'openid profile email',
        'state': state
    }
    
    if config['org_name']:
        params['org'] = config['org_name']
        
    return f"{current_app.config['CASDOOR_SERVER_URL']}/login/oauth/authorize?{urlencode(params)}"

def get_access_token(code, role):
    config = get_casdoor_config(role)
    
    token_url = f"{current_app.config['CASDOOR_SERVER_URL']}/api/login/oauth/access_token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'code': code,
        'redirect_uri': current_app.config['CASDOOR_REDIRECT_URI']
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def get_user_info(access_token):
    userinfo_url = f"{current_app.config['CASDOOR_SERVER_URL']}/api/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(userinfo_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None