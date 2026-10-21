import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "nexus-studio"


class TestBedrockResolver:
    def test_resolve_us_region(self, client):
        response = client.post(
            "/api/v1/bedrock/resolve",
            json={
                "region": "us-east-1",
                "foundation_model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["prefix"] == "us"
        assert "us.anthropic.claude-3-sonnet-20240229-v1:0" in data["inference_profile_id"]

    def test_resolve_eu_region(self, client):
        response = client.post(
            "/api/v1/bedrock/resolve",
            json={
                "region": "eu-west-1",
                "foundation_model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["prefix"] == "eu"
        assert "eu.anthropic.claude-3-sonnet-20240229-v1:0" in data["inference_profile_id"]

    def test_resolve_au_region(self, client):
        response = client.post(
            "/api/v1/bedrock/resolve",
            json={
                "region": "ap-southeast-2",
                "foundation_model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["prefix"] == "au"
        assert "au.anthropic.claude-3-sonnet-20240229-v1:0" in data["inference_profile_id"]
        assert "INFERENCE_PROFILE" in data["inference_types_supported"]
        assert "ON_DEMAND" not in data["inference_types_supported"]

    def test_resolve_apac_region(self, client):
        response = client.post(
            "/api/v1/bedrock/resolve",
            json={
                "region": "ap-northeast-1",
                "foundation_model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["prefix"] == "apac"

    def test_resolve_unknown_region_defaults_to_us(self, client):
        response = client.post(
            "/api/v1/bedrock/resolve",
            json={
                "region": "unknown-region-1",
                "foundation_model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True  # Still valid, just warns
        assert data["prefix"] == "us"
        assert data["error_message"] is not None
        assert "Unknown region" in data["error_message"]

    def test_resolve_unknown_model(self, client):
        response = client.post(
            "/api/v1/bedrock/resolve",
            json={
                "region": "us-east-1",
                "foundation_model_id": "unknown.model.id",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert "Unknown foundation model" in data["error_message"]


class TestIAMPolicyGenerator:
    def test_generate_policy_us_region(self, client):
        response = client.post(
            "/api/v1/bedrock/iam-policy",
            json={
                "region": "us-east-1",
                "role_arn": "arn:aws:iam::123456789012:role/TestRole",
            },
        )
        assert response.status_code == 200
        data = response.json()
        policy = data["policy_json"]
        assert "us.anthropic.*" in policy
        assert "arn:aws:iam::123456789012:role/TestRole" in policy
        assert "BedrockInvokeAccess" in policy

    def test_generate_policy_au_region(self, client):
        response = client.post(
            "/api/v1/bedrock/iam-policy",
            json={
                "region": "ap-southeast-2",
                "role_arn": "arn:aws:iam::123456789012:role/TestRole",
            },
        )
        assert response.status_code == 200
        data = response.json()
        policy = data["policy_json"]
        assert "au.anthropic.*" in policy
        assert "us.anthropic.*" not in policy


class TestPluginValidator:
    def test_validate_hooks_json_valid(self, client, tmp_path):
        # Create valid hooks.json
        hooks_dir = tmp_path / "test-plugin" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "hooks.json").write_text('{"hooks": {}}')

        response = client.post(
            "/api/v1/plugins/validate",
            json={"plugins_root": str(tmp_path)},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["status"] == "passed"
        assert data["results"][0]["validation_type"] == "hooks"

    def test_validate_hooks_json_invalid_array(self, client, tmp_path):
        # Create invalid hooks.json (bare array)
        hooks_dir = tmp_path / "test-plugin" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "hooks.json").write_text("[]")

        response = client.post(
            "/api/v1/plugins/validate",
            json={"plugins_root": str(tmp_path)},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["status"] == "failed"
        assert any("Root must be an object" in e for e in data["results"][0]["errors"])

    def test_validate_mcp_json_valid(self, client, tmp_path):
        mcp_file = tmp_path / "test-plugin" / ".mcp.json"
        mcp_file.parent.mkdir(parents=True)
        mcp_file.write_text('{"connector1": {"url": "https://example.com"}}')

        response = client.post(
            "/api/v1/plugins/validate",
            json={"plugins_root": str(tmp_path)},
        )
        assert response.status_code == 200
        data = response.json()
        mcp_results = [r for r in data["results"] if r["validation_type"] == "mcp"]
        assert len(mcp_results) == 1
        assert mcp_results[0]["status"] == "passed"

    def test_validate_mcp_json_missing_comma(self, client, tmp_path):
        mcp_file = tmp_path / "test-plugin" / ".mcp.json"
        mcp_file.parent.mkdir(parents=True)
        # Missing comma between objects
        mcp_file.write_text('{"connector1": {"url": "https://example.com"}\n"connector2": {"url": "https://example2.com"}}')

        response = client.post(
            "/api/v1/plugins/validate",
            json={"plugins_root": str(tmp_path)},
        )
        assert response.status_code == 200
        data = response.json()
        mcp_results = [r for r in data["results"] if r["validation_type"] == "mcp"]
        assert len(mcp_results) == 1
        assert mcp_results[0]["status"] == "failed"
        assert any("Expecting" in e for e in mcp_results[0]["errors"])

    def test_fix_hooks_json(self, client, tmp_path):
        hooks_dir = tmp_path / "test-plugin" / "hooks"
        hooks_dir.mkdir(parents=True)
        hooks_file = hooks_dir / "hooks.json"
        hooks_file.write_text("[]")

        response = client.post(
            "/api/v1/plugins/fix",
            json={"plugins_root": str(tmp_path)},
        )
        assert response.status_code == 200
        data = response.json()
        # Verify file was fixed
        fixed_content = hooks_file.read_text()
        assert '"hooks": {}' in fixed_content


class TestBootstrapToken:
    def test_bootstrap_flow(self, client):
        response = client.post(
            "/api/v1/bootstrap/token",
            json={
                "bootstrap_url": "https://example.com/bootstrap",
                "client_id": "test-client-id",
                "tenant_id": "test-tenant-id",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "gateway_token" in data
        assert "bootstrap_expires_at" in data
        assert "token_source" in data
        assert data["token_source"] in ["cache", "silent_refresh", "interactive"]


# Unit tests for services (without HTTP)
class TestBedrockResolverUnit:
    def test_get_prefix_for_region(self):
        from app.services.bedrock_resolver import get_resolver, RegionPrefix

        resolver = get_resolver()
        assert resolver.get_prefix_for_region("us-east-1") == RegionPrefix.US
        assert resolver.get_prefix_for_region("eu-west-1") == RegionPrefix.EU
        assert resolver.get_prefix_for_region("ap-southeast-2") == RegionPrefix.AU
        assert resolver.get_prefix_for_region("ap-northeast-1") == RegionPrefix.APAC
        assert resolver.get_prefix_for_region("unknown") == RegionPrefix.US

    def test_resolve_model_au_region(self):
        from app.services.bedrock_resolver import get_resolver, RegionPrefix, InferenceType

        resolver = get_resolver()
        resolution = resolver.resolve_model("ap-southeast-2", "anthropic.claude-3-sonnet-20240229-v1:0")
        assert resolution.is_valid
        assert resolution.prefix == RegionPrefix.AU
        assert resolution.inference_profile_id == "au.anthropic.claude-3-sonnet-20240229-v1:0"
        assert InferenceType.INFERENCE_PROFILE in resolution.inference_types_supported
        assert InferenceType.ON_DEMAND not in resolution.inference_types_supported

    def test_get_iam_policy_prefix(self):
        from app.services.bedrock_resolver import get_resolver

        resolver = get_resolver()
        assert resolver.get_iam_policy_prefix("us-east-1") == "us.anthropic.*"
        assert resolver.get_iam_policy_prefix("eu-west-1") == "eu.anthropic.*"
        assert resolver.get_iam_policy_prefix("ap-southeast-2") == "au.anthropic.*"
        assert resolver.get_iam_policy_prefix("ap-northeast-1") == "apac.anthropic.*"


class TestIAMPolicyGeneratorUnit:
    def test_generate_policy(self):
        from app.services.iam_policy_generator import IAMPolicyGenerator
        from app.services.bedrock_resolver import get_resolver

        generator = IAMPolicyGenerator(get_resolver())
        policy = generator.generate_bedrock_policy("ap-southeast-2", "arn:aws:iam::123456789012:role/TestRole")
        policy_json = policy.to_json()
        assert "au.anthropic.*" in policy_json
        assert "arn:aws:iam::123456789012:role/TestRole" in policy_json
        assert "BedrockInvokeAccess" in policy_json
        assert "BedrockListAccess" in policy_json
        assert "STSAssumeRole" in policy_json


class TestPluginValidatorUnit:
    def test_hooks_validator_valid(self):
        from app.services.plugin_validator import HooksJsonValidator

        validator = HooksJsonValidator()
        is_valid, errors = validator.validate('{"hooks": {}}', "test.json")
        assert is_valid
        assert len(errors) == 0

    def test_hooks_validator_invalid_array(self):
        from app.services.plugin_validator import HooksJsonValidator

        validator = HooksJsonValidator()
        is_valid, errors = validator.validate("[]", "test.json")
        assert not is_valid
        assert any("Root must be an object" in e for e in errors)

    def test_hooks_validator_fix(self):
        from app.services.plugin_validator import HooksJsonValidator

        validator = HooksJsonValidator()
        fixed = validator.fix("[]")
        assert fixed == '{\n  "hooks": {}\n}'

    def test_mcp_validator_valid(self):
        from app.services.plugin_validator import McpJsonValidator

        validator = McpJsonValidator()
        is_valid, errors = validator.validate('{"conn1": {"url": "https://example.com"}}', "test.json")
        assert is_valid
        assert len(errors) == 0

    def test_mcp_validator_missing_comma(self):
        from app.services.plugin_validator import McpJsonValidator

        validator = McpJsonValidator()
        content = '{"conn1": {"url": "https://example.com"}\n"conn2": {"url": "https://example2.com"}}'
        is_valid, errors = validator.validate(content, "test.json")
        assert not is_valid
        fixed = validator.fix(content)
        assert fixed is not None
        # Verify fixed content is valid JSON
        import json
        json.loads(fixed)


class TestBootstrapTokenUnit:
    def test_bootstrap_flow(self):
        from app.services.bootstrap_token import create_bootstrap_config, BootstrapTokenManager

        config = create_bootstrap_config(
            bootstrap_url="https://example.com/bootstrap",
            client_id="test-client",
            tenant_id="test-tenant",
        )
        manager = BootstrapTokenManager(config)
        result = manager.bootstrap_flow()
        assert "gateway_token" in result
        assert "bootstrap_expires_at" in result
        assert "token_source" in result
        assert result["token_source"] == "interactive"  # First call is interactive