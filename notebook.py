# ============================================================
# ImplementForge — FreshCart Under Pressure
# COSE 278: Implementing Systems — Day 4
# ============================================================
#
# This notebook is your team's workspace for the entire game.
# Each cell is a step. Run them in order.
# Do not skip cells.
#
# Your instructor has pre-loaded two files:
#   if_engine.py  — game engine (read-only)
#   if_cards.py   — card library (read-only)
#
# ============================================================


# ============================================================
# CELL 0 — SETUP
# Run this first. Do not modify.
# ============================================================

# Download game files from GitHub
GITHUB_BASE = "https://raw.githubusercontent.com/rickghome/278game/main"

import urllib.request
import os

for filename in ["if_engine.py", "if_cards.py"]:
    url = f"{GITHUB_BASE}/{filename}"
    urllib.request.urlretrieve(url, filename)
    print(f"  ✅  {filename} loaded")

exec(open("if_engine.py").read())
exec(open("if_cards.py").read())

print("\n✅  ImplementForge loaded.")
print("    When you're ready, scroll to CELL 1 and begin.\n")


# ============================================================
# CELL 0b — SAVE / RESTORE
# Run SAVE after each phase to protect against session timeout.
# Run RESTORE if your session dies and you need to continue.
# ============================================================

import pickle

def save_game(game):
    """Save game state to file. Run after each phase."""
    with open('game_state.pkl', 'wb') as f:
        pickle.dump(game, f)
    print(f"💾  Game saved — {game['team_name']} — Phase {game['phase']}")
    print(f"    Income so far: ${sum(game['income'].values()):,}")
    print(f"    Trust: {game['trust_score']}/100")

def restore_game():
    """Restore game state after session timeout."""
    if not os.path.exists('game_state.pkl'):
        print("❌  No saved game found. Start from CELL 1.")
        return None
    with open('game_state.pkl', 'rb') as f:
        game = pickle.load(f)
    print(f"✅  Game restored — {game['team_name']}")
    print(f"    Income so far: ${sum(game['income'].values()):,}")
    print(f"    Trust: {game['trust_score']}/100")
    print(f"    Active seeds: {game['seeds']}")
    print(f"    Continue from where you left off.")
    return game

# To save:  save_game(game)
# To restore after timeout:  game = restore_game()
print("💾  Save/restore functions ready.")
print("    Run save_game(game) after each phase to protect your progress.")


# ============================================================
# CELL 1 — TEAM SETUP
# Enter your team name. Run this cell.
# ============================================================

TEAM_NAME = "Team Name Here"   # ← change this

game = new_game_state(TEAM_NAME)

print(f"✅  Team registered: {TEAM_NAME}")
print(f"    Starting trust score: {game['trust_score']}/100")
print(f"    Scroll to CELL 2 to begin Frame 1.\n")


# ============================================================
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FRAME 1 — ARCHITECTURE CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# You are the implementation team for FreshCart.
# You designed this system in COSE 260. Now you're building it.
#
# Fill out the config object below. Each field has options
# listed as comments. Choose one value per field.
# Run the cell when done.
# ============================================================


# CELL 2 — FRAME 1: ARCHITECTURE CONFIG

system_profile = {

    "environment": "consumer",
    # consumer    — fast market, high volume, volatile trust
    # enterprise  — contract-driven, stable, reputational risk
    # government  — fixed budget, procurement rules, political exposure

    "team_structure": "stream_aligned",
    # stream_aligned  — small teams, end-to-end ownership, low coordination cost
    # platform        — shared services team supporting others
    # siloed          — functional departments, high handoff cost

    "build_buy_configure": "build",
    # build       — we write it ourselves
    # buy         — we purchase a product
    # configure   — we implement a vendor platform

    "primary_risk": "delivery_speed",
    # delivery_speed   — we might be too slow
    # technical_debt   — we might cut corners
    # integration      — our components might not fit together
    # vendor_lock      — we might become too dependent on third parties
    # team_capability  — we might not have the right skills

    "data_architecture": "shared_db",
    # dedicated_dbs  — each service owns its data — higher cost, clean boundaries
    # shared_db      — single shared database — lower cost, faster to build

    "coupling": "medium",            # fixed — do not change this value
}

