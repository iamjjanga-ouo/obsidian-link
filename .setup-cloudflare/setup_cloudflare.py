#!/usr/bin/env python3
"""
Cloudflare setup automation script
- Add DNS CNAME record
- Create Single Page Redirection Rule
"""

import os
import re
import sys
from cloudflare import Cloudflare


def get_env_var(name: str) -> str:
    """Get environment variable, exit if not found"""
    value = os.getenv(name)
    if not value:
        print(f"Error: Environment variable {name} is not set.")
        sys.exit(1)
    return value


def validate_zone_id(zone_id: str) -> bool:
    """Validate Zone ID format"""
    # Zone ID is typically a 32-character hexadecimal string
    pattern = r"^[a-f0-9]{32}$"
    return bool(re.match(pattern, zone_id, re.IGNORECASE))


def verify_credentials(client: Cloudflare, zone_id: str) -> None:
    """Verify API credentials and Zone ID"""
    print("Verifying Cloudflare connection...")

    # Validate Zone ID format
    if not validate_zone_id(zone_id):
        print(f"\n❌ Invalid Zone ID format: {zone_id}")
        print("\nZone ID must be a 32-character hexadecimal string.")
        print("Example: 023e105f4ecef8ad9ca31a8372d0c353")
        print("\nHow to find Zone ID:")
        print("1. Log in to Cloudflare Dashboard")
        print("2. Select your domain")
        print("3. Check 'Zone ID' in the 'API' section on the right sidebar")
        sys.exit(1)

    try:
        # Verify Zone (Zone-scoped tokens cannot call user.get())
        zone = client.zones.get(zone_id=zone_id)
        print(f"✓ API Token authentication successful")
        print(f"✓ Zone verified: {zone.name} (ID: {zone.id})")
        print()

    except Exception as e:
        print(f"\n❌ Cloudflare authentication/Zone verification failed:")
        print(f"   {str(e)}")
        print("\nPlease check:")
        print("1. CF_API_TOKEN is correct")
        print("2. CF_ZONE_ID is correct")
        print("3. API Token has the following permissions:")
        print("   - Zone:DNS:Edit")
        print("   - Zone:Single Redirect:Edit (or Zone:Dynamic Redirect:Edit)")
        print("4. Zone ID matches the Zone configured in the API Token")
        sys.exit(1)


def create_dns_record(client: Cloudflare, zone_id: str) -> None:
    """
    Create DNS CNAME record

    Note: CNAME records must point to a hostname.
    For simple redirects, use root domain ('@').
    """
    print("Creating DNS record...")

    # Check for existing record
    existing_records = client.dns.records.list(zone_id=zone_id, name="go", type="CNAME")

    if existing_records.result:
        print(f"CNAME record 'go' already exists: {existing_records.result[0].content}")
        print("Keeping existing record.")
        return

    # Create CNAME record
    # For simple redirect: @ (root domain)
    dns_record = client.dns.records.create(
        zone_id=zone_id,
        name="go",
        type="CNAME",
        content="@",  # Root domain
        proxied=True,  # Enable Cloudflare proxy
        ttl=1,  # Auto (1 when proxied=True)
        comment="Obsidian Link redirect subdomain",
    )

    print(f"✓ DNS record created: {dns_record.name} -> {dns_record.content}")


def create_redirect_rule(client: Cloudflare, zone_id: str) -> None:
    """
    Create Single Redirect Rule

    Rule configuration:
    - Name: obsidian-web-link-redirect
    - Condition: Requests to https://go.obsidian-link.com/open*
    - Action: Redirect to obsidian://open/${1} (302)
    - Preserve query string
    """
    print("Creating Redirect Rule...")

    # Check for existing ruleset
    existing_rulesets = client.rulesets.list(zone_id=zone_id)
    redirect_ruleset = None

    for ruleset in existing_rulesets:
        if ruleset.phase == "http_request_dynamic_redirect":
            redirect_ruleset = ruleset
            break

    # Create new rule
    rule_name = "obsidian-web-link-redirect"

    if redirect_ruleset:
        # Add rule to existing ruleset
        # Check if rule with same name already exists
        for rule in redirect_ruleset.rules:
            if rule.description == rule_name:
                print(f"Rule '{rule_name}' already exists.")
                print("Keeping existing rule.")
                return

        # Update ruleset (existing rules + new rule)
        new_rule = {
            "action": "redirect",
            "action_parameters": {
                "from_value": {
                    "status_code": 302,
                    "target_url": {"value": "obsidian://open"},
                    "preserve_query_string": True,
                }
            },
            "expression": '(http.host eq "go.obsidian-link.com" and starts_with(http.request.uri.path, "/open"))',
            "description": rule_name,
            "enabled": True,
        }

        # Get existing rules list
        existing_rules = [
            {
                "action": rule.action,
                "action_parameters": rule.action_parameters,
                "expression": rule.expression,
                "description": rule.description,
                "enabled": rule.enabled,
            }
            for rule in redirect_ruleset.rules
        ]

        # Add new rule at first position (Place at: First)
        updated_rules = [new_rule] + existing_rules

        client.rulesets.update(
            ruleset_id=redirect_ruleset.id,
            zone_id=zone_id,
            rules=updated_rules,
            phase="http_request_dynamic_redirect",
        )

        print(f"✓ Redirect Rule added: {rule_name}")
    else:
        # Create new ruleset
        client.rulesets.create(
            zone_id=zone_id,
            name="Dynamic redirect rules",
            kind="zone",
            phase="http_request_dynamic_redirect",
            rules=[
                {
                    "action": "redirect",
                    "action_parameters": {
                        "from_value": {
                            "status_code": 302,
                            "target_url": {"value": "obsidian://open"},
                            "preserve_query_string": True,
                        }
                    },
                    "expression": '(http.host eq "go.obsidian-link.com" and starts_with(http.request.uri.path, "/open"))',
                    "description": rule_name,
                    "enabled": True,
                }
            ],
        )

        print(f"✓ Redirect Ruleset and Rule created: {rule_name}")


def main():
    """Main function"""
    print("=== Cloudflare Setup Start ===\n")

    # Get environment variables
    api_token = get_env_var("CF_API_TOKEN")
    zone_id = get_env_var("CF_ZONE_ID")

    # Initialize Cloudflare client
    client = Cloudflare(api_token=api_token)

    try:
        # 0. Verify API credentials and Zone
        verify_credentials(client, zone_id)

        # 1. Create DNS record
        create_dns_record(client, zone_id)
        print()

        # 2. Create Redirect Rule
        create_redirect_rule(client, zone_id)
        print()

        print("=== Setup Complete ===")
        print("\nTest with the following URL:")
        print("https://go.obsidian-link.com/open?vault=my-vault&file=test.md")
        print("→ Should redirect to: obsidian://open?vault=my-vault&file=test.md")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
