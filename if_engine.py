"""
ImplementForge — Game Engine
COSE 278: Implementing Systems — Day 4

Hidden from students. Do not distribute.
Handles all game logic: validation, card selection,
income/trust calculation, seed tracking, facilitator trace.

Income triplets throughout are ordered:
  Consumer / Enterprise / Government
"""

import random 

# ============================================================
# CONSTANTS
# ============================================================

ENV_IDX = {"consumer": 0, "enterprise": 1, "government": 2}

# Baseline income per phase (Consumer / Enterprise / Government)
PHASE_BASELINE = (500_000, 375_000, 300_000)

# Engineering capacity costs for Frame 2 choices
CAPACITY_COSTS = {
    "testing_coverage": {
        "minimal": 5, "standard": 15, "thorough": 30
    },
    "deployment_method": {
        "big_bang": 5, "rolling": 15, "blue_green": 25, "canary": 30
    },
    "rollback_plan": {
        "none": 0, "partial": 10, "full": 20
    },
    "observability_level": {
        "none": 0, "basic": 10, "full": 25
    },
    "change_owner": {
        "single_person": 0, "shared_pair": 10, "team_owned": 20
    },
}
CAPACITY_MAX = 100

# Valid enum values — engine validates against these
VALID_VALUES = {
    "environment":         ["consumer", "enterprise", "government"],
    "team_structure":      ["stream_aligned", "platform", "siloed"],
    "build_buy_configure": ["build", "buy", "configure"],
    "primary_risk":        ["delivery_speed", "technical_debt", "integration",
                            "vendor_lock", "team_capability"],
    "data_architecture":   ["shared_db", "dedicated_dbs"],
    "coupling":            ["medium"],
    "testing_coverage":    ["minimal", "standard", "thorough"],
    "deployment_method":   ["big_bang", "rolling", "blue_green", "canary"],
    "rollback_plan":       ["none", "partial", "full"],
    "observability_level": ["none", "basic", "full"],
    "change_owner":        ["single_person", "shared_pair", "team_owned"],
    "vendor_dependency":   ["low", "medium", "high"],
    "fallback_strategy":   ["none", "manual", "automated"],
    "on_call_coverage":    ["none", "business_hours", "follow_the_sun", "full_24x7"],
    "incident_response":   ["ad_hoc", "runbook", "practiced"],
}

# Severity multipliers applied to baseline income loss
SEVERITY = {
    "none":     0.00,
    "minor":    0.15,
    "major":    0.35,
    "critical": 0.70,
}


# ============================================================
# GAME STATE
# One per team. Passed through all phases.
# ============================================================

def new_game_state(team_name):
    return {
        "team_name":       team_name,
        "environment":     None,
        "phase":           0,
        "income": {
            "phase1": 0,
            "phase2": 0,
            "phase3": 0,
            "phase4": 0,
        },
        "trust_score":     100,
        "seeds":           [],     # planted consequence IDs
        "cards_fired":     [],     # card IDs that have fired
        "decisions":       {},     # card_id -> "a"/"b"/"c"
        "rationales":      {},     # card_id -> rationale string
        "facilitator_trace": [],   # human-readable trace entries
        "frame1":          None,
        "frame2":          None,
        "frame3":          None,
    }


# ============================================================
# VALIDATION
# ============================================================

def _check_field(profile, field, required=True):
    """Validate a single field against allowed values."""
    errors = []
    warnings = []
    if field not in profile:
        if required:
            errors.append(f"Missing required field: '{field}'")
        return errors, warnings
    val = profile[field]
    allowed = VALID_VALUES.get(field, [])
    if allowed and val not in allowed:
        errors.append(
            f"'{field}' = '{val}' is not valid. "
            f"Choose one of: {allowed}"
        )
    return errors, warnings