# --- Validate Frame 1 ---
is_valid, errors, warnings = validate_frame1(system_profile)

if errors:
    print("❌  Frame 1 has errors. Fix before continuing:\n")
    for e in errors:
        print(f"    {e}")
else:
    print("✅  Frame 1 config accepted.\n")
    game["frame1"] = system_profile
    game["environment"] = system_profile["environment"]
    if warnings:
        print("Notices:")
        for w in warnings:
            print(f"  {w}")
    print(f"\n    Environment:      {system_profile['environment']}")
    print(f"    Team structure:   {system_profile['team_structure']}")
    print(f"    Strategy:         {system_profile['build_buy_configure']}")
    print(f"    Primary risk:     {system_profile['primary_risk']}")
    print(f"    Data:             {system_profile['data_architecture']}")
    print(f"\n    Phase 1 baseline income: ${_baseline(system_profile['environment']):,}")
    print(f"\n    Scroll to CELL 3 to begin Phase 1.\n")


# ============================================================
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 1 — BUILD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FreshCart is under construction. Your architecture choices
# are now meeting the reality of building a system.
# ============================================================


# CELL 3 — PHASE 1 CARD
# Run this cell to see which incident fires.

_phase1_cards = select_build_cards(system_profile, game)
_current_card_id = _phase1_cards[0] if _phase1_cards else None

if _current_card_id:
    _card = get_card(_current_card_id)
    game["cards_fired"].append(_current_card_id)
    print_card(
        _card["name"],
        _card["scenario"],
        _card["options"],
        _card["flavor"]
    )
    print(f"\n    Active cards this phase: {_phase1_cards}")
    print(f"    Scroll to CELL 4 to enter your decision.\n")
else:
    print("✅  No incidents this phase. Proceed to Frame 2.")


# CELL 4 — PHASE 1 DECISION
# Enter your decision below. Then run this cell.

decision_rationale = "Enter one sentence explaining why you chose this option"
decision = "a"   # ← change to a, b, or c

# --- Apply decision ---
if not decision_rationale or decision_rationale.startswith("Enter"):
    print("❌  decision_rationale is required. Explain your choice in one sentence.")
elif decision not in ["a", "b", "c"]:
    print("❌  decision must be 'a', 'b', or 'c'.")
elif _current_card_id:
    _card = get_card(_current_card_id)
    game["decisions"][_current_card_id] = decision
    game["rationales"][_current_card_id] = decision_rationale
    _env = game["environment"]
    _idx = ENV_IDX[_env]

    # Calculate income loss
    _loss_triplet = _card["income_loss"].get(decision, (0, 0, 0))
    _income_loss = _loss_triplet[_idx]

    # Apply environment modifier if present
    _modifier = _card.get("environment_modifier", {}).get(_env, 1.0)
    _income_loss = int(_income_loss * _modifier)

    # Trust delta
    _trust_delta = _card["trust_delta"].get(decision, 0)

    # Plant seeds
    _seed = _card.get("seeds", {}).get(decision)
    if _seed:
        plant_seed(game, _seed)

    # Update game state
    _phase_income = _baseline(_env) - _income_loss
    update_income(game, "phase1", _phase_income)
    update_trust(game, _trust_delta)

    # Facilitator trace
    add_trace(
        game,
        card_id=_current_card_id,
        reason=f"Frame 1: {_card['id']} triggered by {system_profile.get('team_structure', '')} / {system_profile.get('build_buy_configure', '')}",
        severity="minor" if _income_loss < 100_000 else "major",
        next_risk=_card.get("seeds", {}).get(decision),
    )
    game["facilitator_trace"][-1]["phase"] = "Phase 1"

    # Print outcome
    _note = _card.get("consequence_notes", {}).get(decision, "")
    print_consequence(_card["name"], decision, _income_loss, _trust_delta,
                      consequence_note=_note,
                      seed_planted=_seed)
    print_income_summary(game)

    # Check for remaining phase 1 cards
    _remaining = _phase1_cards[1:]
    if _remaining:
        print(f"\n    Additional cards this phase: {_remaining}")
        print(f"    Your instructor will run those as discussion cards.")
    print(f"\n    Scroll to CELL 5 when instructed to configure Frame 2.\n")
