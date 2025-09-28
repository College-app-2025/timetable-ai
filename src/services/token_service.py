# The one for testing

from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import Optional, Dict, Any
import secrets
from src.utils.logger_config import get_logger

logger = get_logger("token_service")

class TokenService:
    def __init__(self):
        # Security recommendations from research
        self.SECRET_KEY = "Pappu_@_12340"  # TODO: Use environment variable
        self.ALGORITHM = "HS256"
        
        # Token expiry times based on best practices
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 15    # Short-lived (15 minutes)
        self.REFRESH_TOKEN_EXPIRE_DAYS = 7       # Longer-lived (7 days)
        
        # Optional: Store active refresh tokens (for revocation)
        self.active_refresh_tokens = set()

        logger.info("TokenService initialized for prototype")

    async def create_access_token(self, user_data: dict, expires_delta: Optional[timedelta] = None):
        """Create a short-lived access token"""
        to_encode = user_data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),  # Issued at time
            "type": "access"  # Token type identifier
        })

        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        logger.debug(f"Access token created for user: {user_data.get('sub', 'unknown')}")
        return encoded_jwt

    async def create_refresh_token(self, user_data: dict, expires_delta: Optional[timedelta] = None):
        """Create a long-lived refresh token"""
        to_encode = user_data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
            
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",  # Token type identifier
            "jti": secrets.token_urlsafe(32)  # Unique token ID for revocation
        })

        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        logger.debug(f"Refresh token created for user: {user_data.get('sub', 'unknown')}")

        # Store for potential revocation (optional - can be stored in database)
        self.active_refresh_tokens.add(encoded_jwt)
        
        return encoded_jwt
    
    async def verify_token_type(self, token : str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
                
            if payload.get("type") == "access":
                return "access"
            
            if payload.get("type") == "refresh":
                return "refresh"
            
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")   
        
        
        

    async def verify_access_token(self, token: str) -> Dict[Any, Any]:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token: missing subject")
            
            logger.debug(f"Access token verified for user: {username}")
                
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Access token expired")
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    async def verify_refresh_token(self, token: str) -> Dict[Any, Any]:
        """Verify and decode refresh token"""
        try:
            # Check if token is still active (not revoked)
            if token not in self.active_refresh_tokens:
                raise HTTPException(status_code=401, detail="Refresh token revoked or invalid")
            
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token: missing subject")
            
            logger.debug(f"Refresh token verified for user: {username}")
                
            return payload
            
        except jwt.ExpiredSignatureError:
            # Remove expired token from active set
            self.active_refresh_tokens.discard(token)
            raise HTTPException(status_code=401, detail="Refresh token expired")
        
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid refresh token: {str(e)}")

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        payload = await self.verify_refresh_token(refresh_token)
        
        user_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email")
        }
        
        new_access_token = await self.create_access_token(user_data)

        logger.info(f"Access token refreshed for user: {user_data.get('sub')}")
        
        return new_access_token
    
    async def refresh_token_rotation(self, old_refresh_token: str) -> Dict[str, str]:
        """Rotate refresh token - more secure approach"""
        try:
            # Verify the old refresh token
            payload = await self.verify_refresh_token(old_refresh_token)
            
            # Remove old token from active set
            self.active_refresh_tokens.discard(old_refresh_token)
            
            # Create user data for new tokens
            user_data = {
                "sub": payload.get("sub"), 
                "email": payload.get("email"),
                "role": payload.get("role")
            }
            
            # Generate new tokens
            new_access_token = await self.create_access_token(user_data)
            new_refresh_token = await self.create_refresh_token(user_data)
            
            logger.info(f"Token rotation completed for user: {user_data.get('sub')}")
            
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer"
            }
            
        except HTTPException as e:
            # If refresh token is expired or invalid, we can still try to decode it
            # for a graceful degraded experience during demo
            if "expired" in str(e.detail).lower():
                try:
                    # Decode without verification to get user data
                    payload = jwt.decode(old_refresh_token, self.SECRET_KEY, 
                                       algorithms=[self.ALGORITHM], options={"verify_exp": False})
                    
                    user_data = {
                        "sub": payload.get("sub"), 
                        "email": payload.get("email"),
                        "institute_id": payload.get("institute_id")
                    }
                    
                    # Generate fresh tokens
                    new_access_token = await self.create_access_token(user_data)
                    new_refresh_token = await self.create_refresh_token(user_data)
                    
                    logger.warning(f"Token rotation with expired token for user: {user_data.get('sub')}")
                    
                    return {
                        "access_token": new_access_token,
                        "refresh_token": new_refresh_token,
                        "token_type": "bearer"
                    }
                except:
                    pass
            
            # Re-raise the original exception
            raise e


    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke a refresh token (logout functionality)"""
        if refresh_token in self.active_refresh_tokens:
            self.active_refresh_tokens.remove(refresh_token)
            logger.info("Refresh token revoked successfully")
            return True
        return False


    async def revoke_all_refresh_tokens_for_user(self, user_id: str):
        """Revoke all refresh tokens for a specific user (security breach response)"""
        tokens_to_remove = []
        for token in self.active_refresh_tokens:
            try:
                payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
                if payload.get("sub") == user_id:
                    tokens_to_remove.append(token)
            except:
                # Invalid token, remove it anyway
                tokens_to_remove.append(token)
        
        for token in tokens_to_remove:
            self.active_refresh_tokens.discard(token)

        logger.info(f"Revoked {len(tokens_to_remove)} tokens for user: {user_id}")    

    async def get_system_status(self) -> Dict[str, Any]:
        """Get token system status - great for demo dashboard"""
        return {
            "active_refresh_tokens_count": len(self.active_refresh_tokens),
            "algorithm": self.ALGORITHM,
            "access_token_expire_minutes": self.ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": self.REFRESH_TOKEN_EXPIRE_DAYS,
            "status": "active"
        }    

# Create singleton instance
token_service = TokenService()


# One for scalability

# from jose import JWTError, jwt
# from datetime import datetime, timedelta
# from fastapi import HTTPException
# from typing import Optional, Dict, Any
# import secrets
# import redis

# class TokenService:
#     def __init__(self):
#         # Security recommendations from research
#         self.SECRET_KEY = "Pappu_@_12340"  # TODO: Use environment variable
#         self.ALGORITHM = "HS256"
        
#         # Token expiry times based on best practices
#         self.ACCESS_TOKEN_EXPIRE_MINUTES = 15    # Short-lived (15 minutes)
#         self.REFRESH_TOKEN_EXPIRE_DAYS = 7       # Longer-lived (7 days)
        
#         # Redis connection for storing active refresh tokens
#         self.redis_client = redis.Redis(
#             host='localhost', 
#             port=6379, 
#             db=0, 
#             decode_responses=True  # Automatically decode bytes to strings
#         )
        
#         # Redis key prefix for refresh tokens
#         self.REDIS_TOKEN_PREFIX = "active_refresh_token:"

#     async def create_access_token(self, user_data: dict, expires_delta: Optional[timedelta] = None):
#         """Create a short-lived access token"""
#         to_encode = user_data.copy()
        
#         if expires_delta:
#             expire = datetime.utcnow() + expires_delta
#         else:
#             expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            
#         to_encode.update({
#             "exp": expire,
#             "iat": datetime.utcnow(),  # Issued at time
#             "type": "access"  # Token type identifier
#         })

#         encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
#         return encoded_jwt

#     async def create_refresh_token(self, user_data: dict, expires_delta: Optional[timedelta] = None):
#         """Create a long-lived refresh token"""
#         to_encode = user_data.copy()
        
#         if expires_delta:
#             expire = datetime.utcnow() + expires_delta
#         else:
#             expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
            
#         to_encode.update({
#             "exp": expire,
#             "iat": datetime.utcnow(),
#             "type": "refresh",  # Token type identifier
#             "jti": secrets.token_urlsafe(32)  # Unique token ID for revocation
#         })

#         encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        
#         # Store in Redis with expiration (automatic cleanup)
#         redis_key = f"{self.REDIS_TOKEN_PREFIX}{encoded_jwt}"
#         expiry_seconds = int(timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
        
#         # SETEX sets the key with expiration in one atomic operation
#         self.redis_client.setex(redis_key, expiry_seconds, "active")
        
#         return encoded_jwt

#     async def verify_access_token(self, token: str) -> Dict[Any, Any]:
#         """Verify and decode access token"""
#         try:
#             payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            
#             # Verify token type
#             if payload.get("type") != "access":
#                 raise HTTPException(status_code=401, detail="Invalid token type")
            
#             username: str = payload.get("sub")
#             if username is None:
#                 raise HTTPException(status_code=401, detail="Invalid token: missing subject")
                
#             return payload
            
#         except jwt.ExpiredSignatureError:
#             raise HTTPException(status_code=401, detail="Access token expired")
#         except JWTError as e:
#             raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

#     async def verify_refresh_token(self, token: str) -> Dict[Any, Any]:
#         """Verify and decode refresh token"""
#         try:
#             # Check if token exists in Redis (not revoked)
#             redis_key = f"{self.REDIS_TOKEN_PREFIX}{token}"
#             if not self.redis_client.exists(redis_key):
#                 raise HTTPException(status_code=401, detail="Refresh token revoked or invalid")
            
#             payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            
#             # Verify token type
#             if payload.get("type") != "refresh":
#                 raise HTTPException(status_code=401, detail="Invalid token type")
            
#             username: str = payload.get("sub")
#             if username is None:
#                 raise HTTPException(status_code=401, detail="Invalid token: missing subject")
                
#             return payload
            
#         except jwt.ExpiredSignatureError:
#             # Remove expired token from Redis
#             redis_key = f"{self.REDIS_TOKEN_PREFIX}{token}"
#             self.redis_client.delete(redis_key)
#             raise HTTPException(status_code=401, detail="Refresh token expired")
#         except JWTError as e:
#             raise HTTPException(status_code=401, detail=f"Invalid refresh token: {str(e)}")

#     async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
#         """Generate new access token using refresh token"""
#         # Verify the refresh token
#         payload = await self.verify_refresh_token(refresh_token)
        
#         # Extract user data for new access token
#         user_data = {
#             "sub": payload.get("sub"),
#             "email": payload.get("email")
#         }
        
#         # Generate new access token
#         new_access_token = await self.create_access_token(user_data)
        
#         return {
#             "access_token": new_access_token,
#             "token_type": "bearer"
#         }

#     async def refresh_token_rotation(self, old_refresh_token: str) -> Dict[str, str]:
#         """
#         Refresh token rotation - generates both new access and refresh tokens
#         This is more secure as it invalidates the old refresh token
#         """
#         # Verify the old refresh token
#         payload = await self.verify_refresh_token(old_refresh_token)
        
