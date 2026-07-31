import logging
from typing import Dict, Any, List
from dory_agent.kernel.contracts import (
    Goal, Action, Event, EventType, PlannerInterface, CriticState
)
from dory_agent.kernel.events.event_bus import EventBus
from dory_agent.intelligence.memory.manager import MemoryManager
from dory_agent.runtime.executor import Executor
from dory_agent.runtime.critic import Critic
from dory_agent.intelligence.policy import PolicyEngine
from dory_agent.runtime.scheduler import Scheduler

class DoryRuntime:
    """
    The main Agent Runtime / Orchestrator.
    It has almost no business logic itself. It acts like an orchestra conductor,
    passing data between Planner -> Policy -> Executor -> Critic and firing events.
    """
    def __init__(
        self,
        planner: PlannerInterface,
        executor: Executor,
        critic: Critic,
        policy_engine: PolicyEngine,
        memory_manager: MemoryManager,
        event_bus: EventBus,
        scheduler: Scheduler
    ):
        self.planner = planner
        self.executor = executor
        self.critic = critic
        self.policy = policy_engine
        self.memory = memory_manager
        self.event_bus = event_bus
        self.scheduler = scheduler

    def start(self):
        """Main loop that continuously processes goals from the scheduler."""
        logging.info("Dory Runtime started. Waiting for goals...")
        while True:
            goal = self.scheduler.next_goal()
            self._process_goal(goal)

    def _process_goal(self, goal: Goal):
        """The core closed-loop execution logic for a single goal."""
        self.event_bus.publish(Event(event_type=EventType.GOAL_RECEIVED, payload={"goal": goal.model_dump()}))
        
        # Start a new working memory context for this goal
        self.memory.working.clear()
        self.memory.working.update("goal_id", "current") # Basic ID
        self.memory.working.update("objective", goal.objective)
        
        max_iterations = 20
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # 1. Plan
            context = {
                "working_memory": self.memory.working.context,
                "recent_episodes": [e.model_dump() for e in self.memory.episodic.get_recent_events()]
            }
            actions = self.planner.plan(goal, context)
            self.event_bus.publish(Event(event_type=EventType.PLAN_CREATED, payload={"actions": [a.model_dump() for a in actions]}))
            
            if not actions:
                # If planner returns no actions, goal might be completed
                break
                
            for action in actions:
                self.event_bus.publish(Event(event_type=EventType.STEP_STARTED, payload={"action": action.model_dump()}))
                
                # 2. Policy Check
                policy_decision = self.policy.evaluate(action)
                if not policy_decision.allowed:
                    # In a real system, this would trigger a REPLAN or human-in-the-loop
                    logging.warning(f"Action blocked: {policy_decision.reason}")
                    continue
                
                # 3. Execute
                self.event_bus.publish(Event(event_type=EventType.ACTION_STARTED, payload={"action": action.model_dump()}))
                observation = self.executor.execute(action, policy_decision)
                self.event_bus.publish(Event(event_type=EventType.OBSERVATION_RECEIVED, payload={"observation": observation.model_dump()}))
                
                # 4. Critic
                critic_result = self.critic.evaluate(action, observation, goal, context)
                self.event_bus.publish(Event(event_type=EventType.CRITIC_EVALUATED, payload={"critic_result": critic_result.model_dump()}))
                
                # Handle Critic Feedback
                if critic_result.state == CriticState.SUCCESS:
                    continue # Move to next action in plan
                elif critic_result.state == CriticState.PARTIAL:
                    continue # Note and continue
                elif critic_result.state == CriticState.RETRY:
                    # In a real impl, loop back to execute this same action a few times
                    break
                elif critic_result.state == CriticState.REPLAN:
                    # Break out of action loop, hit the while loop again to ask planner for new plan
                    break
                elif critic_result.state == CriticState.ABORT:
                    self.event_bus.publish(Event(event_type=EventType.GOAL_FAILED, payload={"reason": critic_result.reasoning}))
                    return
                    
        # If we exit the while loop successfully (or hit iteration limit)
        self.event_bus.publish(Event(event_type=EventType.GOAL_COMPLETED, payload={"status": "finished"}))