else:
    print("✅  No card active this phase.")


# ============================================================
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FRAME 2 — PIPELINE CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# You have seen Phase 1. Now configure your pipeline.
# Engineering Capacity hard cap: 100 units.
# See the cost table below before choosing.
# ============================================================


# CELL 5 — FRAME 2: PIPELINE CONFIG

# ┌─────────────────────────────────────────────────────────────┐
# │  ENGINEERING CAPACITY COST TABLE                            │
# │  Total budget: 100 units                                    │
# ├──────────────────────────────┬────────────────┬────────────┤
# │  Choice                      │  Capacity cost │  Speed     │
# ├──────────────────────────────┼────────────────┼────────────┤
# │  testing: minimal            │       5        │  fast      │
# │  testing: standard           │      15        │  moderate  │
# │  testing: thorough           │      30        │  slow      │
# ├──────────────────────────────┼────────────────┼────────────┤
# │  deploy: big_bang            │       5        │  fastest   │
# │  deploy: rolling             │      15        │  moderate  │
# │  deploy: blue_green          │      25        │  moderate  │
# │  deploy: canary              │      30        │  slowest   │
# ├──────────────────────────────┼────────────────┼────────────┤
# │  rollback: none              │       0        │  —         │
# │  rollback: partial           │      10        │  —         │
# │  rollback: full              │      20        │  —         │
# ├──────────────────────────────┼────────────────┼────────────┤
# │  observability: none         │       0        │  —         │
# │  observability: basic        │      10        │  —         │
# │  observability: full         │      25        │  —         │
# ├──────────────────────────────┼────────────────┼────────────┤
# │  change_owner: single_person │       0        │  —         │
# │  change_owner: shared_pair   │      10        │  —         │
# │  change_owner: team_owned    │      20        │  —         │
# └──────────────────────────────┴────────────────┴────────────┘

pipeline_profile = {

    "testing_coverage": "standard",
    # minimal    — happy path only — fast, cheap, high risk
    # standard   — core flows covered — balanced
    # thorough   — broad coverage — slow, expensive

    "deployment_method": "rolling",
    # big_bang   — everything at once — fast, maximum blast radius
    # rolling    — gradual replacement — slower, recoverable
    # blue_green — parallel environments — expensive, clean cutover
    # canary     — small percentage first — slowest, lowest risk

    "rollback_plan": "partial",
    # none       — no plan — fastest to configure, catastrophic if needed
    # partial    — critical paths only
    # full       — complete rollback capability — expensive, reliable

    "observability_level": "basic",
    # none       — flying blind — cheapest
    # basic      — logs and uptime only
    # full       — logs, metrics, traces — expensive, nothing hidden

    "change_owner": "shared_pair",
    # single_person  — efficient, bus risk
    # shared_pair    — some redundancy, coordination cost
    # team_owned     — resilient, slower decisions
}

# --- Validate Frame 2 ---
is_valid, errors, warnings, capacity_used = validate_frame2(pipeline_profile)

print(f"Engineering Capacity used: {capacity_used}/100 units")
print()

if errors:
    print("❌  Frame 2 has errors. Fix before continuing:\n")
    for e in errors:
        print(f"    {e}")
else:
    print("✅  Frame 2 config accepted.\n")
    game["frame2"] = pipeline_profile
    if warnings:
        print("Notices:")
        for w in warnings:
            print(f"  {w}")
    print(f"\n    Testing coverage:  {pipeline_profile['testing_coverage']}")
    print(f"    Deployment:        {pipeline_profile['deployment_method']}")
    print(f"    Rollback:          {pipeline_profile['rollback_plan']}")
    print(f"    Observability:     {pipeline_profile['observability_level']}")
    print(f"    Change owner:      {pipeline_profile['change_owner']}")
    print(f"\n    Scroll to CELL 6 to begin Phase 2.\n")


