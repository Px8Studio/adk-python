"""
Google Cloud Platform Authentication Manager

Handles authentication and credential management for GCP services.

Best Practices:
- Use Application Default Credentials (ADC) for development
- Use Service Accounts for production
- Never commit credentials to version control
- Rotate service account keys regularly
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

import google.auth
from google.auth.credentials import Credentials
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


class GCPAuth:
    """
    Centralized authentication manager for GCP services.
    
    Supports multiple authentication methods:
    1. Application Default Credentials (ADC) - Recommended for dev
    2. Service Account JSON key file
    3. Explicit credentials object
    
    Example:
        >>> auth = GCPAuth()
        >>> credentials = auth.get_credentials()
        >>> project_id = auth.get_project_id()
    """
    
    def __init__(
        self,
        *,
        service_account_path: Optional[Path | str] = None,
        credentials: Optional[Credentials] = None,
        project_id: Optional[str] = None,
    ):
        """
        Initialize authentication manager.
        
        Args:
            service_account_path: Path to service account JSON key file
            credentials: Pre-configured credentials object
            project_id: GCP project ID (auto-detected if not provided)
        """
        self._service_account_path = Path(service_account_path) if service_account_path else None
        self._credentials = credentials
        self._project_id = project_id
        self._cached_credentials: Optional[Credentials] = None
        self._cached_project_id: Optional[str] = None
    
    def get_credentials(self) -> Credentials:
        """
        Get GCP credentials using the configured authentication method.
        
        Priority:
        1. Explicit credentials object
        2. Service account JSON key file
        3. Application Default Credentials
        
        Returns:
            Google Cloud credentials object
        
        Raises:
            ValueError: If no valid credentials can be found
        """
        if self._cached_credentials:
            return self._cached_credentials
        
        # Method 1: Explicit credentials
        if self._credentials:
            logger.info("Using explicitly provided credentials")
            self._cached_credentials = self._credentials
            return self._cached_credentials
        
        # Method 2: Service Account JSON
        if self._service_account_path:
            if not self._service_account_path.exists():
                raise ValueError(
                    f"Service account file not found: {self._service_account_path}"
                )
            
            logger.info(f"Loading credentials from service account: {self._service_account_path.name}")
            self._cached_credentials = service_account.Credentials.from_service_account_file(
                str(self._service_account_path)
            )
            return self._cached_credentials
        
        # Method 3: Application Default Credentials (ADC)
        logger.info("Using Application Default Credentials (ADC)")
        try:
            credentials, project = google.auth.default()
            self._cached_credentials = credentials
            
            # Cache project ID if not explicitly set
            if not self._cached_project_id and project:
                self._cached_project_id = project
            
            return self._cached_credentials
        
        except google.auth.exceptions.DefaultCredentialsError as exc:
            raise ValueError(
                "No valid credentials found. Please authenticate using one of:\n"
                "  1. gcloud auth application-default login\n"
                "  2. Set GOOGLE_APPLICATION_CREDENTIALS environment variable\n"
                "  3. Provide service_account_path or credentials parameter"
            ) from exc
    
    def get_project_id(self) -> str:
        """
        Get GCP project ID.
        
        Priority:
        1. Explicitly configured project_id
        2. From environment variable (GOOGLE_CLOUD_PROJECT)
        3. From credentials (ADC)
        
        Returns:
            GCP project ID
        
        Raises:
            ValueError: If no project ID can be determined
        """
        if self._cached_project_id:
            return self._cached_project_id
        
        # Priority 1: Explicit project ID
        if self._project_id:
            self._cached_project_id = self._project_id
            return self._cached_project_id
        
        # Priority 2: Environment variable
        env_project = os.getenv("GOOGLE_CLOUD_PROJECT")
        if env_project:
            logger.info(f"Using project ID from environment: {env_project}")
            self._cached_project_id = env_project
            return self._cached_project_id
        
        # Priority 3: From ADC
        try:
            _, project = google.auth.default()
            if project:
                logger.info(f"Using project ID from credentials: {project}")
                self._cached_project_id = project
                return self._cached_project_id
        except google.auth.exceptions.DefaultCredentialsError:
            pass
        
        raise ValueError(
            "Project ID not found. Please set it using one of:\n"
            "  1. GOOGLE_CLOUD_PROJECT environment variable\n"
            "  2. project_id parameter\n"
            "  3. gcloud config set project <project-id>"
        )
    
    def validate(self) -> dict[str, str]:
        """
        Validate authentication configuration.
        
        Returns:
            Dict with validation results (project_id, auth_method)
        
        Raises:
            ValueError: If validation fails
        """
        credentials = self.get_credentials()
        project_id = self.get_project_id()
        
        # Determine authentication method
        if self._credentials:
            auth_method = "Explicit credentials object"
        elif self._service_account_path:
            auth_method = f"Service account: {self._service_account_path.name}"
        else:
            auth_method = "Application Default Credentials (ADC)"
        
        logger.info("✓ Authentication validated successfully")
        logger.info(f"  Project ID: {project_id}")
        logger.info(f"  Auth method: {auth_method}")
        logger.info(f"  Credentials type: {type(credentials).__name__}")
        
        return {
            "project_id": project_id,
            "auth_method": auth_method,
            "credentials_type": type(credentials).__name__,
        }
    
    @staticmethod
    def setup_adc_instructions() -> str:
        """
        Get instructions for setting up Application Default Credentials.
        
        Returns:
            Multi-line string with setup instructions
        """
        return """
Application Default Credentials (ADC) Setup:

1. Install Google Cloud SDK:
   https://cloud.google.com/sdk/docs/install

2. Authenticate:
   gcloud auth application-default login

3. Set default project:
   gcloud config set project your-project-id

4. Verify:
   gcloud auth application-default print-access-token

For more information:
https://cloud.google.com/docs/authentication/provide-credentials-adc
"""
    
    @staticmethod
    def create_service_account_instructions() -> str:
        """
        Get instructions for creating a service account.
        
        Returns:
            Multi-line string with setup instructions
        """
        return """
Service Account Setup:

1. Create service account:
   gcloud iam service-accounts create <name> --description="<description>"

2. Grant required roles:
   gcloud projects add-iam-policy-binding <project-id> \\
     --member="serviceAccount:<name>@<project-id>.iam.gserviceaccount.com" \\
     --role="roles/bigquery.dataEditor"

   gcloud projects add-iam-policy-binding <project-id> \\
     --member="serviceAccount:<name>@<project-id>.iam.gserviceaccount.com" \\
     --role="roles/bigquery.jobUser"

   gcloud projects add-iam-policy-binding <project-id> \\
     --member="serviceAccount:<name>@<project-id>.iam.gserviceaccount.com" \\
     --role="roles/storage.admin"

3. Create and download key:
   gcloud iam service-accounts keys create key.json \\
     --iam-account=<name>@<project-id>.iam.gserviceaccount.com

4. Set environment variable:
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

For more information:
https://cloud.google.com/iam/docs/service-accounts-create
"""
