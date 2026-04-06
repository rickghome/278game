"""
ImplementForge -- Widget Layer
COSE 278: Implementing Systems -- Day 4

Provides ipywidgets-based UI for card decisions.
Each card renders its own widget. Submit writes to game state.
Students never type decision strings -- they use dropdowns.

Key design principle: commit-on-submit.
Widget state is written to game["pending_decisions"] on submit.
Consequence cells read from game["pending_decisions"], never from widgets.
This means cell re-runs and session restores are safe.
"""

import ipywidgets as widgets
from IPython.display import display, HTML, clear_output


# ============================================================
# STYLING
# Injected once. Works in both light and dark Colab themes.
# ============================================================

CARD_CSS = """
<style>
.if-card {
    border: 2px solid #4a90d9;
    border-radius: 8px;
    padding: 16px;
    margin: 12px 0;
    background: #f8faff;
    font-family: monospace;
}
.if-card-header {
    font-size: 1.1em;
    font-weight: bold;
    color: #1a4a8a;
    margin-bottom: 8px;
    border-bottom: 1px solid #4a90d9;
    padding-bottom: 6px;
}
.if-card-scenario {
    color: #222;
    margin: 10px 0;
    line-height: 1.5;
    white-space: pre-wrap;
}
.if-card-flavor {
    color: #555;
    font-style: italic;
    font-size: 0.9em;
    border-left: 3px solid #4a90d9;
    padding-left: 8px;
    margin: 10px 0;
}
.if-card-timed {
    color: #c0392b;
    font-weight: bold;
    margin: 6px 0;
}
.if-submitted {
    border-color: #27ae60;
    background: #f0fff4;
}
.if-submitted .if-card-header {
    color: #1a6a3a;
    border-color: #27ae60;
}
</style>
"""

_css_injected = False

def _inject_css():
    global _css_injected
    if not _css_injected:
        display(HTML(CARD_CSS))
        _css_injected = True


# ============================================================
# GAMECARD CLASS
# ============================================================

class GameCard:
    """
    A single incident card with self-contained widget UI.

    Lifecycle:
      1. GameCard(card_data, index, total, game) -- create
      2. card.display()                          -- render widgets
      3. student picks dropdown, types rationale, clicks Submit
      4. _on_submit() writes to game["pending_decisions"][card_id]
      5. widgets lock -- state is now in game, not widgets
      6. run_phase_consequences() reads from game["pending_decisions"]
    """

    def __init__(self, card_data, card_index, total_cards, game):
        self.card_data   = card_data
        self.card_id     = card_data["id"]
        self.card_index  = card_index
        self.total_cards = total_cards
        self.game        = game
        self.submitted   = False

        # Build dropdown options: list of (label, value) tuples
        options = card_data.get("options", {})
        self.option_labels = [
            (f"({k})  {v}", k)
            for k, v in sorted(options.items())
        ]

        # Widgets
        self.decision_dropdown = widgets.Dropdown(
            options=self.option_labels,
            description="Decision:",
            style={"description_width": "80px"},
            layout=widgets.Layout(width="98%"),
        )

        self.rationale_input = widgets.Textarea(
            placeholder="One sentence: why did your team choose this?",
            description="Rationale:",
            style={"description_width": "80px"},
            layout=widgets.Layout(width="98%", height="60px"),
        )

        self.submit_button = widgets.Button(
            description="Submit Decision",
            button_style="primary",
            icon="check",
            layout=widgets.Layout(width="200px"),
        )

        self.status_output = widgets.Output()
        self.card_html     = widgets.HTML(value=self._build_card_html(submitted=False))

        self.submit_button.on_click(self._on_submit)

    def _build_card_html(self, submitted=False, decision_label="", rationale=""):
        """Build card HTML. Called on init and after submit."""
        css_class = "if-card if-submitted" if submitted else "if-card"
        header_suffix = "  &nbsp; SUBMITTED" if submitted else ""

        is_timed = self.card_data.get("timed", False)
        timed_html = ""
        if is_timed:
            secs = self.card_data.get("timer_seconds", 60)
            timed_html = (
                f'<div class="if-card-timed">'
                f'TIMED -- {secs} seconds. Discuss and decide quickly.'
                f'</div>'
            )

        submitted_html = ""
        if submitted and decision_label:
            submitted_html = (
                f'<div style="margin-top:8px; color:#1a6a3a;">'
                f'<strong>Decision:</strong> {decision_label}<br>'
                f'<strong>Rationale:</strong> {rationale}'
                f'</div>'
            )

        scenario = self.card_data.get("scenario", "").replace("\n", "<br>")
        flavor   = self.card_data.get("flavor", "")

        return f"""
<div class="{css_class}">
  <div class="if-card-header">
    CARD {self.card_index} of {self.total_cards}
    &nbsp;|&nbsp; {self.card_data["name"]}
    {header_suffix}
  </div>
  {timed_html}
  <div class="if-card-scenario">{scenario}</div>
  <div class="if-card-flavor">{flavor}</div>
  {submitted_html}
</div>
"""

    def _on_submit(self, button):
        """Handle submit. Validate, commit to game state, lock widgets."""
        rationale = self.rationale_input.value.strip()

        if not rationale:
            with self.status_output:
                clear_output()
                print("Please enter your rationale before submitting.")
            return

        decision_value = self.decision_dropdown.value
        option_text = dict(self.option_labels).get(decision_value, decision_value)

        # Write to game state -- this is the commit
        if "pending_decisions" not in self.game:
            self.game["pending_decisions"] = {}

        self.game["pending_decisions"][self.card_id] = {
            "decision":  decision_value,
            "rationale": rationale,
        }

        # Lock widgets
        self.decision_dropdown.disabled = True
        self.rationale_input.disabled   = True
        self.submit_button.disabled     = True
        self.submit_button.description  = "Submitted"
        self.submit_button.button_style = "success"
        self.submitted = True

        # Update card HTML to show submitted state
        self.card_html.value = self._build_card_html(
            submitted=True,
            decision_label=option_text,
            rationale=rationale,
        )

        with self.status_output:
            clear_output()
            print(f"Decision for {self.card_id} recorded. Run the consequence cell when all cards are submitted.")

    def display(self):
        """Render the full card widget."""
        card_box = widgets.VBox([
            self.card_html,
            self.decision_dropdown,
            self.rationale_input,
            self.submit_button,
            self.status_output,
        ])
        display(card_box)