# ============================================================
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 2 — LIVE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FreshCart is live. Real load. Real users. Real consequences.
# One card in this phase runs under a 60-second timer.
# ============================================================


# CELL 6 — PHASE 2 CARD

_phase2_cards = select_live_cards(system_profile, pipeline_profile, game)
_current_card_p2 = _phase2_cards[0] if _phase2_cards else None

if _current_card_p2:
    _card_p2 = get_card(_current_card_p2)
    game["cards_fired"].append(_current_card_p2)

    # Check for positive branch
    if _current_card_p2 in ["L1_positive", "L3_positive"]:
        _env = game["environment"]
        _idx = ENV_IDX[_env]
        _protected_loss = _card_p2["income_loss"][_idx]
        _phase_income = _baseline(_env) - _protected_loss
        update_income(game, "phase2", _phase_income)
        print_positive(
            _card_p2["name"],
            _card_p2["message"],
            _protected_loss,
            "unchanged — your investment paid off"
        )
        print_income_summary(game)
        print(f"\n    Scroll to CELL 7 when ready for Frame 3.\n")
    else:
        print_card(
            _card_p2["name"],
            _card_p2["scenario"],
            _card_p2["options"],
            _card_p2["flavor"]
        )
        if _card_p2.get("timed"):
            print(f"\n    ⏱  THIS IS A TIMED CARD.")
            print(f"    You have {_card_p2['timer_seconds']} seconds to decide.")
            print(f"    No decision entered = option (b) by default.\n")
        print(f"\n    Scroll to CELL 7 to enter your decision.\n")
else:
    print("✅  No incidents this phase.")
    update_income(game, "phase2", _baseline(game["environment"]))
    print_income_summary(game)


# CELL 7 — PHASE 2 DECISION

decision_rationale_p2 = "Enter one sentence explaining why you chose this option"
decision_p2 = "a"   # ← change to a, b, or c

# --- Apply decision ---
if not _current_card_p2 or _current_card_p2 in ["L1_positive", "L3_positive"]:
    print("✅  No decision required this phase.")
elif not decision_rationale_p2 or decision_rationale_p2.startswith("Enter"):
    print("❌  decision_rationale_p2 is required.")
elif decision_p2 not in ["a", "b", "c"]:
    print("❌  decision must be 'a', 'b', or 'c'.")
else:
    _card_p2 = get_card(_current_card_p2)
    game["decisions"][_current_card_p2] = decision_p2
    game["rationales"][_current_card_p2] = decision_rationale_p2
    _env = game["environment"]
    _idx = ENV_IDX[_env]

    # Special case: L1 hotfix has random outcome
    if _current_card_p2 == "L1" and decision_p2 == "b":
        import random
        _hotfix_works = random.random() > 0.5
        _outcome_key = "b_success" if _hotfix_works else "b_fail"
        _loss_triplet = _card_p2["income_loss"].get(_outcome_key, (0, 0, 0))
        _trust_delta = _card_p2["trust_delta"].get(_outcome_key, 0)
        if not _hotfix_works:
            print("🎲  Hotfix outcome: FAILED — the fix made things worse.\n")
        else:
            print("🎲  Hotfix outcome: WORKED — issue resolved.\n")
    else:
        _loss_triplet = _card_p2["income_loss"].get(decision_p2, (0, 0, 0))
        _trust_delta = _card_p2["trust_delta"].get(decision_p2, 0)

    _income_loss = _loss_triplet[_idx]

    # Special case L3: locked 4-day loss added
    if _current_card_p2 == "L3":
        _locked = _card_p2["income_loss_base"]["locked"][_idx]
        _income_loss += _locked

    _modifier = _card_p2.get("environment_modifier", {}).get(_env, 1.0)
    _income_loss = int(_income_loss * _modifier)

    _seed = _card_p2.get("seeds", {}).get(decision_p2)
    if _seed:
        plant_seed(game, _seed)

    _phase_income = _baseline(_env) - _income_loss
    update_income(game, "phase2", _phase_income)
    update_trust(game, _trust_delta)

    add_trace(
        game,
        card_id=_current_card_p2,
        reason=f"Phase 2: {_current_card_p2} triggered by pipeline config",
        severity="minor" if _income_loss < 150_000 else "major",
        next_risk=_seed,
    )
    game["facilitator_trace"][-1]["phase"] = "Phase 2"

    _note = _card_p2.get("consequence_notes", {}).get(decision_p2, "")
    print_consequence(_card_p2["name"], decision_p2, _income_loss, _trust_delta,
                      consequence_note=_note, seed_planted=_seed)
    print_income_summary(game)
    print(f"\n    Scroll to CELL 8 when instructed to configure Frame 3.\n")


