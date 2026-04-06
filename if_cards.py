"""
ImplementForge — Card Library (Pilot Deck)
COSE 278: Implementing Systems — Day 4

Hidden from students. Do not distribute.
Contains all 15 pilot deck cards with trigger logic,
scenario text, income/trust impacts, and seed planting.

Income triplets throughout: Consumer / Enterprise / Government
"""

# Card IDs in pilot deck:
# Build:  B1, B3, B5, B6, B7
# Live:   L1, L3, L4, L6
# v2:     P1, P3, D1, V2 
# Scale:  S1, S2


# ============================================================
# CARD TRIGGER LOGIC
# Each function returns True if the card should fire.
# ============================================================

def _should_fire_B1(frame1, game_state):
    return frame1.get("team_structure") == "siloed"

def _should_fire_B3(frame1, game_state):
    return (frame1.get("primary_risk") == "team_capability" or
            frame1.get("build_buy_configure") == "build")

def _should_fire_B5(frame1, game_state):
    # Always fires — speed pressure hits every team
    return True

def _should_fire_B6(frame1, game_state):
    # CFO freeze hits everyone
    return True

def _should_fire_B7(frame1, game_state):
    return (frame1.get("team_structure") == "siloed" or
            frame1.get("build_buy_configure") == "configure")

def _should_fire_L1(frame1, frame2, game_state):
    # Positive branch: canary or blue_green
    if frame2.get("deployment_method") in ["canary", "blue_green"]:
        return "positive"
    # Negative branch: big_bang + no rollback
    return (frame2.get("deployment_method") == "big_bang" and
            frame2.get("rollback_plan") == "none")

def _should_fire_L3(frame2, game_state):
    # Positive branch: full observability
    if frame2.get("observability_level") == "full":
        return "positive"
    # Negative branch: none or basic
    return frame2.get("observability_level") in ["none", "basic"]

def _should_fire_L4(frame2, game_state):
    return frame2.get("change_owner") == "single_person"

def _should_fire_L6(frame1, frame2, game_state):
    # Always fires — every team gets VP Override
    return True

def _should_fire_P1(frame1, frame2, game_state):
    # Delayed: requires seed from B5(b/c) or L6(b/c) + minimal testing
    has_seed = (game_state.get("seeds") and
                any(s in game_state["seeds"] for s in ["B5_speed_skip", "L6_uat_skip"]))
    return has_seed and frame2.get("testing_coverage") == "minimal"

def _should_fire_P3(frame1, frame2, game_state):
    # Delayed: requires B3(c) seed + build strategy
    has_seed = "B3_debt_accumulated" in game_state.get("seeds", [])
    return has_seed and frame1.get("build_buy_configure") == "build"

def _should_fire_D1(frame1, game_state):
    return frame1.get("data_architecture") == "shared_db"

def _should_fire_V2(frame1, game_state):
    # In pilot: fires for configure strategy (B2 not in deck — trigger directly)
    return frame1.get("build_buy_configure") == "configure"

def _should_fire_S1(game_state):
    # Always fires — universal scale event
    return True

def _should_fire_S2(game_state):
    # Always fires after S1
    return True


# ============================================================
# CARD DEFINITIONS
# Each card returns a dict with all data the engine needs.
# ============================================================

def card_B1():
    return {
        "id": "B1",
        "name": "The Handoff Gap",
        "phase": "build",
        "scenario": (
            "FreshCart's checkout team finished their module and handed it to the\n"
            "integration team. Three weeks later, integration discovers the API contract\n"
            "was never formally agreed. Both sides built to different assumptions."
        ),
        "options": {
            "a": "Renegotiate the contract — delay delivery, rebuild one side",
            "b": "Build an adapter layer — maintains timeline, adds technical debt",
            "c": "Ship it and hope the gap doesn't surface in production",
        },
        "flavor": "The UK NHS NPfIT: 12 separate suppliers, 12 sets of assumptions, nobody verified. £12.7B.",
        "income_loss": {
            "a": (60_000, 45_000, 36_000),
            "b": (40_000, 30_000, 24_000),
            "c": (0, 0, 0),
        },
        "trust_delta": {
            "a": 0, "b": 0, "c": 0
        },
        "seeds": {
            "c": "B1_gap_unresolved"
        },
        "consequence_notes": {
            "a": "Integration rebuilt cleanly. Delay absorbed.",
            "b": "Adapter works for now. The debt is noted.",
            "c": "No immediate impact. The gap is live in production.",
        },
    }


