import pytest
from agent.policy import PolicyEngine

@pytest.fixture
def policy():
    # minimal policy engine instance; adjust constructor if needed
    rules = {
        "read_document": {"allow": True},
        "send_email": {"allow": False},
    }
    return PolicyEngine(rules=rules)

def test_policy_allows_known_action(policy):
    assert policy.is_allowed("read_document") is True

def test_policy_denies_restricted_action(policy):
    assert policy.is_allowed("send_email") is False

def test_policy_defaults_to_deny(policy):
    # unknown actions should be denied by default
    assert policy.is_allowed("some_random_action") is False