# ============================================================
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FRAME 3 — OPERATIONS CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# You have seen Phases 1 and 2. Configure your operational layer.
# ============================================================


# CELL 8 — FRAME 3: OPERATIONS CONFIG

operations_profile = {

    "vendor_dependency": "medium",
    # low     — minimal third party reliance — more build cost, more control
    # medium  — selective use — balanced risk and cost
    # high    — heavily dependent — fast to market, fragile

    "fallback_strategy": "manual",
    # none       — no fallback — cheapest, zero resilience
    # manual     — human-executed recovery — moderate cost, error prone
    # automated  — system-triggered recovery — expensive, reliable

    "on_call_coverage": "business_hours",
    # none            — incidents found by customers
    # business_hours  — daytime only
    # follow_the_sun  — partial 24x7
    # full_24x7       — always covered

    "incident_response": "runbook",
    # ad_hoc     — whoever is available — fast to set up, chaotic under pressure
    # runbook    — documented procedures
    # practiced  — drilled and tested — expensive, reliable under pressure
}

# --- Validate Frame 3 ---
is_valid, errors, warnings = validate_frame3(operations_profile)

if errors:
    print("❌  Frame 3 has errors. Fix before continuing:\n")
    for e in errors:
        print(f"    {e}")
else:
    print("✅  Frame 3 config accepted.\n")
    game["frame3"] = operations_profile
    if warnings:
        print("Notices:")
        for w in warnings:
            print(f"  {w}")
    print(f"\n    Vendor dependency:  {operations_profile['vendor_dependency']}")
    print(f"    Fallback strategy:  {operations_profile['fallback_strategy']}")
    print(f"    On-call coverage:   {operations_profile['on_call_coverage']}")
    print(f"    Incident response:  {operations_profile['incident_response']}")
    print(f"\n    Scroll to CELL 9 to begin Phase 3.\n")


# ============================================================
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 3 — v2 RELEASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FreshCart is adding a real-time delivery tracking feature.
# Same requirement for every team. Different outcomes.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v2 UNIVERSAL REQUIREMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FreshCart is adding a real-time delivery tracking feature.

This requires:
  - A new Tracking Service component
  - An updated mobile API contract
  - A change to the Notification Service

All teams implement this. What happens next depends
on what you built.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


# CELL 9 — PHASE 3 CARD

_phase3_cards = select_v2_cards(system_profile, pipeline_profile, game)
_current_card_p3 = _phase3_cards[0] if _phase3_cards else None

# Apply severity escalation
_seed_count = count_seeds(game)
if _seed_count >= 2:
    print(f"⚠  Entering Phase 3 with {_seed_count} active seeds.")
    print(f"   Severity of first card escalated.\n")

if _current_card_p3:
    _card_p3 = get_card(_current_card_p3)
    game["cards_fired"].append(_current_card_p3)
    print_card(
        _card_p3["name"],
        _card_p3["scenario"],
        _card_p3["options"],
        _card_p3["flavor"]
    )
    print(f"\n    Scroll to CELL 10 to enter your decision.\n")
else:
    print("✅  No major incidents this phase. Your earlier decisions held.")
    update_income(game, "phase3", _baseline(game["environment"]))
    print_income_summary(game)


# CELL 10 — PHASE 3 DECISION