def card_B3():
    return {
        "id": "B3",
        "name": "The Capability Gap",
        "phase": "build",
        "scenario": (
            "Sprint 3 velocity is 40% below estimate. The team is more junior than\n"
            "the hiring plan assumed. A consultant offers to embed for 8 weeks\n"
            "at significant cost."
        ),
        "options": {
            "a": "Hire the consultant — expensive, stabilizes velocity",
            "b": "Reduce scope — protects timeline, cuts features",
            "c": "Push through — maintain scope and timeline, accumulate debt",
        },
        "flavor": "Canada Phoenix cut staffing to save cost. The payroll system paid people wrong for years. $5B and counting.",
        "income_loss": {
            "a": (120_000, 90_000, 72_000),
            "b": (50_000, 37_000, 30_000),
            "c": (0, 0, 0),
        },
        "trust_delta": {
            "a": 0, "b": 0, "c": 0
        },
        "seeds": {
            "c": "B3_debt_accumulated"
        },
        "consequence_notes": {
            "a": "Velocity stabilizes. Cost absorbed.",
            "b": "Scope reduced. Timeline holds. Some features cut.",
            "c": "Timeline maintained. Technical debt is accumulating silently.",
        },
    }


def card_B5():
    return {
        "id": "B5",
        "name": "The Speed Tax",
        "phase": "build",
        "scenario": (
            "Leadership has pushed the go-live date forward by three weeks to hit\n"
            "a board announcement. The team flags that integration testing hasn't\n"
            "been completed. Leadership says ship it."
        ),
        "options": {
            "a": "Push back — hold the date, complete testing",
            "b": "Ship with known gaps — document the risks",
            "c": "Ship without documenting — fastest, most dangerous",
        },
        "flavor": "CrowdStrike bypassed their validation gate under deadline pressure. 8.5 million devices. The gate existed for exactly this situation.",
        "income_loss": {
            "a": (80_000, 60_000, 48_000),
            "b": (0, 0, 0),
            "c": (0, 0, 0),
        },
        "trust_delta": {
            "a": 0,
            "b": 0,
            "c": -5,
        },
        "seeds": {
            "b": "B5_speed_skip",
            "c": "B5_speed_skip",
        },
        "consequence_notes": {
            "a": "Date held. Testing completed. Delay cost absorbed.",
            "b": "Shipped. Gaps documented. Risk is live.",
            "c": "Shipped. No documentation. Risk is live and untracked.",
        },
    }


def card_B6():
    return {
        "id": "B6",
        "name": "The CFO Freeze",
        "phase": "build",
        "scenario": (
            "Mid-sprint, the CFO sends a company-wide memo. Discretionary spending\n"
            "is frozen effective immediately pending Q3 reforecast. Three things your\n"
            "team was counting on are now unfunded: the observability tooling upgrade,\n"
            "the additional testing environment, and the on-call rotation expansion."
        ),
        "options": {
            "a": "Absorb the cuts — continue with what you have, accept the gaps",
            "b": "Escalate — make the case these are risk items, not discretionary",
            "c": "Reallocate internally — find budget by descoping features",
        },
        "flavor": "Budget freezes don't arrive at convenient moments. They arrive when you are most exposed.",
        "income_loss": {
            "a": (0, 0, 0),
            "b": (30_000, 22_000, 18_000),   # 50% chance modeled as half cost
            "c": (80_000, 60_000, 48_000),
        },
        "trust_delta": {
            "a": 0, "b": 0, "c": 0
        },
        "seeds": {
            "a": "B6_gaps_absorbed",
        },
        "consequence_notes": {
            "a": "Cuts absorbed. Gaps now exist in observability and coverage.",
            "b": "Escalation submitted. Outcome uncertain — check back next phase.",
            "c": "Features descoped. Budget reallocated. Scope is smaller.",
        },
        "environment_modifier": {
            "government": 0.8,   # 20% reduction — government expected this
            "consumer":   1.2,   # 20% increase — consumer teams most exposed
            "enterprise": 1.0,
        },
    }


