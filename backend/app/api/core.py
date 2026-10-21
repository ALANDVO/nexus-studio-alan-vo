from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from app.services.bedrock_resolver import get_resolver, ModelResolution, RegionPrefix
from app.services.iam_policy_generator import generate_wizard_iam_policy
from app.services.plugin_validator import PluginValidator, ValidationType, ValidationStatus
from app.services.bootstrap_token import create_bootstrap_config, BootstrapTokenManager
from app.core.config import get_settings
router = APIRouter(prefix="/api/v1", tags=["core"])



# Request/Response models
class BedrockResolveRequest(BaseModel):
    region: str = Field(..., description="AWS region (e.g., ap-southeast-2)")
    foundation_model_id: str = Field(..., description="Foundation model ID (e.g., anthropic.claude-3-sonnet-20240229-v1:0)")


class BedrockResolveResponse(BaseModel):
    region: str
    foundation_model_id: str
    inference_profile_id: str
    prefix: str
    inference_types_supported: list[str]
    is_valid: bool
    error_message: Optional[str] = None


class IAMPolicyRequest(BaseModel):
    region: str = Field(..., description="AWS region")
    role_arn: str = Field(..., description="IAM role ARN")


class IAMPolicyResponse(BaseModel):
    policy_json: str


class PluginValidateRequest(BaseModel):
    plugins_root: str = Field(..., description="Path to plugins root directory")


class PluginValidationResult(BaseModel):
    plugin_name: str
    plugin_version: str
    validation_type: str
    status: str
    file_path: str
    errors: list[str]
    fixed_content: Optional[str] = None


class PluginValidateResponse(BaseModel):
    results: list[PluginValidationResult]


class BootstrapRequest(BaseModel):
    bootstrap_url: str = Field(..., description="Bootstrap endpoint URL")
    client_id: str = Field(..., description="Azure AD client ID")
    tenant_id: str = Field(..., description="Azure AD tenant ID")
    scopes: Optional[list[str]] = None
    account: Optional[str] = None


class BootstrapResponse(BaseModel):
    gateway_token: str
    bootstrap_expires_at: int
    token_source: str
    token_expires_in: int


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "nexus-studio"}


@router.post("/bedrock/resolve", response_model=BedrockResolveResponse)
async def resolve_bedrock_model(request: BedrockResolveRequest):
    """Resolve correct Bedrock model identifier for a region."""
    resolver = get_resolver()
    resolution: ModelResolution = resolver.resolve_model(request.region, request.foundation_model_id)
    return BedrockResolveResponse(
        region=resolution.region,
        foundation_model_id=resolution.foundation_model_id,
        inference_profile_id=resolution.inference_profile_id,
        prefix=resolution.prefix.value,
        inference_types_supported=[t.value for t in resolution.inference_types_supported],
        is_valid=resolution.is_valid,
        error_message=resolution.error_message,
    )


@router.post("/bedrock/iam-policy", response_model=IAMPolicyResponse)
async def generate_iam_policy(request: IAMPolicyRequest):
    """Generate region-aware IAM policy for Bedrock access."""
    policy_json = generate_wizard_iam_policy(request.region, request.role_arn)
    return IAMPolicyResponse(policy_json=policy_json)


@router.post("/plugins/validate", response_model=PluginValidateResponse)
async def validate_plugins(request: PluginValidateRequest):
    """Validate all plugin configuration files."""
    validator = PluginValidator()
    results = validator.validate_all_plugins(Path(request.plugins_root))
    return PluginValidateResponse(
        results=[
            PluginValidationResult(
                plugin_name=r.plugin_name,
                plugin_version=r.plugin_version,
                validation_type=r.validation_type.value,
                status=r.status.value,
                file_path=r.file_path,
                errors=r.errors,
                fixed_content=r.fixed_content,
            )
            for r in results
        ]
    )


@router.post("/plugins/fix", response_model=PluginValidateResponse)
async def fix_plugins(request: PluginValidateRequest):
    """Fix invalid plugin configuration files."""
    validator = PluginValidator()
    results = validator.fix_all_plugins(Path(request.plugins_root), dry_run=False)
    return PluginValidateResponse(
        results=[
            PluginValidationResult(
                plugin_name=r.plugin_name,
                plugin_version=r.plugin_version,
                validation_type=r.validation_type.value,
                status=r.status.value,
                file_path=r.file_path,
                errors=r.errors,
                fixed_content=r.fixed_content,
            )
            for r in results
        ]
    )


@router.post("/bootstrap/token", response_model=BootstrapResponse)
async def bootstrap_token(request: BootstrapRequest):
    """Execute bootstrap flow with automatic token refresh."""
    config = create_bootstrap_config(
        bootstrap_url=request.bootstrap_url,
        client_id=request.client_id,
        tenant_id=request.tenant_id,
        scopes=request.scopes,
    )
    manager = BootstrapTokenManager(config)
    result = manager.bootstrap_flow(request.account)
    return BootstrapResponse(**result)

