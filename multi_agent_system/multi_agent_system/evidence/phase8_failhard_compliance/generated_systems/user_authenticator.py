#!/usr/bin/env python3
"""
Generated Transformer Component: user_authenticator
Handles user authentication and JWT token validation

This component follows the V5.1 harness-compatible Transformer pattern.
"""
import anyio
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
import jwt

from autocoder.components import Transformer


class GeneratedTransformer_user_authenticator(Transformer):
    """
    Handles user authentication and JWT token validation
    
    V5.1 harness-compatible Transformer that processes data from anyio input streams 
    and sends results to anyio output streams.
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        
        # Configuration for JWT authentication
        self.jwt_secret_key = config.get('jwt_secret_key') if config else None
        self.token_expiry = config.get('token_expiry', 3600) if config else 3600
        self.processed_count = 0
        
        if not self.jwt_secret_key:
            self.logger.warning("JWT secret key not configured - authentication will fail")
        
    async def _transform_data(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user authentication and JWT token validation.
        
        Processes authentication requests and validates JWT tokens,
        returning authenticated user context for downstream components.
        """
        self.processed_count += 1
        
        # Extract authentication request from inputs
        auth_request = inputs.get('auth_requests', {})
        
        # Validate required inputs
        if not auth_request:
            return {"error": "No authentication request provided", "processed_by": self.name}
        
        request_type = auth_request.get('type', 'unknown')
        
        try:
            if request_type == 'login':
                return await self._process_login(auth_request)
            elif request_type == 'validate_token':
                return await self._process_token_validation(auth_request)
            elif request_type == 'refresh_token':
                return await self._process_token_refresh(auth_request)
            else:
                return {
                    "error": f"Unknown authentication request type: {request_type}",
                    "processed_by": self.name,
                    "auth_count": self.processed_count
                }
        except Exception as e:
            return {
                "error": f"Authentication failed: {str(e)}",
                "processed_by": self.name,
                "auth_count": self.processed_count
            }
    
    async def _process_login(self, auth_request: Dict[str, Any]) -> Dict[str, Any]:
        """Process user login with credential validation"""
        
        username = auth_request.get('username')
        password = auth_request.get('password')
        
        if not username or not password:
            return {"error": "Username and password required", "processed_by": self.name}
        
        if not self.jwt_secret_key:
            return {"error": "JWT secret key not configured", "processed_by": self.name}
        
        # Simulate user validation (in real implementation, this would check database)
        # For demo purposes, accept any non-empty credentials
        if len(username) > 0 and len(password) >= 4:
            # Generate user context
            user_id = str(abs(hash(username)) % 10000)  # Simple user ID generation
            
            # Create JWT token
            token_payload = {
                'user_id': user_id,
                'username': username,
                'exp': datetime.utcnow() + timedelta(seconds=self.token_expiry),
                'iat': datetime.utcnow(),
                'type': 'access_token'
            }
            
            try:
                token = jwt.encode(token_payload, self.jwt_secret_key, algorithm='HS256')
                
                authenticated_user = {
                    "user_id": user_id,
                    "username": username,
                    "token": token,
                    "token_type": "Bearer",
                    "expires_in": self.token_expiry,
                    "authenticated_at": datetime.utcnow().isoformat(),
                    "is_authenticated": True
                }
                
                return {
                    "authenticated_users": authenticated_user,
                    "processed_by": self.name,
                    "auth_count": self.processed_count
                }
                
            except Exception as e:
                return {"error": f"Token generation failed: {str(e)}", "processed_by": self.name}
        else:
            return {
                "error": "Invalid credentials - username required and password must be at least 4 characters",
                "processed_by": self.name
            }
    
    async def _process_token_validation(self, auth_request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate JWT token and extract user context"""
        
        token = auth_request.get('token')
        if not token:
            return {"error": "Token required for validation", "processed_by": self.name}
        
        if not self.jwt_secret_key:
            return {"error": "JWT secret key not configured", "processed_by": self.name}
        
        try:
            # Remove Bearer prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Validate and decode token
            payload = jwt.decode(token, self.jwt_secret_key, algorithms=['HS256'])
            
            # Extract user context
            authenticated_user = {
                "user_id": payload['user_id'],
                "username": payload['username'],
                "token": token,
                "token_type": "Bearer",
                "validated_at": datetime.utcnow().isoformat(),
                "is_authenticated": True,
                "token_valid": True
            }
            
            return {
                "authenticated_users": authenticated_user,
                "processed_by": self.name,
                "auth_count": self.processed_count
            }
            
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired", "processed_by": self.name}
        except jwt.InvalidTokenError as e:
            return {"error": f"Invalid token: {str(e)}", "processed_by": self.name}
        except Exception as e:
            return {"error": f"Token validation failed: {str(e)}", "processed_by": self.name}
    
    async def _process_token_refresh(self, auth_request: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh JWT token for authenticated user"""
        
        refresh_token = auth_request.get('refresh_token')
        if not refresh_token:
            return {"error": "Refresh token required", "processed_by": self.name}
        
        if not self.jwt_secret_key:
            return {"error": "JWT secret key not configured", "processed_by": self.name}
        
        try:
            # Validate refresh token
            payload = jwt.decode(refresh_token, self.jwt_secret_key, algorithms=['HS256'])
            
            # Generate new access token
            new_payload = {
                'user_id': payload['user_id'],
                'username': payload['username'],
                'exp': datetime.utcnow() + timedelta(seconds=self.token_expiry),
                'iat': datetime.utcnow(),
                'type': 'access_token'
            }
            
            new_token = jwt.encode(new_payload, self.jwt_secret_key, algorithm='HS256')
            
            authenticated_user = {
                "user_id": payload['user_id'],
                "username": payload['username'],
                "token": new_token,
                "token_type": "Bearer",
                "expires_in": self.token_expiry,
                "refreshed_at": datetime.utcnow().isoformat(),
                "is_authenticated": True
            }
            
            return {
                "authenticated_users": authenticated_user,
                "processed_by": self.name,
                "auth_count": self.processed_count
            }
            
        except jwt.ExpiredSignatureError:
            return {"error": "Refresh token has expired", "processed_by": self.name}
        except jwt.InvalidTokenError as e:
            return {"error": f"Invalid refresh token: {str(e)}", "processed_by": self.name}
        except Exception as e:
            return {"error": f"Token refresh failed: {str(e)}", "processed_by": self.name}