def card_B7():
    return {
        "id": "B7",
        "name": "The Partner Team",
        "phase": "build",
        "scenario": (
            "FreshCart's Notification Service is owned by a separate partner team.\n"
            "Your v1 release depends on their API being ready by Thursday. It's\n"
            "Wednesday afternoon. They just told you it'll be another two weeks.\n"
            "Their manager says it's not their problem — your timeline was never\n"
            "formally agreed."
        ),
        "options": {
            "a": "Delay your release — wait for the partner team",
            "b": "Build a stub — mock the integration, ship, replace later",
            "c": "Escalate to shared leadership — force a resolution",
        },
        "flavor": "Dependencies you don't own are risks you can't fully manage. Most teams discover this the hard way.",
        "income_loss": {
            "a": (90_000, 67_000, 54_000),
            "b": (60_000, 45_000, 36_000),
            "c": (35_000, 26_000, 21_000),   # 50% chance modeled as half
        },
        "trust_delta": {
            "a": 0, "b": 0, "c": 0
        },
        "seeds": {
            "b": "B7_stub_integration",
        },
        "consequence_notes": {
            "a": "Release delayed. Partner API wait begins.",
            "b": "Stub built. Notification Service mocked for now.",
            "c": "Escalation in progress. Timeline uncertain.",
        },
    }


def card_L1_negative():
    return {
        "id": "L1",
        "name": "The Ghost Deploy",
        "phase": "live",
        "scenario": (
            "FreshCart pushed last night. This morning checkout is processing orders\n"
            "incorrectly. Nobody can identify which change caused it — everything\n"
            "went out at once."
        ),
        "options": {
            "a": "Roll back the entire release — clean but costly",
            "b": "Hotfix blind — fast, high risk of making it worse",
            "c": "Take checkout offline while you diagnose — safe, expensive per minute",
        },
        "flavor": "Knight Capital lost $440M in 45 minutes because a deployment triggered code nobody remembered was still there.",
        "income_loss": {
            "a": (150_000, 112_000, 90_000),
            "b_success": (80_000, 60_000, 48_000),
            "b_fail":    (300_000, 225_000, 180_000),
            "c": (200_000, 150_000, 120_000),
        },
        "trust_delta": {
            "a": 0,
            "b_success": 0,
            "b_fail": -15,
            "c": -10,
        },
        "consequence_notes": {
            "a": "Full rollback complete. Release delayed. Root cause unknown.",
            "b": "Hotfix attempted. Outcome depends on luck — see result above.",
            "c": "Checkout offline. Diagnosis in progress. Revenue stopped.",
        },
    }


def card_L1_positive():
    """Positive branch for L1 — fires when canary or blue_green chosen."""
    return {
        "id":      "L1_positive",
        "name":    "The Ghost Deploy",
        "phase":   "live",
        "message": (
            "Your canary deployment caught the checkout issue before it reached\n"
            "full traffic. 3% of users affected. Rolled back in 4 minutes.\n"
            "Income protected. Trust unchanged.\n\n"
            "This is what you paid for when you chose canary deployment."
        ),
        "income_loss": (18_000, 13_000, 11_000),
        "trust_delta": 0,
    }


def card_L3_negative():
    return {
        "id": "L3",
        "name": "Invisible Fire",
        "phase": "live",
        "scenario": (
            "FreshCart's order fulfillment rate dropped 18% four days ago.\n"
            "You're finding out now because a customer emailed the CEO.\n"
            "Your dashboards showed green the entire time."
        ),
        "options": {
            "a": "Emergency observability retrofit — expensive, mid-flight",
            "b": "Manual investigation — slow, labor intensive",
            "c": "Public acknowledgment and fix — trust play, operationally painful",
        },
        "flavor": "Equifax's breach went undetected for 78 days. Not because nobody was watching — because nobody had instrumented the right thing.",
        "income_loss_base": {
            # 4 days already lost regardless of decision
            "locked": (75_000, 56_000, 45_000),
            "a": (180_000, 135_000, 108_000),
            "b": (90_000, 67_000, 54_000),
            "c": (60_000, 45_000, 36_000),
        },
        "trust_delta": {
            "a": -10, "b": -20, "c": -8
        },
        "consequence_notes": {
            "a": "Retrofit underway. 4 days of revenue already lost regardless.",
            "b": "Manual investigation in progress. 4 days of revenue already lost.",
            "c": "Publicly acknowledged. Customers notified. 4 days already lost.",
        },
    }


def card_L3_positive():
    """Positive branch for L3 — fires when full observability chosen."""
    return {
        "id":      "L3_positive",
        "name":    "Invisible Fire",
        "phase":   "live",
        "message": (
            "Your monitoring caught the fulfillment degradation 47 minutes after\n"
            "it started. Incident resolved before customer impact.\n\n"
            "Your observability investment paid for itself today."
        ),
        "income_loss": (18_000, 13_000, 11_000),
        "trust_delta": 0,
    }


