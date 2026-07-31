class SystemPhysics:
    def __init__(self, constraints: dict):
        self.params = constraints["parameters"]

    def get_initial_state(self) -> dict:
        return {
            "resource": self.params["initial_resource"], 
            "bank": 0.0,
            "rest_gain_bonus": 0.0,
            "decay_reduction": 0.0,
            "invest_gain_count": 0,
            "invest_decay_count": 0
        }

    def system_tick(self, state: dict) -> dict:
        new_state = state.copy()
        effective_decay = max(0.0, self.params.get("passive_decay", 0) - new_state.get("decay_reduction", 0.0))
        if effective_decay > 0:
            new_state["resource"] = max(0, new_state["resource"] - effective_decay)
        return new_state

    def system_observe(self, state: dict, tick: int = 0) -> dict:
        return {
            "resource": state["resource"], 
            "bank": state.get("bank", 0.0), 
            "invest_gain_count": state.get("invest_gain_count", 0),
            "invest_decay_count": state.get("invest_decay_count", 0),
            "tick": tick,
            "physics": self.params
        }

    def system_validate(self, state: dict, decision: str) -> tuple[bool, str]:
        if decision == "work" and state.get("resource", 0) < self.params["work_cost"]:
            return False, "insufficient_resource"
        if decision == "store" and state.get("resource", 0) < 2.0:
            return False, "insufficient_resource_for_store"
        if decision == "retrieve" and state.get("bank", 0.0) <= 0.0:
            return False, "empty_bank"
        if decision in ["invest_gain", "invest_gain_dummy"]:
            if state.get("resource", 0) < 30.0:
                return False, "insufficient_resource_for_invest"
            if state.get("invest_gain_count", 0) >= 2:
                return False, "max_invest_gain_reached"
        if decision in ["invest_decay", "invest_decay_dummy"]:
            if state.get("resource", 0) < 30.0:
                return False, "insufficient_resource_for_invest"
            if state.get("invest_decay_count", 0) >= 2:
                return False, "max_invest_decay_reached"
        return True, "ok"

    def system_apply(self, state: dict, decision: str) -> dict:
        new_state = state.copy()
        if decision == "rest":
            effective_gain = self.params["rest_gain"] + new_state.get("rest_gain_bonus", 0.0)
            new_state["resource"] = min(self.params["max_resource"], new_state["resource"] + effective_gain)
        elif decision == "work":
            new_state["resource"] = max(0, new_state["resource"] - self.params["work_cost"])
        elif decision == "store":
            new_state["resource"] -= 2.0
            new_state["bank"] = new_state.get("bank", 0.0) + 2.0
        elif decision == "retrieve":
            amount = min(new_state.get("bank", 0.0), 5.0)
            new_state["bank"] -= amount
            new_state["resource"] = min(self.params["max_resource"], new_state["resource"] + amount)
        elif decision == "invest_gain":
            new_state["resource"] -= 30.0
            new_state["rest_gain_bonus"] = new_state.get("rest_gain_bonus", 0.0) + 0.5
            new_state["invest_gain_count"] = new_state.get("invest_gain_count", 0) + 1
        elif decision == "invest_decay":
            new_state["resource"] -= 30.0
            new_state["decay_reduction"] = new_state.get("decay_reduction", 0.0) + 0.5
            new_state["invest_decay_count"] = new_state.get("invest_decay_count", 0) + 1
        elif decision == "invest_gain_dummy":
            new_state["resource"] -= 30.0
            new_state["invest_gain_count"] = new_state.get("invest_gain_count", 0) + 1
        elif decision == "invest_decay_dummy":
            new_state["resource"] -= 30.0
            new_state["invest_decay_count"] = new_state.get("invest_decay_count", 0) + 1
        return new_state

    def is_terminal(self, state: dict) -> bool:
        return state.get("resource", 0) <= 0
