import os
import re
import pytest
import requests
import yaml
from pathlib import Path


def load_yaml_config(file_path):
    """Load YAML configuration file"""
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
            return config
    except Exception as e:
        raise ValueError(f"Error loading config file: {str(e)}")


def replace_env_vars(config):
    """Replace ${VAR} placeholders with environment variables"""
    def _replace_env_var(match):
        env_var = match.group(1)
        return os.environ.get(env_var, f"${{{env_var}}}")

    if isinstance(config, dict):
        for key, value in config.items():
            if isinstance(value, (dict, list)):
                config[key] = replace_env_vars(value)
            elif isinstance(value, str):
                config[key] = re.sub(r'\${([^}]+)}', _replace_env_var, value)
    elif isinstance(config, list):
        for i, item in enumerate(config):
            if isinstance(item, (dict, list)):
                config[i] = replace_env_vars(item)
            elif isinstance(item, str):
                config[i] = re.sub(r'\${([^}]+)}', _replace_env_var, item)
    return config


@pytest.fixture(scope="session")
def config():
    """Load configuration from YAML file with environment variable substitution"""
    current_dir = Path(__file__).parent
    config_path = os.path.join(current_dir, "config.yml")
    
    try:
        raw_config = load_yaml_config(config_path)
        processed_config = replace_env_vars(raw_config)
        return processed_config
    except Exception as e:
        pytest.fail(f"Failed to load configuration: {str(e)}")


class ApiHelper:
    def __init__(self, base_url):
        self.base_url = base_url.strip() if base_url else ""
    
    def make_request(self, endpoint, params=None, headers=None, method='GET', json=None, data=None):
        """Make HTTP request to the API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                json=json,
                data=data,
                timeout=30
            )
            return response
        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")


class ApiClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper
    
    def get(self, endpoint, headers=None, params=None):
        """Make GET request"""
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')
    
    def post(self, endpoint, headers=None, params=None, json=None, data=None):
        """Make POST request"""
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='POST', json=json, data=data)
    
    def put(self, endpoint, headers=None, params=None, json=None, data=None):
        """Make PUT request"""
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='PUT', json=json, data=data)
    
    def delete(self, endpoint, headers=None, params=None):
        """Make DELETE request"""
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='DELETE')


@pytest.fixture(scope="session")
def api_helper(config):
    """Create API helper instance"""
    base_url = config.get('api', {}).get('host', '')
    if not base_url:
        pytest.fail("API host URL not found in configuration")
    return ApiHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Create API client instance"""
    return ApiClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Extract valid API key from config"""
    api_key = config.get('api', {}).get('api_key', '')
    if not api_key:
        pytest.fail("Valid API key not found in configuration")
    return api_key


@pytest.fixture(scope="session")
def invalid_api_key():
    """Provide a dummy invalid API key for testing"""
    return "invalid_api_key_for_testing_12345"


@pytest.fixture(scope="session")
def valid_location(config):
    """Provide a test location parameter"""
    location = config.get('test_data', {}).get('location', 'New York')
    return location


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Extract OAuth2 token from config"""
    token = config.get('auth', {}).get('oauth2_token', '')
    if not token:
        pytest.fail("OAuth2 token not found in configuration")
    return token
