"""List all attacks and verify scenario filtering works correctly."""
from attacks import ATTACKS, get_attacks_for_scenario, get_all_categories

print(f"Loaded {len(ATTACKS)} total attacks across {len(get_all_categories())} categories:\n")

# Show all attacks grouped by category
for cat in sorted(get_all_categories()):
    cat_attacks = [a for a in ATTACKS if a["category"] == cat]
    print(f"  [{cat}]")
    for a in cat_attacks:
        targets = ", ".join(a["targets"])
        print(f"    - {a['name']} (targets: {targets})")
    print()

# Verify filtering — each scenario should get exactly 7 attacks
# (4 universal + 3 scenario-specific)
print("--- Attacks per scenario ---")
for scenario in ["secret_keeper", "english_only", "no_code"]:
    matched = get_attacks_for_scenario(scenario)
    print(f"  {scenario}: {len(matched)} attacks")
    assert len(matched) == 7, f"Expected 7 attacks for {scenario}, got {len(matched)}"

print("\nAll checks passed!")