def card_L4():
    return {
        "id": "L4",
        "name": "Bus Route",
        "phase": "live",
        "scenario": (
            "Your lead integration engineer — the only person who fully understands\n"
            "the FreshCart payment flow — is out unexpectedly for three weeks.\n"
            "No documentation exists. A payment edge case is failing in production."
        ),
        "options": {
            "a": "Wait for them to return — halt payment edge case fixes",
            "b": "Reconstruct knowledge from code — slow, error prone",
            "c": "Engage an external consultant — expensive but experienced",
        },
        "flavor": "Single points of human failure are architectural decisions. You made this choice in Frame 2.",
        "income_loss": {
            "a": (90_000, 67_000, 54_000),
            "b": (120_000, 90_000, 72_000),
            "c": (160_000, 120_000, 96_000),
        },
        "trust_delta": {
            "a": -10, "b": -5, "c": -5
        },
        "seeds": {
            "a": "L4_ownership_gap",
            "b": "L4_ownership_gap",
        },
        "consequence_notes": {
            "a": "Payment edge case unresolved. Engineer out three weeks.",
            "b": "Knowledge reconstruction in progress. Error risk elevated.",
            "c": "Consultant engaged. Expensive, but moving forward.",
        },
    }


def card_L6():
    return {
        "id": "L6",
        "name": "VP Override",
        "phase": "live",
        "timed": True,
        "timer_seconds": 60,
        "scenario": (
            "The VP of Product just messaged the team lead directly. A competitor\n"
            "launched a similar feature this morning. She wants FreshCart's v1.2\n"
            "release moved up from Thursday to today.\n\n"
            "\"Just skip UAT — we tested enough in staging. I'll own it.\"\n\n"
            "⏱  You have 60 seconds to decide."
        ),
        "options": {
            "a": "Hold the process — UAT runs, Thursday ships",
            "b": "Skip UAT, ship today — VP owns it in writing",
            "c": "Partial skip — smoke test only, ship tomorrow",
        },
        "flavor": "The person who says 'I'll own it' is never the one paged at 2am when it breaks. CrowdStrike's validation gate was skipped under exactly this kind of pressure.",
        "income_loss": {
            "a": (40_000, 30_000, 24_000),
            "b": (0, 0, 0),
            "c": (0, 0, 0),
        },
        "trust_delta": {
            "a": 0,
            "b": -5,
            "c": -3,
        },
        "seeds": {
            "b": "L6_uat_skip",
            "c": "L6_uat_skip",
        },
        "default_on_timeout": "b",
        "consequence_notes": {
            "a": "UAT completed Thursday. Process held.",
            "b": "UAT skipped. Shipped today. Risk is live and unvalidated.",
            "c": "Smoke test only. Shipped tomorrow. Risk partially mitigated.",
        },
    }


def card_P1():
    return {
        "id": "P1",
        "name": "The Silent Passenger",
        "phase": "v2",
        "scenario": (
            "The v2 release is live. Orders are processing normally.\n"
            "Three hours later your fraud detection team notices a pattern — a bug\n"
            "in the payment validation logic has been present since the skipped\n"
            "test cycle. It has been approving transactions it should have declined.\n"
            "FreshCart has processed $340,000 in fraudulent orders."
        ),
        "options": {
            "a": "Immediate shutdown of payment processing — stop the bleeding",
            "b": "Silent fix — patch quietly, absorb the fraud loss",
            "c": "Notify affected customers and regulators — painful, correct",
        },
        "flavor": "CrowdStrike. Knight Capital. The common thread is not bad code — it's a gate that existed for exactly this scenario and wasn't used.",
        "income_loss": {
            "a": (340_000, 255_000, 204_000),
            "b": (340_000, 255_000, 204_000),
            "c": (380_000, 285_000, 228_000),  # fraud + notification cost
        },
        "trust_delta": {
            "a": -15,
            "b": -5,   # -40 more if discovered in S1
            "c": -10,
        },
        "trust_recovery_modifier": {
            "c": 15    # partial recovery for transparency
        },
        "seeds": {
            "b": "P1_silent_fraud",
        },
        "consequence_notes": {
            "a": "Payments halted. Fraud stopped. Revenue paused.",
            "b": "Silent fix applied. Fraud absorbed. Regulators not notified.",
            "c": "Customers and regulators notified. Trust partially protected.",
        },
    }