decision_rationale_p3 = "Enter one sentence explaining why you chose this option"
decision_p3 = "a"   # ← change to a, b, or c

if not _current_card_p3:
    print("✅  No decision required this phase.")
elif not decision_rationale_p3 or decision_rationale_p3.startswith("Enter"):
    print("❌  decision_rationale_p3 is required.")
elif decision_p3 not in ["a", "b", "c"]:
    print("❌  decision must be 'a', 'b', or 'c'.")
else:
    _card_p3 = get_card(_current_card_p3)
    game["decisions"][_current_card_p3] = decision_p3
    game["rationales"][_current_card_p3] = decision_rationale_p3
    _env = game["environment"]
    _idx = ENV_IDX[_env]

    _loss_triplet = _card_p3["income_loss"].get(decision_p3, (0, 0, 0))
    _income_loss = _loss_triplet[_idx]

    # Severity escalation for 2+ seeds
    if _seed_count >= 2:
        _income_loss = int(_income_loss * 1.35)

    _trust_delta = _card_p3["trust_delta"].get(decision_p3, 0)
    _seed = _card_p3.get("seeds", {}).get(decision_p3)
    if _seed:
        plant_seed(game, _seed)

    # Trust recovery modifier
    _recovery = _card_p3.get("trust_recovery_modifier", {}).get(decision_p3, 0)
    if _recovery:
        _trust_delta += _recovery

    _phase_income = _baseline(_env) - _income_loss
    update_income(game, "phase3", _phase_income)
    update_trust(game, _trust_delta)

    add_trace(
        game,
        card_id=_current_card_p3,
        reason=f"Phase 3: {_current_card_p3} — {'delayed consequence' if _seed_count > 0 else 'direct trigger'}",
        seed_trigger=", ".join(game["seeds"]) if game["seeds"] else None,
        severity="critical" if _income_loss > 300_000 else "major",
        next_risk=_seed,
    )
    game["facilitator_trace"][-1]["phase"] = "Phase 3"

    _note = _card_p3.get("consequence_notes", {}).get(decision_p3, "")
    print_consequence(_card_p3["name"], decision_p3, _income_loss, _trust_delta,
                      consequence_note=_note, seed_planted=_seed)
    print_income_summary(game)
    print(f"\n    Scroll to CELL 11 when instructed to begin Phase 4.\n")


# ============================================================
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 4 — SCALE EVENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Your instructor will read the scenario aloud.
# No new config. Your architecture holds — or it doesn't.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# CELL 11 — PHASE 4: S1 — THE MOMENT OF TRUTH
# Wait for your instructor to read the scenario aloud.
# Then run this cell.