def validate_frame1(profile):
    """
    Validate Frame 1 architecture config.
    Returns (is_valid, errors, warnings).
    """
    errors = []
    warnings = []
    required = ["environment", "team_structure", "build_buy_configure",
                "primary_risk", "data_architecture", "coupling"]

    for field in required:
        e, w = _check_field(profile, field)
        errors.extend(e)
        warnings.extend(w)

    # Coupling must be medium
    if profile.get("coupling") != "medium":
        errors.append("'coupling' must be 'medium' — this field is fixed.")

    # Foreshadowing warnings (not errors — students choose to ignore or not)
    if profile.get("data_architecture") == "shared_db":
        warnings.append(
            "⚠  shared_db selected — lower cost, faster to build. "
            "Note for later: all services share one database."
        )
    if profile.get("team_structure") == "siloed":
        warnings.append(
            "⚠  siloed team structure — functional departments with handoff boundaries."
        )
    if profile.get("build_buy_configure") == "configure":
        warnings.append(
            "⚠  configure strategy — your delivery depends on vendor roadmap decisions."
        )

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def validate_frame2(profile):
    """
    Validate Frame 2 pipeline config.
    Checks valid values AND engineering capacity hard cap.
    Returns (is_valid, errors, warnings, capacity_used).
    """
    errors = []
    warnings = []
    required = ["testing_coverage", "deployment_method", "rollback_plan",
                "observability_level", "change_owner"]

    for field in required:
        e, w = _check_field(profile, field)
        errors.extend(e)
        warnings.extend(w)

    # Capacity check
    capacity_used = calculate_capacity(profile)
    if capacity_used > CAPACITY_MAX:
        errors.append(
            f"Engineering Capacity exceeded: {capacity_used}/100 units used. "
            f"You are over by {capacity_used - CAPACITY_MAX} units. "
            f"Make tradeoffs before proceeding."
        )

    # Foreshadowing warnings
    if profile.get("rollback_plan") == "none":
        warnings.append(
            "⚠  No rollback plan — if a release fails, there is no recovery path."
        )
    if profile.get("observability_level") == "none":
        warnings.append(
            "⚠  No observability — failures will be invisible until customers report them."
        )
    if profile.get("change_owner") == "single_person":
        warnings.append(
            "⚠  Single change owner — one person holds all deployment knowledge."
        )
    if profile.get("deployment_method") == "big_bang" and profile.get("rollback_plan") == "none":
        warnings.append(
            "⚠  big_bang + no rollback — maximum blast radius with no recovery option."
        )

    is_valid = len(errors) == 0
    return is_valid, errors, warnings, capacity_used


def validate_frame3(profile):
    """
    Validate Frame 3 operations config.
    Returns (is_valid, errors, warnings).
    """
    errors = []
    warnings = []
    required = ["vendor_dependency", "fallback_strategy",
                "on_call_coverage", "incident_response"]

    for field in required:
        e, w = _check_field(profile, field)
        errors.extend(e)
        warnings.extend(w)

    # Foreshadowing warnings
    if profile.get("vendor_dependency") == "high" and profile.get("fallback_strategy") == "none":
        warnings.append(
            "⚠  high vendor dependency + no fallback — a vendor outage has no recovery path."
        )
    if profile.get("on_call_coverage") == "none":
        warnings.append(
            "⚠  No on-call coverage — incidents will be found by customers, not your team."
        )
    if profile.get("incident_response") == "ad_hoc":
        warnings.append(
            "⚠  ad_hoc incident response — whoever is available will coordinate under pressure."
        )

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def calculate_capacity(frame2_profile):
    """Return total engineering capacity units used by Frame 2 choices."""
    total = 0
    for field, costs in CAPACITY_COSTS.items():
        val = frame2_profile.get(field)
        if val in costs:
            total += costs[val]
    return total


# ============================================================
# INCOME HELPERS
# ============================================================

def _baseline(environment):
    """Return phase baseline income for environment."""
    return PHASE_BASELINE[ENV_IDX[environment]]


def _loss(environment, severity_key):
    """Calculate income loss as fraction of phase baseline."""
    base = _baseline(environment)
    return int(base * SEVERITY[severity_key])


