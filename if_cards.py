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

def _should_fire_A1(frame1, game_state):
    return frame1.get("architecture_pattern") == "monolith"

def _should_fire_A2(frame1, game_state):
    return frame1.get("architecture_pattern") == "layered"

def _should_fire_A3(frame1, game_state):
    return frame1.get("architecture_pattern") == "client_server"

def _should_fire_A4(frame1, game_state):
    return frame1.get("architecture_pattern") == "event_driven"

def _should_fire_A5(frame1, game_state):
    return frame1.get("architecture_pattern") == "microservices"

def _should_fire_PT1(frame1, frame2, game_state):
    return frame2.get("testing_coverage") == "minimal"

def _should_fire_PT2(frame1, frame2, game_state):
    # Fires for any team — environment mismatches are universal
    return True

def _should_fire_PT4(frame1, frame2, game_state):
    return (frame1.get("team_structure") == "siloed" and
            frame2.get("testing_coverage") != "thorough")

def _should_fire_PT3(frame1, frame2, game_state):
    return frame2.get("testing_coverage") in ["minimal", "standard"]

def _should_fire_PT5(frame1, frame2, game_state):
    return (frame2.get("deployment_method") == "big_bang" and
            frame2.get("observability_level") in ["none", "basic"])


def _should_fire_B1(frame1, game_state):
    return frame1.get("team_structure") == "siloed"

def _should_fire_B2(frame1, game_state):
    return frame1.get("build_buy_configure") == "configure"

def _should_fire_B3(frame1, game_state):
    return (frame1.get("primary_risk") == "team_capability" or
            frame1.get("build_buy_configure") == "build")

def _should_fire_B4(frame1, game_state):
    return frame1.get("environment") == "government"

def _should_fire_B5(frame1, game_state):
    return True

def _should_fire_B6(frame1, game_state):
    return True

def _should_fire_B7(frame1, game_state):
    return (frame1.get("team_structure") == "siloed" or
            frame1.get("build_buy_configure") == "configure")

def _should_fire_L1(frame1, frame2, game_state):
    if frame2.get("deployment_method") in ["canary", "blue_green"]:
        return "positive"
    return (frame2.get("deployment_method") == "big_bang" and
            frame2.get("rollback_plan") == "none")

def _should_fire_L2(frame1, frame2, game_state):
    return "B1_gap_unresolved" in game_state.get("seeds", [])

def _should_fire_L3(frame2, game_state):
    if frame2.get("observability_level") == "full":
        return "positive"
    return frame2.get("observability_level") in ["none", "basic"]

def _should_fire_L4(frame2, game_state):
    return frame2.get("change_owner") == "single_person"

def _should_fire_L5(frame1, frame2, game_state):
    return (frame1.get("environment") == "government" and
            game_state.get("frame3", {}).get("incident_response") == "ad_hoc"
            if game_state.get("frame3") else
            frame1.get("environment") == "government")

def _should_fire_L6(frame1, frame2, game_state):
    return True

def _should_fire_P1(frame1, frame2, game_state):
    has_seed = any(s in game_state.get("seeds", [])
                   for s in ["B5_speed_skip", "L6_uat_skip"])
    return has_seed and frame2.get("testing_coverage") == "minimal"

def _should_fire_P2(frame1, frame2, game_state):
    return ("L4_ownership_gap" in game_state.get("seeds", []) or
            frame1.get("team_structure") == "siloed")

def _should_fire_P3(frame1, frame2, game_state):
    has_seed = "B3_debt_accumulated" in game_state.get("seeds", [])
    return has_seed and frame1.get("build_buy_configure") == "build"

def _should_fire_D1(frame1, game_state):
    return frame1.get("data_architecture") == "shared_db"

def _should_fire_V1(frame1, game_state):
    return ("L2_patch_debt" in game_state.get("seeds", []) and
            game_state.get("frame3", {}).get("vendor_dependency") in ["medium", "high"])

def _should_fire_V2(frame1, game_state):
    return (frame1.get("build_buy_configure") == "configure" or
            "B2_vendor_risk" in game_state.get("seeds", []))

def _should_fire_G3(frame1, game_state):
    return (frame1.get("environment") == "government" and
            any(s in game_state.get("seeds", [])
                for s in ["B4_procurement_risk", "L5_retroactive_deploy"]))

def _should_fire_S3(frame1, game_state):
    return (frame1.get("environment") == "government" and
            "G3_political_escalation" in game_state.get("seeds", []))


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


