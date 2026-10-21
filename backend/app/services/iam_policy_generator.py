"""
IAM Policy Generator - Creates region-aware IAM policies for Bedrock access.

Uses BedrockModelResolver to determine correct geographic prefix.
"""

import json
from typing import Optional
from dataclasses import dataclass

from app.services.bedrock_resolver import BedrockModelResolver, RegionPrefix, get_resolver


@dataclass(frozen=True)
class IAMPolicyStatement:
    sid: str
    effect: str
    action: list[str]
    resource: list[str]
    condition: Optional[dict] = None


@dataclass(frozen=True)
class IAMPolicy:
    version: str = "2012-10-17"
    statement: list[IAMPolicyStatement] = None

    def to_json(self, indent: int = 2) -> str:
        return json.dumps({
            "Version": self.version,
            "Statement": [
                {
                    "Sid": stmt.sid,
                    "Effect": stmt.effect,
                    "Action": stmt.action,
                    "Resource": stmt.resource,
                    **({"Condition": stmt.condition} if stmt.condition else {})
                }
                for stmt in (self.statement or [])
            ]
        }, indent=indent)


class IAMPolicyGenerator:
    """Generates IAM policies for Bedrock access with region-aware prefixes."""

    def __init__(self, resolver: Optional[BedrockModelResolver] = None):
        self.resolver = resolver or get_resolver()

    def generate_bedrock_policy(
        self,
        region: str,
        role_arn: str,
        include_foundation_models: bool = True,
        include_inference_profiles: bool = True,
        include_cross_region: bool = True,
    ) -> IAMPolicy:
        """
        Generate IAM policy for Bedrock access in a specific region.

        Args:
            region: AWS region (e.g., ap-southeast-2)
            role_arn: IAM role ARN for the policy
            include_foundation_models: Include foundation model permissions
            include_inference_profiles: Include inference profile permissions
            include_cross_region: Include cross-region inference profile permissions

        Returns:
            IAMPolicy object that can be serialized to JSON
        """
        prefix = self.resolver.get_prefix_for_region(region)
        prefix_str = prefix.value

        statements = []

        # Bedrock invoke permissions
        actions = [
            "bedrock:InvokeModel",
            "bedrock:InvokeModelWithResponseStream",
        ]

        resources = []

        if include_foundation_models:
            # Foundation model ARNs
            resources.append(f"arn:aws:bedrock:{region}::foundation-model/anthropic.*")

        if include_inference_profiles:
            # Inference profile ARNs - region-specific prefix
            resources.append(f"arn:aws:bedrock:{region}::inference-profile/{prefix_str}.anthropic.*")

        if include_cross_region and prefix != RegionPrefix.US:
            # Cross-region inference profiles for non-US regions
            resources.append(f"arn:aws:bedrock:{region}::inference-profile/{prefix_str}.anthropic.*")

        # Add the invoke statement
        statements.append(IAMPolicyStatement(
            sid="BedrockInvokeAccess",
            effect="Allow",
            action=actions,
            resource=resources,
        ))

        # Add model listing permissions
        statements.append(IAMPolicyStatement(
            sid="BedrockListAccess",
            effect="Allow",
            action=[
                "bedrock:ListFoundationModels",
                "bedrock:ListInferenceProfiles",
                "bedrock:GetFoundationModel",
                "bedrock:GetInferenceProfile",
            ],
            resource=["*"],
        ))

        # STS AssumeRole for cross-account if needed
        statements.append(IAMPolicyStatement(
            sid="STSAssumeRole",
            effect="Allow",
            action=["sts:AssumeRole"],
            resource=[role_arn],
            condition={
                "StringEquals": {
                    "sts:ExternalId": "nexus-studio-bedrock"
                }
            } if "nexus-studio" not in role_arn else None,
        ))

        return IAMPolicy(statement=statements)

    def generate_policy_for_setup_wizard(
        self,
        region: str,
        role_arn: str,
    ) -> str:
        """
        Generate policy JSON for the setup wizard.

        This is the policy template that should be used in the wizard
        instead of hardcoding 'us.anthropic.*'.
        """
        policy = self.generate_bedrock_policy(
            region=region,
            role_arn=role_arn,
            include_foundation_models=True,
            include_inference_profiles=True,
            include_cross_region=True,
        )
        return policy.to_json()


# Convenience function for wizard integration
def generate_wizard_iam_policy(region: str, role_arn: str) -> str:
    """Generate IAM policy for the Bedrock setup wizard."""
    generator = IAMPolicyGenerator()
    return generator.generate_policy_for_setup_wizard(region, role_arn)