# ============================================================
# PHASE DISPLAY FUNCTION
# ============================================================

def show_phase_cards(phase_label, phase_cards, game):
    """
    Display all cards for a phase as interactive widgets.

    Handles:
    - Positive branch cards (L1_positive, L3_positive) -- shown as payoff, no decision
    - Active cards -- rendered as GameCard widgets
    - Already-submitted state (cell re-run) -- shows notice, no re-render
    - Empty phase -- shows "no incidents" notice

    Stores card IDs in game for use by run_phase_consequences().
    """
    _inject_css()

    # Split card types
    positive_ids = [c for c in phase_cards if c in ["L1_positive", "L3_positive"]]
    active_ids   = [c for c in phase_cards if c not in ["L1_positive", "L3_positive"]]

    # Show positive branch payoffs
    for cid in positive_ids:
        card = get_card(cid, game)
        if not card:
            continue
        env = game["environment"]
        idx = ENV_IDX[env]
        loss = card["income_loss"][idx]
        msg  = card.get("message", "").replace("\n", "<br>")
        display(HTML(f"""
<div class="if-card if-submitted">
  <div class="if-card-header" style="color:#1a6a3a; border-color:#27ae60;">
    RESILIENCE PAYOFF -- {card["name"]}
  </div>
  <div class="if-card-scenario">{msg}</div>
  <div style="color:#1a6a3a; margin-top:8px;">
    <strong>Minor income loss only:</strong> ${loss:,}<br>
    <strong>Trust:</strong> unchanged
  </div>
</div>
"""))

    # No active cards
    if not active_ids:
        if not positive_ids:
            display(HTML("""
<div class="if-card if-submitted">
  <div class="if-card-header" style="color:#1a6a3a; border-color:#27ae60;">
    No incidents this phase
  </div>
  <div class="if-card-scenario">
    Your earlier decisions held. Run the consequence cell to record phase income.
  </div>
</div>
"""))
        game["_active_card_ids"]   = []
        game["_positive_card_ids"] = positive_ids
        return

    # Check if already submitted (cell re-run protection)
    pending = game.get("pending_decisions", {})
    all_submitted = all(cid in pending for cid in active_ids)

    if all_submitted:
        display(HTML("""
<div style="padding:10px; background:#f0fff4; border:2px solid #27ae60;
            border-radius:6px; margin:8px 0; font-family:monospace;">
  <strong style="color:#1a6a3a;">All decisions already submitted.</strong><br>
  Run the consequence cell below to process results.
</div>
"""))
        game["_active_card_ids"]   = active_ids
        game["_positive_card_ids"] = positive_ids
        return

    # Clear stale pending decisions for active cards in this phase only
    for cid in active_ids:
        pending.pop(cid, None)

    # Phase header
    n = len(active_ids)
    display(HTML(f"""
<div style="padding:10px 16px; background:#1a4a8a; color:white; border-radius:6px;
            margin:8px 0; font-family:monospace; font-weight:bold; font-size:1.05em;">
  {phase_label} &nbsp;--&nbsp; {n} CARD{"S" if n > 1 else ""} FIRED
</div>
"""))

    # Render each card
    for i, cid in enumerate(active_ids):
        card_data = get_card(cid, game)
        if card_data:
            card_obj = GameCard(card_data, i + 1, n, game)
            card_obj.display()

    # Multi-card reminder
    if n > 1:
        display(HTML(f"""
<div style="padding:8px 12px; background:#fff3cd; border:1px solid #ffc107;
            border-radius:4px; margin:8px 0; font-family:monospace;">
  Submit all {n} cards before running the consequence cell below.
</div>
"""))

    # Store for consequence cell
    game["_active_card_ids"]   = active_ids
    game["_positive_card_ids"] = positive_ids


