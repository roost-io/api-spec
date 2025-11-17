import os
import re
import yaml
import pytest
import requests
from typing import Dict, Any, Optional, List


def load_config():
    """Load configuration from config.yml file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            # Replace ${var} with environment variables
            config_str = str(config)
            env_vars = re.findall(r'\${([^}]+)}', config_str)
            for var in env_vars:
                if var in os.environ:
                    config_str = config_str.replace(f'${{{var}}}', os.environ[var])
            # Convert back to dict
            return yaml.safe_load(config_str)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration: {e}")


class APIHelper:
    """Helper class for making API requests."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.strip()
    
    def make_request(self, endpoint: str, params: Optional[Dict] = None, 
                     headers: Optional[Dict] = None, method: str = 'GET') -> requests.Response:
        """Make a request to the API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Request headers
            method: HTTP method (GET, POST, etc.)
            
        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=params, headers=headers)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=params, headers=headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")


class APIClient:
    """Simple API client for making requests."""
    
    def __init__(self, api_helper: APIHelper):
        self.api_helper = api_helper
    
    def get(self, endpoint: str, headers: Optional[Dict] = None, params: Optional[Dict] = None) -> requests.Response:
        """Make a GET request."""
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')


class SchemaValidator:
    """Validate JSON responses against schemas."""
    
    def validate_schema_METARproperties(self, data: Dict[str, Any]) -> bool:
        """Validate METARproperties object schema"""
        # No required fields specified in the schema
        required_fields = []
        return all(field in data for field in required_fields)

    def validate_schema_METARtext(self, data: str) -> bool:
        """Validate METARtext schema"""
        # This is a string type schema, no required fields to check
        return isinstance(data, str)

    def validate_schema_METARJSON(self, data: List[Dict[str, Any]]) -> bool:
        """Validate METARJSON schema"""
        if not isinstance(data, list):
            return False
        # Each item should be validated against METARproperties
        for item in data:
            if not self.validate_schema_METARproperties(item):
                return False
        return True

    def validate_schema_METARGeoJSON(self, data: Dict[str, Any]) -> bool:
        """Validate METARGeoJSON schema"""
        required_fields = ['type', 'features']
        if not all(field in data for field in required_fields):
            return False
        
        # Validate features
        for feature in data.get('features', []):
            feature_required = ['type', 'id', 'properties', 'geometry']
            if not all(field in feature for field in feature_required):
                return False
            
            # Validate properties (METARproperties)
            if not self.validate_schema_METARproperties(feature.get('properties', {})):
                return False
            
            # Validate geometry
            geometry = feature.get('geometry', {})
            geometry_required = ['type', 'coordinates']
            if not all(field in geometry for field in geometry_required):
                return False
        
        return True

    def validate_schema_METARXML(self, data: Dict[str, Any]) -> bool:
        """Validate METARXML schema"""
        required_fields = ['request_index', 'data_source', 'request', 'time_taken_ms', 'data']
        return all(field in data for field in required_fields)

    def validate_schema_TAFproperties(self, data: Dict[str, Any]) -> bool:
        """Validate TAFproperties object schema"""
        # No required fields specified in the schema
        required_fields = []
        return all(field in data for field in required_fields)

    def validate_schema_TAFtext(self, data: str) -> bool:
        """Validate TAFtext schema"""
        # This is a string type schema, no required fields to check
        return isinstance(data, str)

    def validate_schema_TAFJSON(self, data: List[Dict[str, Any]]) -> bool:
        """Validate TAFJSON schema"""
        if not isinstance(data, list):
            return False
        # Each item should be validated against TAFproperties
        for item in data:
            if not self.validate_schema_TAFproperties(item):
                return False
        return True

    def validate_schema_TAFGeoJSON(self, data: Dict[str, Any]) -> bool:
        """Validate TAFGeoJSON schema"""
        required_fields = ['type', 'features']
        if not all(field in data for field in required_fields):
            return False
        
        # Validate features
        for feature in data.get('features', []):
            feature_required = ['type', 'id', 'properties', 'geometry']
            if not all(field in feature for field in feature_required):
                return False
            
            # Validate properties (TAFproperties)
            if not self.validate_schema_TAFproperties(feature.get('properties', {})):
                return False
            
            # Validate geometry
            geometry = feature.get('geometry', {})
            geometry_required = ['type', 'coordinates']
            if not all(field in geometry for field in geometry_required):
                return False
        
        return True

    def validate_schema_PIREPtext(self, data: str) -> bool:
        """Validate PIREPtext schema"""
        # This is a string type schema, no required fields to check
        return isinstance(data, str)

    def validate_schema_PIREPJSON(self, data: List[Dict[str, Any]]) -> bool:
        """Validate PIREPJSON schema"""
        if not isinstance(data, list):
            return False
        # No specific required fields to check for each item
        return True

    def validate_schema_PIREPGeoJSON(self, data: Dict[str, Any]) -> bool:
        """Validate PIREPGeoJSON schema"""
        required_fields = ['type', 'features']
        return all(field in data for field in required_fields)

    def validate_schema_PIREPXML(self, data: Dict[str, Any]) -> bool:
        """Validate PIREPXML schema"""
        required_fields = ['request_index', 'data_source', 'request', 'time_taken_ms', 'data']
        return all(field in data for field in required_fields)

    def validate_schema_StationInfoJSON(self, data: List[Dict[str, Any]]) -> bool:
        """Validate StationInfoJSON schema"""
        if not isinstance(data, list):
            return False
        # No specific required fields to check for each item
        return True

    def validate_schema_StationInfoGeoJSON(self, data: Dict[str, Any]) -> bool:
        """Validate StationInfoGeoJSON schema"""
        required_fields = ['type', 'features']
        return all(field in data for field in required_fields)

    def validate_schema_StationInfoXML(self, data: Dict[str, Any]) -> bool:
        """Validate StationInfoXML schema"""
        required_fields = ['request_index', 'data_source', 'request', 'time_taken_ms', 'data']
        return all(field in data for field in required_fields)

    def validate_schema_CloudInfo(self, data: List[Dict[str, Any]]) -> bool:
        """Validate CloudInfo schema"""
        if not isinstance(data, list):
            return False
        
        for cloud in data:
            required_fields = ['cover', 'base']
            if not all(field in cloud for field in required_fields):
                return False
        
        return True

    def validate_schema_AirSigmetJSON(self, data: List[Dict[str, Any]]) -> bool:
        """Validate AirSigmetJSON schema"""
        if not isinstance(data, list):
            return False
        # No specific required fields to check for each item
        return True

    def validate_schema_AirSigmetGeoJSON(self, data: Dict[str, Any]) -> bool:
        """Validate AirSigmetGeoJSON schema"""
        required_fields = ['type', 'features']
        return all(field in data for field in required_fields)

    def validate_schema_ISigmetJSON(self, data: List[Dict[str, Any]]) -> bool:
        """Validate ISigmetJSON schema"""
        if not isinstance(data, list):
            return False
        # No specific required fields to check for each item
        return True

    def validate_schema_ISigmetGeoJSON(self, data: Dict[str, Any]) -> bool:
        """Validate ISigmetGeoJSON schema"""
        required_fields = ['type', 'features']
        return all(field in data for field in required_fields)

    def validate_schema_GairmetJSON(self, data: List[Dict[str, Any]]) -> bool:
        """Validate GairmetJSON schema"""
        if not isinstance(data, list):
            return False
        # No specific required fields to check for each item
        return True

    def validate_schema_GairmetGeoJSON(self, data: Dict[str, Any]) -> bool:
        """Validate GairmetGeoJSON schema"""
        required_fields = ['type', 'features']
        return all(field in data for field in required_fields)

    def validate_schema_AirmetJSON(self, data: List[Dict[str, Any]]) -> bool:
        """Validate AirmetJSON schema"""
        if not isinstance(data, list):
            return False
        # No specific required fields to check for each item
        return True

    def validate_schema_AirmetGeoJSON(self, data: Dict[str, Any]) -> bool:
        """Validate AirmetGeoJSON schema"""
        required_fields = ['type', 'features']
        return all(field in data for field in required_fields)

    def validate_schema_CwaJSON(self, data: List[Dict[str, Any]]) -> bool:
        """Validate CwaJSON schema"""
        if not isinstance(data, list):
            return False
        # No specific required fields to check for each item
        return True

    def validate_schema_CwaGeoJSON(self, data: Dict[str, Any]) -> bool:
        """Validate CwaGeoJSON schema"""
        required_fields = ['type', 'features']
        return all(field in data for field in required_fields)

    def validate_schema_TcfGeoJSON(self, data: Dict[str, Any]) -> bool:
        """Validate TcfGeoJSON schema"""
        required_fields = ['type', 'features', 'issueTime']
        return all(field in data for field in required_fields)

    def validate_schema_ErrorJSON(self, data: Dict[str, Any]) -> bool:
        """Validate ErrorJSON schema"""
        required_fields = ['status', 'error']
        return all(field in data for field in required_fields)

    def validate_schema_ErrorXML(self, data: Dict[str, Any]) -> bool:
        """Validate ErrorXML schema"""
        required_fields = ['request_index', 'data_source', 'request', 'errors', 'warnings']
        return all(field in data for field in required_fields)


@pytest.fixture
def config():
    """Load and return the config."""
    return load_config()


@pytest.fixture
def api_helper(config):
    """Create and return an APIHelper instance."""
    return APIHelper(config['api']['host'])


@pytest.fixture
def api_client(api_helper):
    """Create and return an APIClient instance."""
    return APIClient(api_helper)


@pytest.fixture
def valid_api_key(config):
    """Return a valid API key from config."""
    try:
        return config['api']['key']
    except KeyError:
        pytest.skip("API key not found in configuration")


@pytest.fixture
def invalid_api_key():
    """Return an invalid API key for testing error cases."""
    return "invalid_api_key_for_testing_123"


@pytest.fixture
def valid_location():
    """Return a valid test location parameter."""
    return "KORD"  # Chicago O'Hare International Airport


@pytest.fixture
def oauth2_token(config):
    """Return a valid OAuth2 token from config if present."""
    try:
        return config['api']['oauth_token']
    except KeyError:
        pytest.skip("OAuth2 token not found in configuration")


@pytest.fixture
def schema_validator():
    """Return a schema validator instance."""
    return SchemaValidator()
