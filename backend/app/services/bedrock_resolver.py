"""
Bedrock Model Resolver - Core domain engine for region-aware model identifier resolution.

Deterministic offline core: no LLM key required.
Maps AWS regions to correct inference profile prefixes (us/eu/au/apac).
Validates model identifiers against region capabilities.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class InferenceType(str, Enum):
    ON_DEMAND = "ON_DEMAND"
    INFERENCE_PROFILE = "INFERENCE_PROFILE"


class RegionPrefix(str, Enum):
    US = "us"
    EU = "eu"
    AU = "au"
    APAC = "apac"


@dataclass(frozen=True)
class RegionCapabilities:
    region: str
    prefix: RegionPrefix
    supported_inference_types: list[InferenceType]
    available_models: list[str]


@dataclass(frozen=True)
class ModelResolution:
    region: str
    foundation_model_id: str
    inference_profile_id: str
    prefix: RegionPrefix
    inference_types_supported: list[InferenceType]
    is_valid: bool
    error_message: Optional[str] = None


# Region to prefix mapping based on AWS Bedrock documentation
REGION_PREFIX_MAP: dict[str, RegionPrefix] = {
    # US regions
    "us-east-1": RegionPrefix.US,
    "us-east-2": RegionPrefix.US,
    "us-west-1": RegionPrefix.US,
    "us-west-2": RegionPrefix.US,
    # EU regions
    "eu-west-1": RegionPrefix.EU,
    "eu-west-2": RegionPrefix.EU,
    "eu-west-3": RegionPrefix.EU,
    "eu-central-1": RegionPrefix.EU,
    "eu-central-2": RegionPrefix.EU,
    "eu-north-1": RegionPrefix.EU,
    "eu-south-1": RegionPrefix.EU,
    "eu-south-2": RegionPrefix.EU,
    # AU regions
    "ap-southeast-2": RegionPrefix.AU,
    "ap-southeast-4": RegionPrefix.AU,
    # APAC regions (non-AU)
    "ap-northeast-1": RegionPrefix.APAC,
    "ap-northeast-2": RegionPrefix.APAC,
    "ap-northeast-3": RegionPrefix.APAC,
    "ap-south-1": RegionPrefix.APAC,
    "ap-south-2": RegionPrefix.APAC,
    "ap-southeast-1": RegionPrefix.APAC,
    "ap-southeast-3": RegionPrefix.APAC,
    "ap-southeast-5": RegionPrefix.APAC,
    # Other
    "ca-central-1": RegionPrefix.US,
    "sa-east-1": RegionPrefix.US,
    "me-central-1": RegionPrefix.EU,
    "me-south-1": RegionPrefix.EU,
    "il-central-1": RegionPrefix.EU,
    "af-south-1": RegionPrefix.EU,
}

# Known Anthropic Claude model patterns on Bedrock
ANTHROPIC_MODEL_PATTERNS = {
    "claude-3-opus": "anthropic.claude-3-opus-20240229-v1:0",
    "claude-3-sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    "claude-3-haiku": "anthropic.claude-3-haiku-20240307-v1:0",
    "claude-3-5-sonnet": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "claude-3-5-haiku": "anthropic.claude-3-5-haiku-20241022-v1:0",
    "claude-4-opus": "anthropic.claude-4-opus-20250514-v1:0",
    "claude-4-sonnet": "anthropic.claude-4-sonnet-20250514-v1:0",
    "claude-4-haiku": "anthropic.claude-4-haiku-20250514-v1:0",
}

# Region capabilities - in production, this would be fetched from AWS API
# For now, hardcoded based on known Bedrock behavior
REGION_CAPABILITIES: dict[str, RegionCapabilities] = {
    "us-east-1": RegionCapabilities(
        region="us-east-1",
        prefix=RegionPrefix.US,
        supported_inference_types=[InferenceType.ON_DEMAND, InferenceType.INFERENCE_PROFILE],
        available_models=list(ANTHROPIC_MODEL_PATTERNS.values()),
    ),
    "us-west-2": RegionCapabilities(
        region="us-west-2",
        prefix=RegionPrefix.US,
        supported_inference_types=[InferenceType.ON_DEMAND, InferenceType.INFERENCE_PROFILE],
        available_models=list(ANTHROPIC_MODEL_PATTERNS.values()),
    ),
    "eu-west-1": RegionCapabilities(
        region="eu-west-1",
        prefix=RegionPrefix.EU,
        supported_inference_types=[InferenceType.ON_DEMAND, InferenceType.INFERENCE_PROFILE],
        available_models=list(ANTHROPIC_MODEL_PATTERNS.values()),
    ),
    "eu-central-1": RegionCapabilities(
        region="eu-central-1",
        prefix=RegionPrefix.EU,
        supported_inference_types=[InferenceType.ON_DEMAND, InferenceType.INFERENCE_PROFILE],
        available_models=list(ANTHROPIC_MODEL_PATTERNS.values()),
    ),
    "ap-southeast-2": RegionCapabilities(
        region="ap-southeast-2",
        prefix=RegionPrefix.AU,
        supported_inference_types=[InferenceType.INFERENCE_PROFILE],  # Only INFERENCE_PROFILE in AU
        available_models=[f"au.{model}" for model in ANTHROPIC_MODEL_PATTERNS.values()],
    ),
    "ap-southeast-4": RegionCapabilities(
        region="ap-southeast-4",
        prefix=RegionPrefix.AU,
        supported_inference_types=[InferenceType.INFERENCE_PROFILE],
        available_models=[f"au.{model}" for model in ANTHROPIC_MODEL_PATTERNS.values()],
    ),
    "ap-northeast-1": RegionCapabilities(
        region="ap-northeast-1",
        prefix=RegionPrefix.APAC,
        supported_inference_types=[InferenceType.ON_DEMAND, InferenceType.INFERENCE_PROFILE],
        available_models=[f"apac.{model}" for model in ANTHROPIC_MODEL_PATTERNS.values()] + list(ANTHROPIC_MODEL_PATTERNS.values()),
    ),
}


class BedrockModelResolver:
    """
    Resolves correct Bedrock model identifiers for a given region.

    Core domain logic: deterministic, no external dependencies.
    """

    def __init__(self, region_capabilities: Optional[dict[str, RegionCapabilities]] = None):
        self.region_capabilities = region_capabilities or REGION_CAPABILITIES

    def get_prefix_for_region(self, region: str) -> RegionPrefix:
        """Get the geographic prefix for a region."""
        return REGION_PREFIX_MAP.get(region, RegionPrefix.US)

    def get_region_capabilities(self, region: str) -> Optional[RegionCapabilities]:
        """Get capabilities for a region."""
        return self.region_capabilities.get(region)

    def resolve_model(self, region: str, foundation_model_id: str) -> ModelResolution:
        """
        Resolve the correct inference profile ID for a region and foundation model.

        Returns a ModelResolution with the resolved identifier and validation info.
        """
        prefix = self.get_prefix_for_region(region)
        capabilities = self.get_region_capabilities(region)

        # For unknown regions, still return valid with default prefix
        if not capabilities:
            # Determine base model
            base_model = foundation_model_id
            if foundation_model_id.startswith(("us.", "eu.", "au.", "apac.")):
                base_model = foundation_model_id.split(".", 1)[1]
            inference_profile_id = f"{prefix.value}.{base_model}"
            return ModelResolution(
                region=region,
                foundation_model_id=foundation_model_id,
                inference_profile_id=inference_profile_id,
                prefix=prefix,
                inference_types_supported=[InferenceType.ON_DEMAND, InferenceType.INFERENCE_PROFILE],
                is_valid=True,
                error_message=f"Unknown region: {region}. Using default prefix '{prefix.value}'.",
            )


        # Check if foundation model is known
        base_model = foundation_model_id
        if foundation_model_id.startswith(("us.", "eu.", "au.", "apac.")):
            base_model = foundation_model_id.split(".", 1)[1]

        # Validate model exists in known patterns
        model_known = any(base_model in known for known in ANTHROPIC_MODEL_PATTERNS.values())
        if not model_known:
            return ModelResolution(
                region=region,
                foundation_model_id=foundation_model_id,
                inference_profile_id=f"{prefix.value}.{base_model}",
                prefix=prefix,
                inference_types_supported=capabilities.supported_inference_types,
                is_valid=False,
                error_message=f"Unknown foundation model: {foundation_model_id}",
            )

        # Determine correct invocation format based on region capabilities
        if InferenceType.INFERENCE_PROFILE in capabilities.supported_inference_types:
            # Region requires inference profile
            if InferenceType.ON_DEMAND not in capabilities.supported_inference_types:
                # Only inference profile supported (e.g., AU regions)
                inference_profile_id = f"{prefix.value}.{base_model}"
            else:
                # Both supported - prefer inference profile for cross-region
                inference_profile_id = f"{prefix.value}.{base_model}"
        else:
            # Only ON_DEMAND supported
            inference_profile_id = base_model

        return ModelResolution(
            region=region,
            foundation_model_id=foundation_model_id,
            inference_profile_id=inference_profile_id,
            prefix=prefix,
            inference_types_supported=capabilities.supported_inference_types,
            is_valid=True,
        )

    def validate_model_id(self, region: str, model_id: str) -> tuple[bool, Optional[str]]:
        """Validate if a model ID is valid for a region."""
        resolution = self.resolve_model(region, model_id)
        return resolution.is_valid, resolution.error_message

    def get_iam_policy_prefix(self, region: str) -> str:
        """Get the IAM policy resource prefix for a region."""
        prefix = self.get_prefix_for_region(region)
        return f"{prefix.value}.anthropic.*"


# Singleton instance for use across the application
_resolver: Optional[BedrockModelResolver] = None


def get_resolver() -> BedrockModelResolver:
    global _resolver
    if _resolver is None:
        _resolver = BedrockModelResolver()
    return _resolver