def _apply_government_modifiers(environment, trust_delta, income_loss, game_state):
    """Apply government environment modifiers to trust and income."""
    if environment != "government":
        return trust_delta, income_loss
    # Trust decays/recovers at 60% rate
    trust_delta = int(trust_delta * 0.6)
    # Governance dividend: practiced response + full rollback
    frame2 = game_state.get("frame2", {})
    frame3 = game_state.get("frame3", {})
    if (frame3 and frame3.get("incident_response") == "practiced" and
            frame2 and frame2.get("rollback_plan") == "full"):
        trust_delta = int(trust_delta * 0.5)  # half the trust damage
    return trust_delta, income_loss


def _apply_trust_modifier(trust_score, income_loss):
    """Apply trust score modifier to recovery cap (affects future rounds, not current)."""
    if trust_score < 50:
        return income_loss  # no modifier to current loss — affects future recovery
    return income_loss


def update_income(game_state, phase_key, amount):
    """Add amount to phase income. Amount is negative for losses."""
    game_state["income"][phase_key] += amount


def update_trust(game_state, delta):
    """Apply delta to trust score, clamped to 0-100."""
    env = game_state["environment"]
    if env == "government":
        delta = int(delta * 0.6)
    game_state["trust_score"] = max(0, min(100, game_state["trust_score"] + delta))


def plant_seed(game_state, seed_id):
    """Plant a delayed consequence seed."""
    if seed_id not in game_state["seeds"]:
        game_state["seeds"].append(seed_id)


def has_seed(game_state, seed_id):
    """Check if a seed is active."""
    return seed_id in game_state["seeds"]


def count_seeds(game_state):
    """Return number of active seeds."""
    return len(game_state["seeds"])


def severity_escalation(base_severity, game_state, phase):
    """
    Escalate severity based on seed count when entering Phase 3.
    2+ seeds: first card +1 tier. 3+ seeds: first two cards +1 tier.
    """
    if phase < 3:
        return base_severity
    seed_count = count_seeds(game_state)
    tier_order = ["none", "minor", "major", "critical"]
    idx = tier_order.index(base_severity)
    if seed_count >= 2:
        idx = min(idx + 1, len(tier_order) - 1)
    return tier_order[idx]


# ============================================================
# FACILITATOR TRACE
# ============================================================

def add_trace(game_state, card_id, reason, seed_trigger=None,
              severity=None, modifier=None, next_risk=None):
    """Add a facilitator trace entry."""
    entry = {
        "card":         card_id,
        "reason":       reason,
        "seed_trigger": seed_trigger,
        "severity":     severity,
        "modifier":     modifier,
        "next_risk":    next_risk,
    }
    game_state["facilitator_trace"].append(entry)


def print_facilitator_trace(game_state, phase_label):
    """Print facilitator trace for current phase. Hidden from students."""
    sep = "━" * 55
    print(f"\n{sep}")
    print(f"FACILITATOR TRACE — {game_state['team_name']} — {phase_label}")
    print(sep)
    phase_entries = [e for e in game_state["facilitator_trace"]
                     if e.get("phase") == phase_label]
    if not phase_entries:
        entries = game_state["facilitator_trace"][-3:]
    else:
        entries = phase_entries
    for e in entries:
        print(f"Card fired:   {e['card']}")
        print(f"Why:          {e['reason']}")
        if e["seed_trigger"]:
            print(f"Seed trigger: {e['seed_trigger']}")
        if e["severity"]:
            print(f"Severity:     {e['severity']}")
        if e["modifier"]:
            print(f"Modifier:     {e['modifier']}")
        if e["next_risk"]:
            print(f"Next risk:    {e['next_risk']}")
        print()
    active_seeds = game_state["seeds"]
    if active_seeds:
        print(f"Active seeds: {', '.join(active_seeds)}")
    print(f"Trust score:  {game_state['trust_score']}")
    print(sep)


# ============================================================
# OUTPUT FORMATTING
# ============================================================

SEP = "━" * 50