def _calculate_s1_outcome(game):
    """
    Determine S1 outcome tier based on accumulated config and seeds.
    Returns (tier, income_result, trust_delta, narrative).
    """
    env = game["environment"]
    idx = ENV_IDX[env]
    base = PHASE_BASELINE[idx]
    seeds = game.get("seeds", [])
    f2 = game.get("frame2", {})
    f3 = game.get("frame3", {})

    # Score resilience profile
    resilience_score = 0

    # Pipeline resilience
    deploy = f2.get("deployment_method", "big_bang")
    if deploy in ["canary", "blue_green"]:
        resilience_score += 2
    elif deploy == "rolling":
        resilience_score += 1

    rollback = f2.get("rollback_plan", "none")
    if rollback == "full":
        resilience_score += 2
    elif rollback == "partial":
        resilience_score += 1

    obs = f2.get("observability_level", "none")
    if obs == "full":
        resilience_score += 2
    elif obs == "basic":
        resilience_score += 1

    # Operations resilience
    fallback = f3.get("fallback_strategy", "none") if f3 else "none"
    if fallback == "automated":
        resilience_score += 2
    elif fallback == "manual":
        resilience_score += 1

    ir = f3.get("incident_response", "ad_hoc") if f3 else "ad_hoc"
    if ir == "practiced":
        resilience_score += 2
    elif ir == "runbook":
        resilience_score += 1

    # Seed penalties
    seed_penalty = len(seeds) * 0.5

    # Government stability floor
    is_government = env == "government"

    # Determine outcome tier
    effective_score = resilience_score - seed_penalty

    if effective_score >= 7:
        tier = "thriving"
        income = base + int(base * 0.68)   # ~$340k above baseline for consumer
        trust_delta = 10
        narrative = (
            "Traffic spiked 35x. Your systems flagged it in 90 seconds.\n"
            "Automated fallback activated. FreshCart degraded gracefully.\n\n"
            f"Revenue captured: +${int(base * 0.68):,} above baseline.\n"
            "Trust score: +10.\n\n"
            "This is what you paid for."
        )
    elif effective_score >= 4:
        tier = "surviving"
        income = int(base * 0.95)
        trust_delta = 0
        narrative = (
            "Traffic spiked 35x. FreshCart bent but didn't break.\n"
            "Some degradation. Most revenue captured.\n"
            "Your config held well enough."
        )
    elif effective_score >= 1:
        tier = "struggling"
        income = int(base * 0.6)
        trust_delta = -15
        narrative = (
            "Traffic spiked 35x. FreshCart struggled significantly.\n"
            "Major revenue loss. Trust eroded.\n"
            "Your architecture was not ready for this load."
        )
    else:
        tier = "collapsing"
        income = int(base * 0.2)
        if is_government:
            income = max(income, int(base * 0.4))   # government stability floor
        trust_delta = -30
        narrative = (
            "Traffic spiked 35x. FreshCart collapsed under load.\n"
            "Major outage. Most revenue lost.\n"
            "The accumulated decisions of the past three phases\n"
            "produced this outcome."
        )

    # Resolve planted seeds
    seed_notes = []
    extra_loss = 0
    extra_trust = 0

    if "P1_silent_fraud" in seeds:
        extra_loss += (400_000, 300_000, 240_000)[idx]
        extra_trust += -40
        seed_notes.append("P1 silent fraud surfaces publicly during scale event.")

    if "V2_mock_data" in seeds:
        extra_loss += (200_000, 150_000, 120_000)[idx]
        extra_trust += -35
        seed_notes.append("V2 mock data discovered during board demo.")

    if "D1_db_scaling" in seeds:
        extra_loss += (150_000, 112_000, 90_000)[idx]
        extra_trust += -10
        seed_notes.append("Shared DB saturation triggered under 35x load.")

    if "P3_workaround_live" in seeds:
        extra_loss += (120_000, 90_000, 72_000)[idx]
        extra_trust += -10
        seed_notes.append("P3 config cascade triggered during scale event.")

    income = max(0, income - extra_loss)
    trust_delta += extra_trust

    # Government floor
    if is_government:
        income = max(income, int(base * 0.4))

    return tier, income, trust_delta, narrative, seed_notes


_tier, _s1_income, _s1_trust, _s1_narrative, _seed_resolutions = _calculate_s1_outcome(game)
game["cards_fired"].append("S1")

print(f"\n{SEP}")
print(f"PHASE 4 — THE MOMENT OF TRUTH")
print(SEP)
print(_s1_narrative)

if _seed_resolutions:
    print(f"\nSeeds resolving now:")
    for s in _seed_resolutions:
        print(f"  💥 {s}")

update_income(game, "phase4", _s1_income)
update_trust(game, _s1_trust)

print(f"\nOutcome tier:  {_tier.upper()}")
print_income_summary(game)
print(f"\n    Scroll to CELL 12 for the final card.\n")


# CELL 12 — PHASE 4: S2 — THE BILL ARRIVES
# Trust score is revealed first. Wait 30 seconds. Then revenue.

print(f"\n{SEP}")
print(f"THE BILL ARRIVES")
print(SEP)
print(f"\nYour Trust Score: {game['trust_score']}/100")
env_label = {
    "consumer":   "Customer Trust",
    "enterprise": "Stakeholder Confidence",
    "government": "Political Capital"
}.get(game["environment"], "Trust")
print(f"({env_label})")
print(f"\n... waiting for room discussion ...\n")
print(f"Run CELL 13 to reveal revenue impact and enter your decision.")