def card_P3():
    return {
        "id": "P3",
        "name": "The Debt Collector",
        "phase": "v2",
        "scenario": (
            "The technical debt accumulated during the sprint velocity crisis has\n"
            "found v2. The new Tracking Service needs to integrate with the Cart\n"
            "module. The Cart module was never properly documented and contains\n"
            "three known shortcuts. Integration is taking four times longer than\n"
            "estimated. The go-live date is tomorrow."
        ),
        "options": {
            "a": "Delay v2 go-live — fix the integration properly",
            "b": "Ship with a documented workaround — more debt on existing debt",
            "c": "Descope tracking from Cart entirely — reduced feature, clean ship",
        },
        "flavor": "Technical debt doesn't disappear. It waits. It charges interest. It presents the bill at the worst possible moment.",
        "income_loss": {
            "a": (100_000, 75_000, 60_000),
            "b": (60_000, 45_000, 36_000),
            "c": (80_000, 60_000, 48_000),
        },
        "trust_delta": {
            "a": -5,
            "b": -10,
            "c": -15,
        },
        "seeds": {
            "b": "P3_workaround_live",
        },
        "consequence_notes": {
            "a": "v2 delayed. Integration fixed properly.",
            "b": "v2 shipped. Workaround live. Debt compounding.",
            "c": "v2 shipped. Tracking feature gap visible to customers.",
        },
    }


def card_D1():
    return {
        "id": "D1",
        "name": "One Database to Rule Them All",
        "phase": "v2",
        "scenario": (
            "The new Tracking Service needs to write high-frequency location updates —\n"
            "every 30 seconds per active delivery. Your shared database is now\n"
            "handling cart, inventory, payment, notifications, AND tracking writes\n"
            "simultaneously. Checkout query times have gone from 40ms to 4,200ms.\n"
            "Customers are abandoning carts."
        ),
        "options": {
            "a": "Emergency DB split — extract Tracking to its own database now",
            "b": "Throttle tracking update frequency — degrades the feature you just shipped",
            "c": "Scale up the shared DB instance — expensive, buys time, doesn't fix it",
        },
        "flavor": "A shared database is a shared ceiling. You find out where the ceiling is when someone moves in upstairs.",
        "income_loss": {
            "a": (200_000, 150_000, 120_000),
            "b": (80_000, 60_000, 48_000),
            "c": (150_000, 112_000, 90_000),
        },
        "trust_delta": {
            "a": -10,
            "b": -20,
            "c": -5,
        },
        "seeds": {
            "c": "D1_db_scaling",
        },
        "consequence_notes": {
            "a": "DB split in progress. Migration cost absorbed. Architecture improving.",
            "b": "Tracking throttled. Feature degraded. Customers notice.",
            "c": "DB scaled up. Checkout recovering. Architecture unchanged.",
        },
    }


def card_V2():
    return {
        "id": "V2",
        "name": "The Locked Room",
        "phase": "v2",
        "scenario": (
            "The vendor feature FreshCart depends on for the v2 Tracking Service\n"
            "has been formally deprecated. Replacement requires migrating to a new\n"
            "module — 6 weeks of work. You have 2 weeks until the board demo.\n"
            "The vendor offers an emergency professional services engagement\n"
            "to accelerate — at three times normal rate."
        ),
        "options": {
            "a": "Pay the vendor emergency rate — expensive, meets deadline",
            "b": "Build the feature internally — blows the deadline",
            "c": "Demo with mock data, migrate post-demo — reputational risk",
        },
        "flavor": "Lidl. Seven years. €500M. The vendor's roadmap was never yours to control.",
        "income_loss": {
            "a": (240_000, 180_000, 144_000),
            "b": (80_000, 60_000, 48_000),
            "c": (0, 0, 0),
        },
        "trust_delta": {
            "a": 0,
            "b": -10,
            "c": -5,
        },
        "seeds": {
            "c": "V2_mock_data",
        },
        "consequence_notes": {
            "a": "Emergency vendor engagement paid. Demo intact. Very expensive.",
            "b": "Internal build started. Board demo missed. Timeline reset.",
            "c": "Mock data used for demo. Migration scheduled post-demo.",
        },
    }


def card_S1():
    """
    Scale event — instructor reads aloud.
    Outcome determined by accumulated config profile, not a single decision.
    """
    return {
        "id": "S1",
        "name": "The Moment of Truth",
        "phase": "scale",
        "instructor_reads_aloud": True,
        "scenario": (
            "A national news segment just featured FreshCart as the fastest growing\n"
            "grocery delivery service in the region. Traffic spikes 35x in 90 minutes.\n\n"
            "This hits every team equally.\n"
            "What happens next depends entirely on what each team built."
        ),
        "flavor": "Ticketmaster had weeks of warning before Taylor Swift tickets went on sale. The load was predictable. The architecture wasn't ready.",
        # Outcomes determined by engine based on config profile
        # See run_S1() in the engine section below
    }