def print_header(team_name, phase_label, income_this_phase, trust_score):
    print(f"\n{SEP}")
    print(f"FRESHCART — {team_name} — {phase_label}")
    print(SEP)
    print(f"Income this phase:  ${income_this_phase:,}")
    print(f"Trust score:        {trust_score}/100")
    print(SEP)


def print_card(card_name, scenario_text, options, flavor_text):
    print(f"\n⚠  INCIDENT — \"{card_name}\"")
    print(f"{SEP}")
    print(scenario_text)
    print(f"\n{flavor_text}")
    print(f"\nDECISION REQUIRED — enter your response in the cell below:")
    for key, text in options.items():
        print(f"  ({key}) {text}")
    print(SEP)


def print_positive(card_name, message, income_protected, trust_note):
    print(f"\n✅ RESILIENCE PAYOFF — \"{card_name}\"")
    print(SEP)
    print(message)
    print(f"Income protected. Loss limited to: ${income_protected:,}")
    print(f"Trust: {trust_note}")
    print(SEP)


def print_consequence(card_name, decision, income_loss, trust_delta,
                      consequence_note=None, seed_planted=None):
    print(f"\n{SEP}")
    print(f"OUTCOME — \"{card_name}\" — option ({decision})")
    print(SEP)
    if income_loss > 0:
        print(f"Income loss:   -${income_loss:,}")
    else:
        print(f"Income impact: none this phase")
    if trust_delta < 0:
        print(f"Trust impact:  {trust_delta} points")
    elif trust_delta > 0:
        print(f"Trust impact:  +{trust_delta} points")
    else:
        print(f"Trust impact:  neutral")
    if consequence_note:
        print(f"\n{consequence_note}")
    if seed_planted:
        print(f"\n🌱 Seed planted: {seed_planted}")
        print(f"   This decision may have consequences later.")
    print(SEP)


def print_income_summary(game_state):
    print(f"\n{SEP}")
    print(f"FRESHCART INCOME SUMMARY — {game_state['team_name']}")
    print(SEP)
    total = 0
    for phase_key, amount in game_state["income"].items():
        label = phase_key.replace("phase", "Phase ")
        baseline = _baseline(game_state["environment"])
        print(f"  {label}:  ${amount:,}  (baseline: ${baseline:,})")
        total += amount
    print(f"\n  Total income:    ${total:,}")
    print(f"  Trust score:     {game_state['trust_score']}/100")
    env = game_state["environment"]
    trust_label = {
        "consumer": "Customer Trust",
        "enterprise": "Stakeholder Confidence",
        "government": "Political Capital"
    }.get(env, "Trust")
    print(f"  ({trust_label})")
    print(SEP)


def print_final_summary(game_state):
    sep = "━" * 55
    print(f"\n{sep}")
    print(f"FRESHCART FINAL REPORT — {game_state['team_name']}")
    print(sep)
    total = sum(game_state["income"].values())
    print(f"Environment:     {game_state['environment'].title()}")
    print(f"Final income:    ${total:,}")
    print(f"Final trust:     {game_state['trust_score']}/100")
    print()
    print("Income by phase:")
    for pk, amt in game_state["income"].items():
        label = pk.replace("phase", "Phase ")
        print(f"  {label}:  ${amt:,}")
    print()
    print("Key config choices:")
    f1 = game_state.get("frame1", {})
    f2 = game_state.get("frame2", {})
    f3 = game_state.get("frame3", {})
    for label, profile in [("Architecture", f1), ("Pipeline", f2), ("Operations", f3)]:
        if profile:
            for k, v in profile.items():
                if k != "coupling":
                    print(f"  {k}: {v}")
    print()
    cards = game_state.get("cards_fired", [])
    if cards:
        print("Cards that fired:")
        for c in cards:
            d = game_state["decisions"].get(c, "?")
            print(f"  {c} — option ({d})")
    print(sep)
    print("\n📋 Copy the above output and give it to your instructor.")
    print(sep)