# CELL 13 — S2 DECISION

_card_s2 = get_card("S2")
game["cards_fired"].append("S2")
print_card(
    _card_s2["name"],
    _card_s2["scenario"],
    _card_s2["options"],
    _card_s2["flavor"]
)
print(f"\n    Scroll to CELL 14 to enter your decision.\n")


# CELL 14 — S2 DECISION ENTRY

decision_rationale_s2 = "Enter one sentence explaining why you chose this option"
decision_s2 = "a"   # ← change to a, b, or c

if not decision_rationale_s2 or decision_rationale_s2.startswith("Enter"):
    print("❌  decision_rationale_s2 is required.")
elif decision_s2 not in ["a", "b", "c"]:
    print("❌  decision must be 'a', 'b', or 'c'.")
else:
    game["decisions"]["S2"] = decision_s2
    game["rationales"]["S2"] = decision_rationale_s2
    _env = game["environment"]
    _idx = ENV_IDX[_env]

    _loss_triplet = _card_s2["income_loss"].get(decision_s2, (0, 0, 0))
    _income_loss = _loss_triplet[_idx]
    _trust_delta = _card_s2["trust_delta"].get(decision_s2, 0)
    _recovery = _card_s2.get("trust_recovery_modifier", {}).get(decision_s2, 0)

    _seed = _card_s2.get("seeds", {}).get(decision_s2)
    if _seed:
        plant_seed(game, _seed)

    # Apply S2 loss to phase4 income
    game["income"]["phase4"] = max(0, game["income"]["phase4"] - _income_loss)
    update_trust(game, _trust_delta)

    add_trace(
        game,
        card_id="S2",
        reason="Phase 4: S2 — board accountability moment",
        severity="major",
    )
    game["facilitator_trace"][-1]["phase"] = "Phase 4"

    _note = _card_s2.get("consequence_notes", {}).get(decision_s2, "")
    print_consequence(_card_s2["name"], decision_s2, _income_loss, _trust_delta,
                      consequence_note=_note, seed_planted=_seed)
    if _recovery:
        print(f"    Trust recovery modifier: +{_recovery} applied going forward.")

    print(f"\n    Scroll to CELL 15 for your final summary.\n")


# ============================================================
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FINAL SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# CELL 15 — FINAL SUMMARY
# Run this cell to generate your end-of-game output.
# Copy everything between the lines and give it to your instructor.

print_final_summary(game)


# ============================================================
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REFLECTION — BEFORE SECOND ITERATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# CELL 16 — REFLECTION OBJECT
# Fill this out before running the second iteration.
# This cell locks once you run CELL 17.

strategy_change = {
    "what_failed":    "Describe the main thing that went wrong",
    "what_we_change": "Describe the specific config change you are making",
    "why":            "One sentence: why do you believe this change fixes the problem",
}

print("Reflection recorded:")
for k, v in strategy_change.items():
    print(f"  {k}: {v}")
print(f"\nRun CELL 17 to begin the second iteration.")


# CELL 17 — SECOND ITERATION SETUP
# This resets income and trust but keeps your seeds visible.
# You can now edit system_profile, pipeline_profile, and
# operations_profile above, then re-run from CELL 2.

if any(v.startswith("Describe") for v in strategy_change.values()):
    print("❌  Complete the reflection object in CELL 16 before starting iteration 2.")
else:
    # Reset income and trust for second run
    game["income"] = {"phase1": 0, "phase2": 0, "phase3": 0, "phase4": 0}
    game["trust_score"] = 100
    game["cards_fired"] = []
    game["decisions"] = {}
    game["rationales"] = {}
    game["facilitator_trace"] = []
    # Seeds cleared — second run is a clean slate
    game["seeds"] = []
    game["phase"] = 0

    print("✅  Second iteration ready.")
    print(f"    Your reflection has been recorded.")
    print(f"    Scroll back to CELL 2 and update your config.")
    print(f"    Then run all cells in order again.\n")
    print(f"    At the end of iteration 2, the engine will ask:")
    print(f"    'Did your changes actually fix the problem?'")