# ============================================================
# PHASE CONSEQUENCE FUNCTION
# ============================================================

def run_phase_consequences(phase_key, game):
    """
    Process all submitted decisions for a phase.

    Reads ONLY from game["pending_decisions"] -- never from widget state.
    Safe to call after cell re-runs or session restore.

    Returns True on success, False if decisions not yet submitted.
    """
    import random

    # Guard: already processed
    if game.get(f"_{phase_key}_processed"):
        print(f"Phase already processed.")
        print_income_summary(game)
        return True

    active_ids   = game.get("_active_card_ids", [])
    positive_ids = game.get("_positive_card_ids", [])
    pending      = game.get("pending_decisions", {})

    env = game["environment"]
    idx = ENV_IDX[env]
    vel = game.get("velocity_multiplier", 1.0)
    phase_income = int(_baseline(env) * vel)

    # Guard: check all active cards submitted
    if active_ids:
        missing = [cid for cid in active_ids if cid not in pending]
        if missing:
            print(f"Waiting for decisions on: {missing}")
            print("Submit all cards above, then re-run this cell.")
            return False

    # Process positive branch cards
    for cid in positive_ids:
        card = get_card(cid, game)
        if not card:
            continue
        loss = card["income_loss"][idx]
        phase_income -= loss
        if cid not in game["cards_fired"]:
            game["cards_fired"].append(cid)

    # Process each active card
    for cid in active_ids:
        card      = get_card(cid, game)
        entry     = pending[cid]
        decision  = entry["decision"]
        rationale = entry["rationale"]

        if cid not in game["cards_fired"]:
            game["cards_fired"].append(cid)
        game["decisions"][cid]  = decision
        game["rationales"][cid] = rationale

        # Special case: L1 hotfix has random outcome
        if cid == "L1" and decision == "b":
            ok  = random.random() > 0.5
            key = "b_success" if ok else "b_fail"
            outcome_label = "WORKED" if ok else "FAILED -- made it worse"
            print(f"Hotfix attempt: {outcome_label}")
            loss_triplet = card["income_loss"].get(key, (0, 0, 0))
            trust_delta  = card["trust_delta"].get(key, 0)
        else:
            loss_triplet = card["income_loss"].get(decision, (0, 0, 0))
            trust_delta  = card["trust_delta"].get(decision, 0)

        income_loss = loss_triplet[idx]

        # L3 locked 4-day loss
        if cid == "L3":
            income_loss += card.get("income_loss_base", {}).get("locked", (0, 0, 0))[idx]

        # Environment modifier
        mod = card.get("environment_modifier", {}).get(env, 1.0)
        income_loss = int(income_loss * mod)

        # Severity escalation in v2 Release for accumulated seeds
        if phase_key == "v2_release":
            seed_count = count_seeds(game)
            if seed_count >= 2 and active_ids.index(cid) == 0:
                income_loss = int(income_loss * 1.35)

        # Trust recovery modifier
        recovery = card.get("trust_recovery_modifier", {}).get(decision, 0)
        trust_delta += recovery

        # Plant seeds
        seed = card.get("seeds", {}).get(decision)
        if seed:
            plant_seed(game, seed)

        phase_income -= income_loss
        update_trust(game, trust_delta)

        # Facilitator trace
        add_trace(
            game, cid, f"{phase_key}: {cid}",
            seed_trigger=", ".join(game["seeds"]) if game["seeds"] else None,
            severity="minor" if income_loss < 100_000 else "major",
            next_risk=seed,
        )
        game["facilitator_trace"][-1]["phase"] = phase_key

        # Print consequence
        print_consequence(
            card["name"], decision, income_loss, trust_delta,
            consequence_note=card.get("consequence_notes", {}).get(decision, ""),
            seed_planted=seed,
        )

    # Record income for this phase
    # bill_arrives and political_exposure adjust the scale bucket, not their own
    income_bucket = {
        "bill_arrives":      "scale",
        "political_exposure": "scale",
    }.get(phase_key, phase_key)

    if income_bucket in game["income"]:
        update_income(game, income_bucket, max(0, phase_income))
    print_income_summary(game)

    # Mark processed and clean up
    game[f"_{phase_key}_processed"] = True
    if "pending_decisions" in game:
        del game["pending_decisions"]
    game.pop("_active_card_ids", None)
    game.pop("_positive_card_ids", None)

    save_game(game)
    return True