def card_L1_positive(deployment_method="canary"):
    """Positive branch for L1 — fires when canary or blue_green chosen."""
    if deployment_method == "blue_green":
        message = (
            "Your blue/green deployment caught the checkout issue before cutover.\n"
            "Traffic stayed on the green environment. Rolled back in 4 minutes.\n"
            "Income protected. Trust unchanged.\n\n"
            "This is what you paid for when you chose blue/green deployment."
        )
    else:
        message = (
            "Your canary deployment caught the checkout issue before it reached\n"
            "full traffic. 3% of users affected. Rolled back in 4 minutes.\n"
            "Income protected. Trust unchanged.\n\n"
            "This is what you paid for when you chose canary deployment."
        )
    return {
        "id":      "L1_positive",
        "name":    "The Ghost Deploy",
        "phase":   "live",
        "message": message,
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
        "income_loss": {
            "a": (180_000, 135_000, 108_000),
            "b": (90_000,  67_000,  54_000),
            "c": (60_000,  45_000,  36_000),
        },
        "income_loss_base": {
            # 4 days already lost regardless of decision — added on top in _run_phase
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
# ADDITIONAL CARDS — B2, B4, L2, L5, P2, V1, G3, S3
# ============================================================

def card_B2():
    return {
        "id": "B2",
        "name": "The Vendor Promise",
        "phase": "build",
        "scenario": (
            "Your chosen platform vendor just announced their roadmap.\n"
            "Three features FreshCart is counting on are now marked 'under review'.\n"
            "The sales rep says not to worry — they're just being cautious with language."
        ),
        "options": {
            "a": "Demand contractual commitment on the features — delays procurement",
            "b": "Accept the risk and proceed — faster, fragile",
            "c": "Start evaluating an alternative vendor — expensive distraction",
        },
        "flavor": "Lidl trusted SAP's roadmap. Seven years and €500M later they walked away. The features never came.",
        "income_loss": {
            "a": (70_000, 52_000, 42_000),
            "b": (0, 0, 0),
            "c": (90_000, 67_000, 54_000),
        },
        "trust_delta": {"a": 0, "b": 0, "c": 0},
        "seeds": {"b": "B2_vendor_risk"},
        "consequence_notes": {
            "a": "Contract negotiation underway. Procurement delayed.",
            "b": "Proceeding. Vendor promise noted but not binding.",
            "c": "Alternative evaluation started. Timeline disrupted.",
        },
    }


def card_B4():
    return {
        "id": "B4",
        "name": "Procurement Freeze",
        "phase": "build",
        "scenario": (
            "Your cloud infrastructure vendor needs to be reapproved under\n"
            "new procurement rules. Approval takes 6-10 weeks.\n"
            "Your go-live date is in 8 weeks."
        ),
        "options": {
            "a": "Wait for full approval — miss the go-live date",
            "b": "Proceed on existing approval — regulatory risk",
            "c": "Switch to an already-approved vendor — migration cost and delay",
        },
        "flavor": "Government procurement rules exist for good reasons. They also don't care about your deadline.",
        "income_loss": {
            "a": (100_000, 75_000, 60_000),
            "b": (0, 0, 0),
            "c": (140_000, 105_000, 84_000),
        },
        "trust_delta": {"a": 0, "b": -5, "c": 0},
        "seeds": {"b": "B4_procurement_risk"},
        "consequence_notes": {
            "a": "Waiting for approval. Go-live delayed.",
            "b": "Proceeding on existing approval. Regulatory exposure noted.",
            "c": "Switching vendors. Migration cost and delay absorbed.",
        },
    }


def card_L2():
    return {
        "id": "L2",
        "name": "The Assumption Invoice",
        "phase": "live",
        "scenario": (
            "The API contract gap from the handoff is now live in production.\n"
            "Cart items are being dropped at checkout intermittently -- 3% of orders.\n"
            "Enough to matter. Not enough to be obvious."
        ),
        "options": {
            "a": "Emergency fix -- take the integration offline, rebuild the contract",
            "b": "Compensating transaction -- patch around it, add more debt",
            "c": "Monitor and measure -- don't touch until you understand the full scope",
        },
        "flavor": "Silent failures are the most expensive kind. By the time you see them clearly, they've already cost you.",
        "income_loss": {
            "a": (120_000, 90_000, 72_000),
            "b": (60_000, 45_000, 36_000),
            "c": (30_000, 22_000, 18_000),
        },
        "trust_delta": {"a": -5, "b": -10, "c": -15},
        "seeds": {
            "b": "L2_patch_debt",
            "c": "L2_patch_debt",
        },
        "consequence_notes": {
            "a": "Integration rebuilt cleanly. Expensive but resolved.",
            "b": "Patch applied. Debt compounding.",
            "c": "Monitoring in progress. Risk still live.",
        },
    }


def card_L5():
    return {
        "id": "L5",
        "name": "The Approval Chain",
        "phase": "live",
        "scenario": (
            "A critical data exposure bug is found in production. Your team\n"
            "knows the fix. Deploying it requires sign-off from three department\n"
            "heads. One is traveling. One is in a budget meeting.\n"
            "One wants a full impact assessment first."
        ),
        "options": {
            "a": "Wait for proper approval -- correct process, painful delay",
            "b": "Deploy fix, get approval retroactively -- fast, career risk",
            "c": "Partial mitigation only -- reduce exposure without full fix",
        },
        "flavor": "Government incident response without practiced runbooks defaults to committee. Committees don't move at the speed of incidents.",
        "income_loss": {
            "a": (200_000, 150_000, 120_000),
            "b": (50_000, 37_000, 30_000),
            "c": (100_000, 75_000, 60_000),
        },
        "trust_delta": {"a": -15, "b": -5, "c": -10},
        "seeds": {"b": "L5_retroactive_deploy"},
        "consequence_notes": {
            "a": "Waiting for approval. Exposure window open.",
            "b": "Fix deployed. Approval requested retroactively.",
            "c": "Partial mitigation applied. Full fix still pending.",
        },
    }


def card_P2():
    return {
        "id": "P2",
        "name": "Who Owns the Tracking Service?",
        "phase": "v2",
        "scenario": (
            "The new Tracking Service sits between three existing teams.\n"
            "Nobody owns it. Each team assumed another was responsible.\n"
            "It has been live for six days. Tonight it fails silently.\n"
            "4,000 customers get no delivery updates. Support has no information."
        ),
        "options": {
            "a": "Emergency ownership assignment -- designate a team now",
            "b": "Shared ownership agreement -- committee approach",
            "c": "Outsource ownership to vendor -- fast, expensive, creates dependency",
        },
        "flavor": "Ownership gaps are architectural decisions that feel like org decisions. You made this one in Frame 1 and Frame 2.",
        "income_loss": {
            "a": (80_000, 60_000, 48_000),
            "b": (120_000, 90_000, 72_000),
            "c": (200_000, 150_000, 120_000),
        },
        "trust_delta": {"a": -10, "b": -20, "c": -10},
        "seeds": {"b": "P2_shared_ownership"},
        "consequence_notes": {
            "a": "Ownership assigned. Team scrambling to get up to speed.",
            "b": "Committee formed. Coordination overhead begins.",
            "c": "Vendor engaged. Dependency created.",
        },
    }


def card_V1():
    return {
        "id": "V1",
        "name": "API Surprise",
        "phase": "v2",
        "scenario": (
            "Your notification vendor updated their API last night.\n"
            "No advance notice. The v2 Tracking Service depends on this\n"
            "API for delivery status pushes. It is now broken in production.\n"
            "12,000 customers are not receiving delivery notifications."
        ),
        "options": {
            "a": "Emergency API update -- drop everything, fix now",
            "b": "Fallback to email only -- degrades experience, buys time",
            "c": "Queue notifications and batch send when fixed",
        },
        "flavor": "Vendor APIs change. Always. The question is whether you built for it.",
        "income_loss": {
            "a": (90_000, 67_000, 54_000),
            "b": (40_000, 30_000, 24_000),
            "c": (30_000, 22_000, 18_000),
        },
        "trust_delta": {"a": -5, "b": -15, "c": -5},
        "seeds": {"c": "V1_queue_risk"},
        "consequence_notes": {
            "a": "Emergency fix underway. All hands on deck.",
            "b": "Fallback active. Customers getting emails only.",
            "c": "Queue building. Risk of overflow if scale event hits.",
        },
    }


def card_G3():
    return {
        "id": "G3",
        "name": "The Audit",
        "phase": "v2",
        "scenario": (
            "An internal audit has flagged two procurement and deployment\n"
            "decisions from earlier in the project as non-compliant.\n"
            "The finding is now with the department secretary.\n"
            "Project may be paused pending review.\n"
            "Technical risk is low. Process risk is high."
        ),
        "options": {
            "a": "Full cooperation -- transparent audit response, possible project pause",
            "b": "Legal/compliance remediation only -- address the letter, not the spirit",
            "c": "Escalate politically -- use relationships to contain the finding",
        },
        "flavor": "Canada Phoenix wasn't just a technical failure. It was a governance failure. The two are inseparable in government implementations.",
        "income_loss": {
            "a": (180_000, 135_000, 108_000),
            "b": (120_000, 90_000, 72_000),
            "c": (80_000, 60_000, 48_000),
        },
        "trust_delta": {"a": -5, "b": -15, "c": -10},
        "trust_recovery_modifier": {"a": 20},
        "seeds": {"c": "G3_political_escalation"},
        "consequence_notes": {
            "a": "Full cooperation underway. Project may pause. Trust building long term.",
            "b": "Compliance addressed on paper. Underlying risk remains.",
            "c": "Escalation in progress. Political capital being spent.",
        },
    }


def card_S3():
    return {
        "id": "S3",
        "name": "The Political Exposure",
        "phase": "scale",
        "scenario": (
            "The minister responsible for the FreshCart government contract\n"
            "has been asked a question in parliament about procurement irregularities.\n"
            "Your team has 4 hours to prepare a briefing.\n"
            "The technical facts are defensible. The process facts are not."
        ),
        "options": {
            "a": "Full briefing -- technical and process facts, transparent",
            "b": "Technical briefing only -- answer what was asked, nothing more",
            "c": "No comment pending internal review -- buys time, looks evasive",
        },
        "flavor": "Canada Phoenix became a political crisis before it became a technical one. Government implementations don't fail in server rooms -- they fail in question time.",
        "income_loss": {
            "a": (120_000, 90_000, 72_000),
            "b": (80_000, 60_000, 48_000),
            "c": (200_000, 150_000, 120_000),
        },
        "trust_delta": {"a": -10, "b": -20, "c": -35},
        "trust_recovery_modifier": {"a": 25},
        "consequence_notes": {
            "a": "Full briefing delivered. Trust rebuilding begins.",
            "b": "Technical facts only. Follow-up questions likely.",
            "c": "No comment issued. Political pressure building.",
        },
    }

# ============================================================
# CARD REGISTRY
# ============================================================

# ============================================================
# PHASE 0 — ARCHITECTURE STRESS TEST CARDS
# One card per architecture pattern.
# Fire based on architecture_pattern choice in Frame 1.
# ============================================================

def card_A1():
    return {
        "id": "A1",
        "name": "The Monolith Moment",
        "phase": "architecture",
        "scenario": (
            "Sprint 2. Product requests a new promotional pricing feature.\n"
            "Simple change in theory. But the pricing logic is woven through\n"
            "eight modules — checkout, inventory, cart, reporting, admin,\n"
            "notifications, fraud, and the API layer.\n"
            "Touching one breaks tests in three others.\n"
            "Your team just discovered what 'tightly coupled' means in practice."
        ),
        "options": {
            "a": "Refactor pricing into a module boundary now — expensive, right",
            "b": "Add the feature carefully — test everything, slow but safe",
            "c": "Ship it fast — accept the coupling, move on",
        },
        "flavor": "Every monolith starts as the pragmatic choice. Lidl's SAP monolith took 7 years to untangle. The coupling was there from Sprint 2.",
        "income_loss": {
            "a": (90_000, 67_000, 54_000),
            "b": (50_000, 37_000, 30_000),
            "c": (0, 0, 0),
        },
        "trust_delta": {"a": 0, "b": 0, "c": 0},
        "seeds": {
            "c": "A1_coupling_debt",
        },
        "consequence_notes": {
            "a": "Pricing module extracted. Architecture improved. Cost absorbed.",
            "b": "Feature shipped carefully. Coupling remains but tested.",
            "c": "Feature shipped fast. Coupling deepened. Nobody noticed yet.",
        },
    }


def card_A2():
    return {
        "id": "A2",
        "name": "The Layer Leak",
        "phase": "architecture",
        "scenario": (
            "Sprint 3. A developer under deadline pressure puts a SQL query\n"
            "directly in the presentation layer to 'just make it work'.\n"
            "Then another developer does the same thing.\n"
            "Then a third. Your layered architecture is now\n"
            "a suggestion, not a boundary.\n"
            "The tech lead finds out during a code review."
        ),
        "options": {
            "a": "Enforce boundaries immediately — code review gate, no exceptions",
            "b": "Document it as technical debt — fix it next sprint",
            "c": "Allow it pragmatically — the deadlines are real",
        },
        "flavor": "Architectural boundaries are only real if the team defends them. The moment a shortcut is allowed, the second shortcut is easier.",
        "income_loss": {
            "a": (40_000, 30_000, 24_000),
            "b": (0, 0, 0),
            "c": (0, 0, 0),
        },
        "trust_delta": {"a": 0, "b": 0, "c": 0},
        "seeds": {
            "b": "A2_layer_debt",
            "c": "A2_layer_debt",
        },
        "consequence_notes": {
            "a": "Boundaries enforced. Team slows down briefly. Architecture holds.",
            "b": "Debt logged. Shortcuts continue until next sprint.",
            "c": "Pragmatism wins. Layer boundaries eroding.",
        },
    }


def card_A3():
    return {
        "id": "A3",
        "name": "The Bottleneck Appears",
        "phase": "architecture",
        "scenario": (
            "Three weeks into build. FreshCart's client-server architecture\n"
            "has all business logic on the central server.\n"
            "Load testing shows the server becomes a bottleneck\n"
            "at 800 concurrent users. Your production target is 5,000.\n"
            "The server vendor offers a hardware upgrade — expensive.\n"
            "Re-architecting would take 6 weeks."
        ),
        "options": {
            "a": "Upgrade the server hardware — buy time, not a solution",
            "b": "Re-architect now — move some logic to the client",
            "c": "Ship at current capacity — deal with scale when it's a real problem",
        },
        "flavor": "Client-server scales vertically until it can't. Then it falls off a cliff. Healthcare.gov hit this cliff with 250,000 users on day one.",
        "income_loss": {
            "a": (100_000, 75_000, 60_000),
            "b": (140_000, 105_000, 84_000),
            "c": (0, 0, 0),
        },
        "trust_delta": {"a": 0, "b": 0, "c": 0},
        "seeds": {
            "c": "A3_scale_cliff",
        },
        "consequence_notes": {
            "a": "Hardware upgraded. Bottleneck delayed. Root cause unchanged.",
            "b": "Re-architecture underway. Timeline hit. Architecture improving.",
            "c": "Shipping at current capacity. Scale cliff still coming.",
        },
    }


def card_A4():
    return {
        "id": "A4",
        "name": "The Ghost Message",
        "phase": "architecture",
        "scenario": (
            "Sprint 4. A customer reports their order confirmation never arrived.\n"
            "Your event-driven system processed the order — the event fired.\n"
            "But nobody can tell if the notification service consumed it.\n"
            "The message queue shows it was delivered. The notification service\n"
            "shows no record. The order is in limbo.\n"
            "Your team has never debugged an async failure before."
        ),
        "options": {
            "a": "Build a message trace system — know where every event goes",
            "b": "Add compensating transactions — retry and reconcile",
            "c": "Manual fix for now — investigate root cause later",
        },
        "flavor": "Event-driven systems are powerful and nearly impossible to debug without the right instrumentation. Equifax couldn't trace their breach for 78 days.",
        "income_loss": {
            "a": (110_000, 82_000, 66_000),
            "b": (70_000, 52_000, 42_000),
            "c": (20_000, 15_000, 12_000),
        },
        "trust_delta": {"a": 0, "b": 0, "c": -5},
        "seeds": {
            "c": "A4_trace_gap",
        },
        "consequence_notes": {
            "a": "Message tracing built. Observability improved. Cost absorbed.",
            "b": "Compensating transactions in place. Resilience improved.",
            "c": "Manual fix applied. Root cause unknown. Will recur.",
        },
    }


def card_A5():
    return {
        "id": "A5",
        "name": "The Service That Ate The Sprint",
        "phase": "architecture",
        "scenario": (
            "Your microservices architecture requires three new services\n"
            "to deliver the first user-facing feature:\n"
            "an API gateway, an auth service, and the feature service itself.\n"
            "The team has capacity for one. Sprint 1 ends with\n"
            "infrastructure built and zero user-facing functionality.\n"
            "The product owner is asking what was delivered."
        ),
        "options": {
            "a": "Simplify — collapse two services into one temporarily",
            "b": "Hire contractors to staff the other services",
            "c": "Explain the investment — next sprint delivers faster",
        },
        "flavor": "Microservices pay dividends at scale. They cost coordination overhead from day one. Canada Phoenix tried to decompose before they had the team to support it.",
        "income_loss": {
            "a": (30_000, 22_000, 18_000),
            "b": (120_000, 90_000, 72_000),
            "c": (0, 0, 0),
        },
        "trust_delta": {"a": 0, "b": 0, "c": -10},
        "seeds": {
            "c": "A5_stakeholder_doubt",
        },
        "consequence_notes": {
            "a": "Services consolidated temporarily. Velocity recovers.",
            "b": "Contractors hired. Services staffed. Budget hit.",
            "c": "Explanation given. Stakeholder confidence shaken.",
        },
    }


# ============================================================
# PIPELINE PHASE CARDS — PT1 through PT5
# Phase 2a (Pipeline Run) and Phase 2b (Staging & UAT)
# ============================================================

def card_PT1():
    return {
        "id": "PT1",
        "name": "The Unit Test That Lied",
        "phase": "pipeline",
        "scenario": (
            "Unit tests pass. All green.\n"
            "Integration testing begins. Three services that passed unit tests\n"
            "individually now fail when they talk to each other.\n"
            "The unit tests were testing mocks — not real dependencies.\n"
            "Nobody defined what integration tests were supposed to cover."
        ),
        "options": {
            "a": "Stop — fix integration failures before proceeding",
            "b": "Log as known issues — ship and fix next sprint",
            "c": "Rewrite unit tests to cover real dependencies",
        },
        "flavor": "A test that passes against a mock tells you the mock works. CrowdStrike's validation didn't catch what it needed to catch either.",
        "income_loss": {
            "a": (80_000, 60_000, 48_000),
            "b": (0, 0, 0),
            "c": (60_000, 45_000, 36_000),
        },
        "trust_delta": {"a": 0, "b": 0, "c": 0},
        "seeds": {"b": "PT1_integration_debt"},
        "consequence_notes": {
            "a": "Integration failures fixed. Pipeline delayed. Clean to proceed.",
            "b": "Known issues logged. Moving forward. Debt accumulating.",
            "c": "Unit tests improved. Integration now covered.",
        },
    }


def card_PT2():
    return {
        "id": "PT2",
        "name": "Works On My Machine",
        "phase": "pipeline",
        "scenario": (
            "The change works perfectly in development.\n"
            "It breaks in integration — the integration environment\n"
            "uses a different version of a shared library.\n"
            "Nobody documented environment differences.\n"
            "The dev who built it isn't sure what version production uses either."
        ),
        "options": {
            "a": "Lock all environment dependencies — pin every version",
            "b": "Patch integration environment to match dev — move on",
            "c": "Ship it — production is probably close enough to dev",
        },
        "flavor": "Environment configuration debt is invisible until it isn't. Knight Capital's deployment triggered code from a different environment era.",
        "income_loss": {
            "a": (50_000, 37_000, 30_000),
            "b": (30_000, 22_000, 18_000),
            "c": (0, 0, 0),
        },
        "trust_delta": {"a": 0, "b": 0, "c": -5},
        "seeds": {"c": "PT2_env_mismatch"},
        "consequence_notes": {
            "a": "Dependencies locked. Environments aligned. Cost absorbed.",
            "b": "Integration patched. Production still unknown.",
            "c": "Shipped. Environment mismatch still live.",
        },
    }


def card_PT3():
    return {
        "id": "PT3",
        "name": "UAT Finds It First",
        "phase": "staging",
        "scenario": (
            "UAT begins. Real users — not testers — try the checkout flow.\n"
            "Within two hours they find a workflow bug that all automated\n"
            "testing missed: when a promo code is applied after adding\n"
            "a subscription item, the total calculates incorrectly.\n"
            "Testers never tested this combination because nobody\n"
            "asked real users how they actually shop."
        ),
        "options": {
            "a": "Fix before go-live — delay release, get it right",
            "b": "Disable promo codes temporarily — ship without the feature",
            "c": "Ship it — edge case, low frequency, fix post-launch",
        },
        "flavor": "UAT exists because users don't read the test script. Healthcare.gov testers never simulated real user behavior at scale before launch day.",
        "income_loss": {
            "a": (70_000, 52_000, 42_000),
            "b": (40_000, 30_000, 24_000),
            "c": (0, 0, 0),
        },
        "trust_delta": {"a": 0, "b": -5, "c": 0},
        "seeds": {"c": "PT3_uat_skip"},
        "consequence_notes": {
            "a": "Fixed before launch. Delay absorbed. Right call.",
            "b": "Promo codes disabled. Feature gap noted. Shipping.",
            "c": "Shipped with known bug. Low frequency — for now.",
        },
    }


def card_PT4():
    return {
        "id": "PT4",
        "name": "The Integration Surprise",
        "phase": "pipeline",
        "scenario": (
            "Component A passes all tests.\n"
            "Component B passes all tests.\n"
            "Together they create a race condition that corrupts\n"
            "cart state when two users checkout simultaneously.\n"
            "Nobody tested them together under concurrent load.\n"
            "The siloed teams each assumed the other had covered it."
        ),
        "options": {
            "a": "Halt — run full integration suite under concurrent load",
            "b": "Add a mutex lock — quick fix, performance cost",
            "c": "Ship — concurrent checkout edge case is rare",
        },
        "flavor": "Components that work alone can fail together in ways neither team anticipated. This is why integration testing exists and why skipping it is expensive.",
        "income_loss": {
            "a": (90_000, 67_000, 54_000),
            "b": (40_000, 30_000, 24_000),
            "c": (0, 0, 0),
        },
        "trust_delta": {"a": 0, "b": 0, "c": 0},
        "seeds": {"c": "PT4_race_condition"},
        "consequence_notes": {
            "a": "Full integration suite run. Race condition found and fixed.",
            "b": "Mutex applied. Performance hit noted. Race condition addressed.",
            "c": "Shipped. Race condition live. Frequency unknown.",
        },
    }


def card_PT5():
    return {
        "id": "PT5",
        "name": "Staging Is Not Production",
        "phase": "staging",
        "scenario": (
            "Staging ran clean. Every test passed.\n"
            "Production has 10x the data volume, a different network\n"
            "topology, and a connection pool sized for the old system.\n"
            "The first production deploy hits a connection pool exhaustion\n"
            "error that never appeared in staging.\n"
            "Staging was not a realistic production mirror."
        ),
        "options": {
            "a": "Rollback immediately — fix staging to match production first",
            "b": "Emergency config fix — patch connection pool in production",
            "c": "Scale up the connection pool — absorb the cost",
        },
        "flavor": "Staging that doesn't mirror production doesn't catch production bugs. It catches staging bugs. GitLab's 2017 outage happened because their restore process had never been tested on production data.",
        "income_loss": {
            "a": (60_000, 45_000, 36_000),
            "b": (80_000, 60_000, 48_000),
            "c": (110_000, 82_000, 66_000),
        },
        "trust_delta": {"a": 0, "b": -5, "c": -5},
        "seeds": {
            "b": "PT5_prod_config_risk",
            "c": "PT5_prod_config_risk",
        },
        "consequence_notes": {
            "a": "Rolled back. Staging now mirrors production. Right call.",
            "b": "Emergency patch applied in production. Risk acknowledged.",
            "c": "Scaled up. Production stable. Root cause unresolved.",
        },
    }


CARD_REGISTRY = {
    # Architecture (Phase 0)
    "A1": card_A1,
    "A2": card_A2,
    "A3": card_A3,
    "A4": card_A4,
    "A5": card_A5,
    # Build (Phase 1)
    "B1": card_B1,
    "B2": card_B2,
    "B3": card_B3,
    "B4": card_B4,
    "B5": card_B5,
    "B6": card_B6,
    "B7": card_B7,
    # Pipeline (Phase 2a)
    "PT1": card_PT1,
    "PT2": card_PT2,
    "PT4": card_PT4,
    # Staging (Phase 2b)
    "PT3": card_PT3,
    "PT5": card_PT5,
    # Live (Phase 3)
    "L1": card_L1_negative,
    "L1_positive": lambda: card_L1_positive("canary"),
    "L2": card_L2,
    "L3": card_L3_negative,
    "L3_positive": card_L3_positive,
    "L4": card_L4,
    "L5": card_L5,
    "L6": card_L6,
    # v2 (Phase 4)
    "P1": card_P1,
    "P2": card_P2,
    "P3": card_P3,
    "D1": card_D1,
    "V1": card_V1,
    "V2": card_V2,
    "G3": card_G3,
    # Scale (Phase 5)
    "S1": card_S1,
    "S2": card_S2,
    "S3": card_S3,
}


def get_card(card_id, game_state=None):
    fn = CARD_REGISTRY.get(card_id)
    if fn is None:
        return None
    if card_id == "L1_positive" and game_state:
        return card_L1_positive(game_state.get("_l1_deploy", "canary"))
    return fn()


# ============================================================
# CARD SELECTION — which cards fire per phase
# ============================================================

def select_architecture_cards(frame1, game_state):
    """Return Phase 0 card — one per team based on architecture pattern."""
    cards = []
    if _should_fire_A1(frame1, game_state): cards.append("A1")
    if _should_fire_A2(frame1, game_state): cards.append("A2")
    if _should_fire_A3(frame1, game_state): cards.append("A3")
    if _should_fire_A4(frame1, game_state): cards.append("A4")
    if _should_fire_A5(frame1, game_state): cards.append("A5")
    return cards[:1]  # exactly one per team


def select_pipeline_cards(frame1, frame2, game_state):
    """Return Phase 2a pipeline run cards. Max 2."""
    cards = []
    if _should_fire_PT1(frame1, frame2, game_state): cards.append("PT1")
    if _should_fire_PT2(frame1, frame2, game_state): cards.append("PT2")
    if _should_fire_PT4(frame1, frame2, game_state): cards.append("PT4")
    return cards[:2]


def select_staging_cards(frame1, frame2, game_state):
    """Return Phase 2b staging/UAT cards. Max 2."""
    cards = []
    if _should_fire_PT3(frame1, frame2, game_state): cards.append("PT3")
    if _should_fire_PT5(frame1, frame2, game_state): cards.append("PT5")
    return cards[:2]



    return frame1.get("team_structure") == "siloed"

def select_build_cards(frame1, game_state):
    """Return list of card IDs to fire in Phase 1 (Build). Max 3."""
    cards = []
    if _should_fire_B1(frame1, game_state):  cards.append("B1")
    if _should_fire_B2(frame1, game_state):  cards.append("B2")
    if _should_fire_B3(frame1, game_state):  cards.append("B3")
    if _should_fire_B4(frame1, game_state):  cards.append("B4")
    if _should_fire_B5(frame1, game_state):  cards.append("B5")
    if _should_fire_B6(frame1, game_state):  cards.append("B6")
    if _should_fire_B7(frame1, game_state):  cards.append("B7")
    return cards[:3]


def select_live_cards(frame1, frame2, game_state):
    """Return list of card IDs to fire in Phase 2 (Live). Max 3."""
    cards = []
    deploy = frame2.get("deployment_method", "big_bang")
    l1_result = _should_fire_L1(frame1, frame2, game_state)
    if l1_result == "positive":
        game_state["_l1_deploy"] = deploy
        cards.append("L1_positive")
    elif l1_result:
        cards.append("L1")
    if _should_fire_L2(frame1, frame2, game_state):  cards.append("L2")
    l3_result = _should_fire_L3(frame2, game_state)
    if l3_result == "positive":
        cards.append("L3_positive")
    elif l3_result:
        cards.append("L3")
    if _should_fire_L4(frame2, game_state):  cards.append("L4")
    if _should_fire_L5(frame1, frame2, game_state):  cards.append("L5")
    if _should_fire_L6(frame1, frame2, game_state):  cards.append("L6")
    return cards[:3]


def select_v2_cards(frame1, frame2, game_state):
    """Return list of card IDs to fire in Phase 3 (v2). Max 3."""
    cards = []
    if _should_fire_P1(frame1, frame2, game_state):  cards.append("P1")
    if _should_fire_P2(frame1, frame2, game_state):  cards.append("P2")
    if _should_fire_P3(frame1, frame2, game_state):  cards.append("P3")
    if _should_fire_D1(frame1, game_state):           cards.append("D1")
    if _should_fire_V1(frame1, game_state):           cards.append("V1")
    if _should_fire_V2(frame1, game_state):           cards.append("V2")
    if _should_fire_G3(frame1, game_state):           cards.append("G3")
    return cards[:3]


def select_scale_cards(game_state):
    """Phase 4 cards — S1 and S2 always fire. S3 fires for government with seed."""
    cards = ["S1", "S2"]
    if _should_fire_S3(game_state.get("frame1", {}), game_state):
        cards.append("S3")
    return cards