#         # Remove old refresh token from Redis
#         old_redis_key = f"{self.REDIS_TOKEN_PREFIX}{old_refresh_token}"
#         self.redis_client.delete(old_redis_key)
        
#         # Extract user data
#         user_data = {
#             "sub": payload.get("sub"),
#             "email": payload.get("email")
#         }
        
#         # Generate new tokens
#         new_access_token = await self.create_access_token(user_data)
#         new_refresh_token = await self.create_refresh_token(user_data)
        
#         return {
#             "access_token": new_access_token,
#             "refresh_token": new_refresh_token,
#             "token_type": "bearer"
#         }

#     async def revoke_refresh_token(self, refresh_token: str) -> bool:
#         """Revoke a refresh token (logout functionality)"""
#         redis_key = f"{self.REDIS_TOKEN_PREFIX}{refresh_token}"
#         result = self.redis_client.delete(redis_key)
#         return result > 0  # Returns True if token was deleted, False if didn't exist

#     async def revoke_all_refresh_tokens_for_user(self, user_id: str):
#         """Revoke all refresh tokens for a specific user (security breach response)"""
#         # Use Redis SCAN to find all tokens for the user
#         # This is more efficient than loading all tokens into memory
#         pattern = f"{self.REDIS_TOKEN_PREFIX}*"
        
#         for key in self.redis_client.scan_iter(match=pattern):
#             try:
#                 # Extract token from Redis key
#                 token = key.replace(self.REDIS_TOKEN_PREFIX, "")
#                 payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
                
#                 if payload.get("sub") == user_id:
#                     self.redis_client.delete(key)
                    
#             except JWTError:
#                 # Invalid token, remove it anyway
#                 self.redis_client.delete(key)

# # Create singleton instance
# token_service = TokenService()
