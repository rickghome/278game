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
    "environment":          ["consumer", "enterprise", "government"],
    "team_structure":       ["stream_aligned", "platform", "siloed"],
    "build_buy_configure":  ["build", "buy", "configure"],
    "primary_risk":         ["delivery_speed", "technical_debt", "integration",
                             "vendor_lock", "team_capability"],
    "data_architecture":    ["shared_db", "dedicated_dbs"],
    "architecture_pattern": ["monolith", "layered", "client_server",
                             "event_driven", "microservices"],
    "coupling":             ["medium"],
    "testing_coverage":     ["minimal", "standard", "thorough"],
    "deployment_method":    ["big_bang", "rolling", "blue_green", "canary"],
    "rollback_plan":        ["none", "partial", "full"],
    "observability_level":  ["none", "basic", "full"],
    "change_owner":         ["single_person", "shared_pair", "team_owned"],
    "vendor_dependency":    ["low", "medium", "high"],
    "fallback_strategy":    ["none", "manual", "automated"],
    "on_call_coverage":     ["none", "business_hours", "follow_the_sun", "full_24x7"],
    "incident_response":    ["ad_hoc", "runbook", "practiced"],
}

# Architecture tax — upfront cost + velocity modifier applied from Frame 1
# (upfront_cost_consumer, upfront_cost_enterprise, upfront_cost_gov, velocity_multiplier)
# velocity_multiplier < 1.0 means phases cost more (slower delivery)
ARCHITECTURE_TAX = {
    "monolith":      (30_000,  22_000,  18_000, 1.00),  # cheap, no velocity hit — pays later
    "layered":       (50_000,  37_000,  30_000, 0.95),  # small structure cost
    "client_server": (60_000,  45_000,  36_000, 0.92),  # server setup overhead
    "event_driven":  (110_000, 82_000,  66_000, 0.85),  # messaging infra + complexity
    "microservices": (150_000, 112_000, 90_000, 0.80),  # highest coordination overhead
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
            # Phase names match the game arc labels exactly.
            # arch_stress  = Phase 0 (architecture pattern stress test)
            # build        = Phase 1 (org and planning cards)
            # pipeline     = Pipeline Phase (gate decisions)
            # live         = Phase 3 (production incidents)
            # v2_release   = Phase 4 (v2 compounding)
            # scale        = Phase 5 (scale event)
            "arch_stress": 0,
            "build":       0,
            "pipeline":    0,
            "live":        0,
            "v2_release":  0,
            "scale":       0,
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
        "pipeline_gates":  None,
        "postmortem":      None,
        "strategy_change": None,
        "iteration":       1,
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


def calculate_architecture_tax(frame1):
    """
    Calculate upfront architecture tax and velocity modifier.
    Returns (upfront_cost, velocity_multiplier, description).
    """
    pattern = frame1.get("architecture_pattern", "monolith")
    env     = frame1.get("environment", "consumer")
    idx     = ENV_IDX.get(env, 0)
    tax     = ARCHITECTURE_TAX.get(pattern, ARCHITECTURE_TAX["monolith"])
    cost    = tax[idx]
    vel     = tax[3]
    descriptions = {
        "monolith":      "Single deployable unit. Low setup cost. Coupling debt deferred.",
        "layered":       "Structured layers. Small coordination overhead from day one.",
        "client_server": "Central server setup. Bottleneck risk baked in.",
        "event_driven":  "Async messaging infrastructure required before first feature.",
        "microservices": "Service boundaries, API contracts, and orchestration required upfront.",
    }
    return cost, vel, descriptions.get(pattern, "")


def apply_architecture_tax(game_state):
    """Apply architecture tax to game state and print the assessment."""
    f1   = game_state.get("frame1", {})
    cost, vel, desc = calculate_architecture_tax(f1)
    pattern = f1.get("architecture_pattern", "monolith")
    vel_pct = int((1.0 - vel) * 100)

    # Store velocity modifier for phase income calculations
    game_state["velocity_multiplier"] = vel
    game_state["architecture_tax_paid"] = cost

    # Deduct from phase 1 income
    game_state["income"]["arch_stress"] -= cost

    sep = "=" * 50
    print(f"\n{sep}")
    print(f"ARCHITECTURE TAX — assessed at Frame 1")
    print(sep)
    print(f"Pattern:   {pattern}")
    print(f"Tax:       -${cost:,} upfront setup cost")
    if vel_pct > 0:
        print(f"           -{vel_pct}% delivery velocity (all phases)")
    else:
        print(f"           No velocity penalty")
    print(f"\n{desc}")
    if vel_pct > 0:
        print(f"\nThis means every phase baseline is reduced by {vel_pct}%.")
        print(f"You chose {pattern}. That choice has a price from day one.")
    print(sep)


def validate_frame1(profile):
    """
    Validate Frame 1 architecture config.
    Returns (is_valid, errors, warnings).
    """
    errors = []
    warnings = []
    required = ["environment", "team_structure", "build_buy_configure",
                "primary_risk", "data_architecture", "architecture_pattern", "coupling"]

    for field in required:
        e, w = _check_field(profile, field)
        errors.extend(e)
        warnings.extend(w)

    if profile.get("coupling") != "medium":
        errors.append("'coupling' must be 'medium' — this field is fixed.")

    # Foreshadowing warnings
    if profile.get("data_architecture") == "shared_db":
        warnings.append(
            "⚠  shared_db — lower cost, faster to build. "
            "All services share one database."
        )
    if profile.get("team_structure") == "siloed":
        warnings.append("⚠  siloed team structure — high handoff cost.")
    if profile.get("build_buy_configure") == "configure":
        warnings.append("⚠  configure — delivery depends on vendor roadmap decisions.")

    # Architecture-specific warnings
    pattern = profile.get("architecture_pattern", "")
    arch_warnings = {
        "monolith":      "⚠  monolith — coupling debt will surface under change pressure.",
        "event_driven":  "⚠  event_driven — async debugging requires strong observability.",
        "microservices": "⚠  microservices — high coordination cost from sprint one.",
    }
    if pattern in arch_warnings:
        warnings.append(arch_warnings[pattern])

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





# ============================================================
# OUTPUT FORMATTING
# ============================================================

SEP = "=" * 50

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


PHASE_LABELS = {
    "arch_stress": "Architecture Stress",
    "build":       "Build",
    "pipeline":    "Pipeline Gates",
    "live":        "Live",
    "v2_release":  "v2 Release",
    "scale":       "Scale Event",
}


def print_income_summary(game_state):
    print(f"\n{SEP}")
    print(f"FRESHCART INCOME SUMMARY -- {game_state['team_name']}")
    print(SEP)
    total    = 0
    baseline = _baseline(game_state.get("environment", "consumer"))
    for phase_key, amount in game_state["income"].items():
        if amount == 0:
            continue
        label = PHASE_LABELS.get(phase_key, phase_key)
        print(f"  {label:<22}  ${amount:>10,}")
        total += amount
    print(f"  {'':-<35}")
    print(f"  {'Total income':<22}  ${total:>10,}")
    print(f"  {'Trust score':<22}  {game_state['trust_score']}/100")
    env = game_state.get("environment", "consumer")
    trust_label = {
        "consumer":   "Customer Trust",
        "enterprise": "Stakeholder Confidence",
        "government": "Political Capital",
    }.get(env, "Trust")
    print(f"  ({trust_label})")
    print(SEP)


def print_final_summary(game_state):
    sep = "=" * 55
    print(f"\n{sep}")
    print(f"FRESHCART FINAL REPORT -- {game_state['team_name']}")
    print(sep)
    total = sum(game_state["income"].values())
    print(f"Environment:      {game_state.get('environment','?').title()}")
    print(f"Iteration:        {game_state.get('iteration', 1)}")
    print(f"Final income:     ${total:,}")
    print(f"Final trust:      {game_state['trust_score']}/100")
    env = game_state.get("environment","consumer")
    trust_label = {
        "consumer": "Customer Trust",
        "enterprise": "Stakeholder Confidence",
        "government": "Political Capital",
    }.get(env, "Trust")
    print(f"                  ({trust_label})")
    print()
    print("Income by phase:")
    for pk, amt in game_state["income"].items():
        if amt == 0:
            continue
        label = PHASE_LABELS.get(pk, pk)
        print(f"  {label:<22}  ${amt:>10,}")
    print()
    print("Key config choices:")
    f1 = game_state.get("frame1", {})
    f2 = game_state.get("frame2", {})
    f3 = game_state.get("frame3", {})
    pg = game_state.get("pipeline_gates", {})
    for profile, label in [(f1,"Architecture"),(f2,"Pipeline"),(f3,"Operations"),(pg,"Gates")]:
        if not profile:
            continue
        for k, v in profile.items():
            if k not in ("coupling",):
                print(f"  {k}: {v}")
    print()
    cards = game_state.get("cards_fired", [])
    if cards:
        print("Cards that fired:")
        for c in cards:
            d = game_state["decisions"].get(c, "?")
            print(f"  {c} -- option ({d})")
    print(sep)
    print("\nCopy the above and give it to your instructor.")
    print(sep)
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


# ============================================================
# FACILITATOR TRACE
# Full causal explanation per team — hidden from students.
# Print this after game ends to debrief fluently.
# ============================================================

DEBRIEF_PROMPTS = {
    "B1": "Why did Team {team} get a handoff gap? They chose siloed team structure. Ask: 'What would a stream-aligned team have done differently here?'",
    "B2": "Why did Team {team} get vendor promise risk? They chose configure strategy. Ask: 'When you chose configure, what were you assuming about the vendor?'",
    "B3": "Why did Team {team} hit a capability gap? They chose build strategy or team_capability as primary risk. Ask: 'What would you have traded to avoid this?'",
    "B4": "Why did Team {team} hit procurement freeze? Government environment. Ask: 'Was this predictable? What should have been planned for?'",
    "B5": "Why did Team {team} face the speed tax? Speed pressure hits every team. Ask: 'What did you optimize for when you made this decision? What did that cost?'",
    "B6": "Why did Team {team} face a CFO freeze? Hits every team. Ask: 'Which gaps did the freeze expose? Were those gaps a choice or a surprise?'",
    "B7": "Why did Team {team} hit partner team friction? Siloed structure or configure strategy. Ask: 'Who owned this dependency? What would ownership have looked like?'",
    "L1": "Why did Team {team} get the ghost deploy? big_bang deployment + no rollback plan. Ask: 'If you had chosen rolling or canary, what would have been different?'",
    "L1_positive": "Why did Team {team} avoid the ghost deploy? They paid for canary or blue_green deployment. Ask: 'What did that cost in capacity? Was it worth it?'",
    "L2": "Why did Team {team} get the assumption invoice? Delayed from B1 — they shipped the handoff gap. Ask: 'When did this become inevitable? What was the earliest decision point?'",
    "L3": "Why did Team {team} have invisible fire? observability: none or basic. Ask: 'What would you have had to instrument to catch this before the CEO email?'",
    "L3_positive": "Why did Team {team} catch the fulfillment issue early? They paid for full observability. Ask: 'What did that cost? What would it have cost not to have it?'",
    "L4": "Why did Team {team} hit the bus route? single change_owner. Ask: 'What does it mean architecturally to have one person hold all the knowledge?'",
    "L5": "Why did Team {team} face the approval chain? Government environment + ad_hoc incident response. Ask: 'What would practiced incident response have bought you here?'",
    "L6": "Why did Team {team} face VP override? Hits every team — speed pressure is universal. Ask: 'Read back your rationale. Looking at the outcome, was that reasoning sound?'",
    "P1": "Why did Team {team} get the silent passenger? Speed skip seed from B5/L6 + minimal testing. Ask: 'Trace this back — when was the earliest moment this became likely?'",
    "P2": "Why did Team {team} face the ownership gap? L4 seed + siloed structure. Ask: 'Nobody owned the Tracking Service. Whose job was it to notice that?'",
    "P3": "Why did Team {team} face the debt collector? B3 debt seed + build strategy. Ask: 'You knew the debt was accumulating. When would have been the right time to pay it?'",
    "D1": "Why did Team {team} hit DB saturation? shared_db chosen in Frame 1. Ask: 'When you picked shared_db, what were you optimizing for? Did it work out that way?'",
    "V1": "Why did Team {team} face API surprise? L2 patch debt seed + medium/high vendor dependency. Ask: 'This was a vendor decision and a patching decision combined. Which came first?'",
    "V2": "Why did Team {team} face the locked room? configure strategy — vendor roadmap was never theirs to control. Ask: 'What would contractual protection have cost? What did not having it cost?'",
    "G3": "Why did Team {team} face the audit? Government environment + procurement/deployment seeds. Ask: 'Technical risk was low. Process risk was high. What does that tell you about where implementation failures actually live?'",
    "S1": "S1 hits everyone. Outcome tier was {tier}. Ask: 'What was the single most important config decision that produced this outcome?'",
    "S2": "The bill arrives for everyone. Ask: 'Read back your rationale for this decision. Would you make the same call again?'",
    "S3": "Why did Team {team} face political exposure? Government environment + G3 political escalation seed. Ask: 'Canada Phoenix became a political crisis before a technical one. Where did that happen here?'",
}


def print_facilitator_trace(game_state):
    """
    Print full causal trace for this team.
    Hidden from students — run from instructor notebook or separate cell.
    """
    sep = "=" * 60
    team = game_state["team_name"]
    print(f"\n{sep}")
    print(f"FACILITATOR TRACE — {team}")
    print(f"(Do not share with students)")
    print(sep)

    # Config summary
    f1 = game_state.get("frame1", {})
    f2 = game_state.get("frame2", {})
    f3 = game_state.get("frame3", {})
    print("\nCONFIG CHOICES:")
    for k, v in f1.items():
        if k != "coupling": print(f"  {k}: {v}")
    for k, v in f2.items(): print(f"  {k}: {v}")
    for k, v in f3.items(): print(f"  {k}: {v}")

    # Seeds
    seeds = game_state.get("seeds", [])
    print(f"\nSEEDS PLANTED: {seeds if seeds else 'none'}")

    # Cards + rationales
    print("\nCARDS FIRED + TEAM RATIONALE:")
    for cid in game_state.get("cards_fired", []):
        decision = game_state["decisions"].get(cid, "?")
        rationale = game_state["rationales"].get(cid, "no rationale recorded")
        prompt = DEBRIEF_PROMPTS.get(cid, "")
        tier = "?"
        if cid == "S1":
            total = sum(game_state["income"].values())
            base = _baseline(game_state.get("environment","consumer")) * 4
            pct = total / base if base else 0
            tier = "thriving" if pct > 0.9 else "surviving" if pct > 0.7 else "struggling" if pct > 0.4 else "collapsing"
        prompt = prompt.format(team=team, tier=tier)
        print(f"\n  [{cid}] — option ({decision})")
        print(f"  Team said: \"{rationale}\"")
        if prompt:
            print(f"  Ask: {prompt}")

    # Outcome
    total = sum(game_state["income"].values())
    print(f"\nFINAL OUTCOME:")
    print(f"  Income:      ${total:,}")
    print(f"  Trust:       {game_state['trust_score']}/100")
    print(f"  Seeds left:  {seeds}")
    print(sep)


def print_iteration_comparison(game_state_v1, game_state_v2):
    """
    Compare two iterations for the same team.
    Shows what changed, what it cost, and whether the changes worked.
    """
    sep = "=" * 60
    team = game_state_v1["team_name"]
    print(f"\n{sep}")
    print(f"ITERATION COMPARISON — {team}")
    print(sep)

    # Income comparison
    total_v1 = sum(game_state_v1["income"].values())
    total_v2 = sum(game_state_v2["income"].values())
    delta = total_v2 - total_v1
    direction = "▲" if delta > 0 else "▼" if delta < 0 else "—"
    print(f"\nINCOME:")
    print(f"  Iteration 1:  ${total_v1:,}")
    print(f"  Iteration 2:  ${total_v2:,}")
    print(f"  Change:       {direction} ${abs(delta):,}")

    # Trust comparison
    t1 = game_state_v1["trust_score"]
    t2 = game_state_v2["trust_score"]
    print(f"\nTRUST:")
    print(f"  Iteration 1:  {t1}/100")
    print(f"  Iteration 2:  {t2}/100")
    print(f"  Change:       {'▲' if t2>t1 else '▼' if t2<t1 else '—'} {abs(t2-t1)} points")

    # Config changes
    print("\nCONFIG CHANGES:")
    f1_v1 = game_state_v1.get("frame1",{})
    f1_v2 = game_state_v2.get("frame1",{})
    f2_v1 = game_state_v1.get("frame2",{})
    f2_v2 = game_state_v2.get("frame2",{})
    f3_v1 = game_state_v1.get("frame3",{})
    f3_v2 = game_state_v2.get("frame3",{})
    changed = False
    for k in list(f1_v1)+list(f2_v1)+list(f3_v1):
        v1 = {**f1_v1,**f2_v1,**f3_v1}.get(k)
        v2 = {**f1_v2,**f2_v2,**f3_v2}.get(k)
        if v1 != v2:
            print(f"  {k}: {v1} → {v2}")
            changed = True
    if not changed:
        print("  No config changes between iterations.")

    # Cards comparison
    cards_v1 = set(game_state_v1.get("cards_fired",[]))
    cards_v2 = set(game_state_v2.get("cards_fired",[]))
    new_cards = cards_v2 - cards_v1
    avoided = cards_v1 - cards_v2
    if avoided: print(f"\nCards avoided in iteration 2: {avoided}")
    if new_cards: print(f"New cards in iteration 2:     {new_cards}")

    # Reflection vs outcome
    reflection = game_state_v1.get("strategy_change",{})
    if reflection:
        print(f"\nTEAM REFLECTION (before iteration 2):")
        for k,v in reflection.items(): print(f"  {k}: {v}")
        print(f"\nDid the changes work?")
        if delta > 50_000:
            print(f"  ✅  Income improved by ${delta:,}. Changes had measurable impact.")
        elif delta > -50_000:
            print(f"  ⚠  Income roughly flat (${delta:,}). Changes may have been insufficient.")
        else:
            print(f"  ❌  Income dropped by ${abs(delta):,}. Changes may have introduced new problems.")

    print(sep)


# ============================================================
# PIPELINE GATE MECHANICS
# ============================================================

VALID_GATE_VALUES = {
    "unit_test_strategy":  ["full", "happy_path", "skip"],
    "integration_owner":   ["dev_and_qa", "dev_only", "skip"],
    "integration_scope":   ["full", "critical_path", "skip"],
    "staging_fidelity":    ["production_mirror", "partial_mirror", "dev_extended"],
    "uat_owner":           ["business_users", "it_team", "skip"],
    "uat_coverage":        ["full_workflows", "happy_path", "skip"],
    "go_nogo_decision":    ["go", "conditional_go", "no_go"],
}

# Cost per gate choice (Consumer / Enterprise / Government)
GATE_COSTS = {
    "unit_test_strategy": {
        "full":       (20_000, 15_000, 12_000),
        "happy_path": (8_000,  6_000,  5_000),
        "skip":       (0, 0, 0),
    },
    "integration": {
        "dev_and_qa_full":       (40_000, 30_000, 24_000),
        "dev_and_qa_critical":   (20_000, 15_000, 12_000),
        "dev_only_full":         (25_000, 18_000, 15_000),
        "dev_only_critical":     (12_000, 9_000,  7_000),
        "skip":                  (0, 0, 0),
    },
    "staging_fidelity": {
        "production_mirror": (50_000, 37_000, 30_000),
        "partial_mirror":    (20_000, 15_000, 12_000),
        "dev_extended":      (0, 0, 0),
    },
    "uat": {
        "business_full":     (30_000, 22_000, 18_000),
        "business_happy":    (15_000, 11_000, 9_000),
        "it_full":           (15_000, 11_000, 9_000),
        "it_happy":          (8_000,  6_000,  5_000),
        "skip":              (0, 0, 0),
    },
}

# Risk seeds planted by gate shortcuts — surface in Phase 3+
GATE_SEEDS = {
    "unit_skip":             "gate_unit_skipped",
    "unit_happy":            "gate_unit_partial",
    "integration_skip":      "gate_integration_skipped",
    "integration_dev_only":  "gate_integration_weak",
    "staging_dev_extended":  "gate_staging_fake",
    "staging_partial":       "gate_staging_partial",
    "uat_it_team":           "gate_uat_wrong_owner",
    "uat_skip":              "gate_uat_skipped",
    "conditional_go":        "gate_known_issues_shipped",
}

# Bugs caught at each stage (used for cost curve display)
BUG_CATCH_RATE = {
    "unit":        {"full": 0.7,  "happy_path": 0.4,  "skip": 0.0},
    "integration": {"full": 0.6,  "critical_path": 0.3, "skip": 0.0},
    "staging":     {"production_mirror": 0.8, "partial_mirror": 0.4, "dev_extended": 0.1},
    "uat":         {"business_users_full": 0.9, "business_users_happy": 0.5,
                    "it_team_full": 0.3, "it_team_happy": 0.15, "skip": 0.0},
}


def validate_pipeline_gates(gate_profile):
    """Validate pipeline gate config. Returns (is_valid, errors, warnings)."""
    errors = []
    warnings = []
    required = ["unit_test_strategy", "integration_owner", "integration_scope",
                "staging_fidelity", "uat_owner", "uat_coverage", "go_nogo_decision"]
    for field in required:
        val = gate_profile.get(field)
        allowed = VALID_GATE_VALUES.get(field, [])
        if not val:
            errors.append(f"Missing required field: '{field}'")
        elif val not in allowed:
            errors.append(f"'{field}' = '{val}' not valid. Choose: {allowed}")

    # Warnings for risky combinations
    if gate_profile.get("unit_test_strategy") == "skip":
        warnings.append("! Skipping unit tests — bugs that could cost $8k to fix will cost $80k+ in production.")
    if gate_profile.get("integration_owner") == "skip":
        warnings.append("! No integration testing — cross-component failures will reach staging or production.")
    if gate_profile.get("staging_fidelity") == "dev_extended":
        warnings.append("! Staging is dev in disguise — production surprises are likely.")
    if gate_profile.get("uat_owner") == "it_team":
        warnings.append("! IT-run UAT answers 'does it run?' not 'does it do what the business needs?'")
    if gate_profile.get("uat_owner") == "skip":
        warnings.append("! No UAT — business workflow gaps will surface post go-live.")

    return len(errors) == 0, errors, warnings


def calculate_pipeline_costs(gate_profile, environment):
    """Calculate total pipeline costs and seeds planted."""
    idx = ENV_IDX.get(environment, 0)
    total_cost = 0
    seeds_planted = []
    bugs_caught = 0
    cost_breakdown = {}

    # Unit test cost
    unit = gate_profile.get("unit_test_strategy", "skip")
    cost = GATE_COSTS["unit_test_strategy"][unit][idx]
    total_cost += cost
    cost_breakdown["unit_test"] = cost
    bugs_caught += BUG_CATCH_RATE["unit"].get(unit, 0) * 5  # assume 5 latent bugs
    if unit == "skip":
        seeds_planted.append(GATE_SEEDS["unit_skip"])
    elif unit == "happy_path":
        seeds_planted.append(GATE_SEEDS["unit_happy"])

    # Integration cost
    owner = gate_profile.get("integration_owner", "skip")
    scope = gate_profile.get("integration_scope", "skip")
    if owner == "skip" or scope == "skip":
        cost = 0
        seeds_planted.append(GATE_SEEDS["integration_skip"])
    else:
        key = f"{owner}_{scope}".replace("critical_path", "critical")
        cost = GATE_COSTS["integration"].get(key, (0, 0, 0))[idx]
        if owner == "dev_only":
            seeds_planted.append(GATE_SEEDS["integration_dev_only"])
        bugs_caught += BUG_CATCH_RATE["integration"].get(scope, 0) * 3
    total_cost += cost
    cost_breakdown["integration"] = cost

    # Staging cost
    staging = gate_profile.get("staging_fidelity", "dev_extended")
    cost = GATE_COSTS["staging_fidelity"][staging][idx]
    total_cost += cost
    cost_breakdown["staging"] = cost
    if staging == "dev_extended":
        seeds_planted.append(GATE_SEEDS["staging_dev_extended"])
    elif staging == "partial_mirror":
        seeds_planted.append(GATE_SEEDS["staging_partial"])
    bugs_caught += BUG_CATCH_RATE["staging"].get(staging, 0) * 4

    # UAT cost
    uat_owner = gate_profile.get("uat_owner", "skip")
    uat_cov   = gate_profile.get("uat_coverage", "skip")
    if uat_owner == "skip" or uat_cov == "skip":
        cost = 0
        seeds_planted.append(GATE_SEEDS["uat_skip"])
    else:
        key = f"{uat_owner}_{uat_cov}".replace("full_workflows", "full").replace("happy_path", "happy")
        cost = GATE_COSTS["uat"].get(key, (0, 0, 0))[idx]
        if uat_owner == "it_team":
            seeds_planted.append(GATE_SEEDS["uat_wrong_owner"])
        bugs_caught += BUG_CATCH_RATE["uat"].get(
            f"{uat_owner}_{uat_cov}".replace("full_workflows", "full").replace("happy_path", "happy"), 0) * 6
    total_cost += cost
    cost_breakdown["uat"] = cost

    # Go/no-go
    if gate_profile.get("go_nogo_decision") == "conditional_go":
        seeds_planted.append(GATE_SEEDS["conditional_go"])

    return total_cost, seeds_planted, int(bugs_caught), cost_breakdown


def print_pipeline_cost_curve(gate_profile, cost_breakdown, bugs_caught,
                               seeds_planted, environment):
    """Print the pipeline cost curve — makes cheap-early vs expensive-late visible."""
    idx = ENV_IDX.get(environment, 0)
    sep = "=" * 50
    print(f"\n{sep}")
    print("PIPELINE COST SUMMARY")
    print(sep)
    print(f"  Gate 1 Unit test:      ${cost_breakdown.get('unit_test',0):>8,}")
    print(f"  Gate 2 Integration:    ${cost_breakdown.get('integration',0):>8,}")
    print(f"  Gate 3 Staging:        ${cost_breakdown.get('staging',0):>8,}")
    print(f"  Gate 4 UAT:            ${cost_breakdown.get('uat',0):>8,}")
    print(f"  {'':->40}")
    total = sum(cost_breakdown.values())
    print(f"  Total pipeline cost:   ${total:>8,}")
    print(f"\n  Bugs caught in pipeline:  ~{int(bugs_caught)}")
    unknown = max(0, 10 - int(bugs_caught))
    print(f"  Bugs still in system:      {'unknown' if unknown > 0 else '0 (well tested)'}")
    if seeds_planted:
        print(f"\n  Risk flags carried forward:")
        seed_labels = {
            "gate_unit_skipped":       "No unit tests run",
            "gate_unit_partial":       "Unit tests covered happy path only",
            "gate_integration_skipped":"No integration testing",
            "gate_integration_weak":   "Integration tested by dev only",
            "gate_staging_fake":       "Staging was not a production mirror",
            "gate_staging_partial":    "Staging had partial data volume",
            "gate_uat_wrong_owner":    "UAT run by IT, not business users",
            "gate_uat_skipped":        "No UAT performed",
            "gate_known_issues_shipped":"Shipped with known issues (conditional go)",
        }
        for s in seeds_planted:
            print(f"    ! {seed_labels.get(s, s)}")
    print(f"\n  Remember: a bug caught here costs ${total//max(1,int(bugs_caught)):,} avg.")
    prod_cost = total * 8
    print(f"  The same bug in production costs ~${prod_cost//max(1,int(bugs_caught)):,} avg.")
    print(sep)


def print_go_nogo_assessment(gate_profile, seeds_planted, game_state):
    """Print go/no-go readiness assessment."""
    sep = "=" * 50
    decision = gate_profile.get("go_nogo_decision", "go")
    risk_count = len(seeds_planted)

    print(f"\n{sep}")
    print("GO / NO-GO ASSESSMENT")
    print(sep)

    # Readiness score
    score = 100
    if "gate_unit_skipped" in seeds_planted:       score -= 25
    if "gate_unit_partial" in seeds_planted:        score -= 10
    if "gate_integration_skipped" in seeds_planted: score -= 25
    if "gate_integration_weak" in seeds_planted:    score -= 15
    if "gate_staging_fake" in seeds_planted:        score -= 20
    if "gate_staging_partial" in seeds_planted:     score -= 10
    if "gate_uat_wrong_owner" in seeds_planted:     score -= 15
    if "gate_uat_skipped" in seeds_planted:         score -= 25

    status = "GREEN" if score >= 80 else "YELLOW" if score >= 50 else "RED"
    print(f"  Pipeline readiness:  {score}/100  [{status}]")
    print(f"  Risk flags:          {risk_count}")
    print(f"  Your decision:       {decision.upper()}")
    print()

    if decision == "go" and status == "RED":
        print("  ! Going live on RED. Risk flags will compound in production.")
        print("  ! This is the sunk cost trap. The pipeline told you the answer.")
        plant_seed(game_state, "gate_red_light_go")
    elif decision == "go" and status == "YELLOW":
        print("  Conditional green. Some risk flags carried forward.")
    elif decision == "no_go":
        print("  Delaying go-live. Pipeline flags will be addressed.")
        print("  Income penalty: delay cost absorbed. Risk flags cleared.")
        # Clear gate seeds on no_go
        for s in list(game_state.get("seeds", [])):
            if s.startswith("gate_"):
                game_state["seeds"].remove(s)
    elif decision == "conditional_go":
        print("  Shipping with known issues documented.")
        print("  Issues are now in production. They will surface.")

    print(sep)


# Post-mortem questions and assumption mapping
ASSUMPTION_OPTIONS = [
    "speed_over_quality",      # we optimized for delivery speed
    "team_knows_the_system",   # we assumed tribal knowledge was sufficient
    "vendor_will_deliver",     # we trusted the vendor roadmap
    "staging_mirrors_prod",    # we assumed staging was good enough
    "users_will_adapt",        # we assumed users would figure it out
    "debt_can_wait",           # we assumed we could pay down debt later
    "architecture_will_scale", # we assumed the architecture would hold
    "pipeline_gates_are_optional", # we assumed gates were bureaucracy
]

PIPELINE_STAGE_OPTIONS = [
    "architecture_decision",
    "team_structure_choice",
    "frame1_config",
    "unit_test_gate",
    "integration_gate",
    "staging_gate",
    "uat_gate",
    "go_nogo_decision",
    "phase3_live_incident",
    "phase4_v2_release",
]


def print_postmortem_analysis(postmortem_profile, game_state):
    """Print post-mortem analysis — closes the learning loop."""
    sep = "=" * 50
    assumption = postmortem_profile.get("assumption_that_failed", "")
    earliest   = postmortem_profile.get("earliest_catch_point", "")
    lesson     = postmortem_profile.get("one_thing_different", "")

    total = sum(game_state["income"].values())
    base  = _baseline(game_state["environment"]) * 5
    lost  = max(0, base - total)

    print(f"\n{sep}")
    print("POST-MORTEM")
    print(sep)

    # Echo back their primary risk from Frame 1
    f1 = game_state.get("frame1", {})
    primary_risk = f1.get("primary_risk", "unknown")
    arch_pattern = f1.get("architecture_pattern", "unknown")

    print(f"  Your stated primary risk:  {primary_risk}")
    print(f"  Your architecture:         {arch_pattern}")
    print(f"  Total income:              ${total:,}")
    print(f"  Baseline potential:        ${base:,}")
    print(f"  Unrealized value:          ${lost:,}")
    print()
    print(f"  Assumption that failed:    {assumption}")
    print(f"  Earliest catch point:      {earliest}")
    print(f"  One thing different:       {lesson}")
    print()

    # Connect assumption to actual cards that fired
    cards_fired = game_state.get("cards_fired", [])
    seeds       = game_state.get("seeds", [])

    # Check if their stated assumption matches what actually happened
    assumption_card_map = {
        "speed_over_quality":      ["B5","L6","PT1","PT3"],
        "pipeline_gates_are_optional": ["gate_unit_skipped","gate_integration_skipped","gate_uat_skipped"],
        "vendor_will_deliver":     ["B2","V2","V1"],
        "staging_mirrors_prod":    ["PT5","gate_staging_fake"],
        "architecture_will_scale": ["A3","D1","S1"],
        "debt_can_wait":           ["P3","A1","A2"],
        "team_knows_the_system":   ["L4","P2","B1"],
        "users_will_adapt":        ["PT3","gate_uat_wrong_owner"],
    }

    related = assumption_card_map.get(assumption, [])
    evidence = [c for c in related if c in cards_fired or c in seeds]

    if evidence:
        print(f"  Evidence in your game:     {evidence}")
        print(f"  This assumption cost you incidents: {evidence}")
    else:
        print(f"  No direct card evidence — may be a deeper structural assumption.")

    print()
    print(f"  Architecture is a hypothesis.")
    print(f"  Implementation is the test.")
    print(f"  Your test revealed: {assumption}")
    print(sep)