def card_S2():
    return {
        "id": "S2",
        "name": "The Bill Arrives",
        "phase": "scale",
        "trust_revealed_first": True,
        "scenario": (
            "The scale event is over. FreshCart survived — or didn't.\n\n"
            "Now the full cost of every shortcut, every deferred decision,\n"
            "every planted seed arrives simultaneously.\n\n"
            "The board wants a full accounting."
        ),
        "options": {
            "a": "Full transparency — present the real picture, propose remediation roadmap",
            "b": "Selective disclosure — show wins, minimize failures",
            "c": "Blame the infrastructure — external attribution",
        },
        "flavor": "Every implementation eventually has this meeting. The teams that survive it built a paper trail of honest decisions, not optimistic ones.",
        "income_loss": {
            "a": (100_000, 75_000, 60_000),
            "b": (50_000, 37_000, 30_000),
            "c": (150_000, 112_000, 90_000),
        },
        "trust_delta": {
            "a": 5,    # slight negative short term, positive recovery modifier
            "b": -10,
            "c": -25,
        },
        "trust_recovery_modifier": {
            "a": 20
        },
        "seeds": {
            "b": "S2_selective_disclosure",
        },
        "consequence_notes": {
            "a": "Full picture presented. Remediation roadmap proposed. Trust rebuilding.",
            "b": "Wins highlighted. Failures minimized. Board watching closely.",
            "c": "Infrastructure blamed. Leadership skeptical. Credibility reduced.",
        },
    }


# ============================================================
# CARD REGISTRY
# ============================================================

CARD_REGISTRY = {
    "B1": card_B1,
    "B3": card_B3,
    "B5": card_B5,
    "B6": card_B6,
    "B7": card_B7,
    "L1": card_L1_negative,
    "L1_positive": card_L1_positive,
    "L3": card_L3_negative,
    "L3_positive": card_L3_positive,
    "L4": card_L4,
    "L6": card_L6,
    "P1": card_P1,
    "P3": card_P3,
    "D1": card_D1,
    "V2": card_V2,
    "S1": card_S1,
    "S2": card_S2,
}


def get_card(card_id):
    fn = CARD_REGISTRY.get(card_id)
    if fn is None:
        return None
    return fn()


# ============================================================
# CARD SELECTION — which cards fire per phase
# ============================================================

def select_build_cards(frame1, game_state):
    """Return list of card IDs to fire in Phase 1 (Build)."""
    cards = []
    if _should_fire_B1(frame1, game_state):
        cards.append("B1")
    if _should_fire_B3(frame1, game_state):
        cards.append("B3")
    if _should_fire_B5(frame1, game_state):
        cards.append("B5")
    if _should_fire_B6(frame1, game_state):
        cards.append("B6")
    if _should_fire_B7(frame1, game_state):
        cards.append("B7")
    # Cap at 3 cards per phase to avoid overload
    return cards[:3]


def select_live_cards(frame1, frame2, game_state):
    """Return list of card IDs to fire in Phase 2 (Live)."""
    cards = []
    l1_result = _should_fire_L1(frame1, frame2, game_state)
    if l1_result == "positive":
        cards.append("L1_positive")
    elif l1_result:
        cards.append("L1")
    l3_result = _should_fire_L3(frame2, game_state)
    if l3_result == "positive":
        cards.append("L3_positive")
    elif l3_result:
        cards.append("L3")
    if _should_fire_L4(frame2, game_state):
        cards.append("L4")
    if _should_fire_L6(frame1, frame2, game_state):
        cards.append("L6")
    return cards[:3]


def select_v2_cards(frame1, frame2, game_state):
    """Return list of card IDs to fire in Phase 3 (v2)."""
    cards = []
    if _should_fire_P1(frame1, frame2, game_state):
        cards.append("P1")
    if _should_fire_P3(frame1, frame2, game_state):
        cards.append("P3")
    if _should_fire_D1(frame1, game_state):
        cards.append("D1")
    if _should_fire_V2(frame1, game_state):
        cards.append("V2")
    return cards[:3]


def select_scale_cards(game_state):
    """Phase 4 always fires S1 then S2."""
    return ["S1", "S2"]
