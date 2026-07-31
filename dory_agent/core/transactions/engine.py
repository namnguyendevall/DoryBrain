from typing import Protocol, Callable, List, Optional
from dory_agent.core.contracts import TransactionId, generate_id

class TransactionEngine(Protocol):
    """
    Interface for Git-like Unit of Work transaction engine.
    Supports Nested Transactions via savepoints.
    """
    def begin(self) -> TransactionId:
        pass
        
    def commit(self, transaction_id: TransactionId):
        pass
        
    def rollback(self, transaction_id: TransactionId):
        pass
        
    def savepoint(self, transaction_id: TransactionId) -> str:
        pass
        
    def rollback_to_savepoint(self, transaction_id: TransactionId, savepoint_id: str):
        pass
        
    def stage(self, transaction_id: TransactionId, rollback_action: Callable):
        pass

class DefaultTransactionEngine(TransactionEngine):
    def __init__(self):
        # Maps TransactionId to a list of rollback functions (LIFO order for rollback)
        self._active_transactions = {}
        
    def begin(self) -> TransactionId:
        tx_id = TransactionId(generate_id())
        self._active_transactions[tx_id] = []
        return tx_id
        
    def commit(self, transaction_id: TransactionId):
        if transaction_id in self._active_transactions:
            # Once committed, we discard the rollback functions
            del self._active_transactions[transaction_id]
            
    def rollback(self, transaction_id: TransactionId):
        if transaction_id in self._active_transactions:
            rollback_actions = self._active_transactions[transaction_id]
            # Execute rollbacks in reverse order (LIFO)
            for action in reversed(rollback_actions):
                try:
                    action()
                except Exception as e:
                    pass # Log in production
            del self._active_transactions[transaction_id]
            
    def stage(self, transaction_id: TransactionId, rollback_action: Callable):
        """
        Whenever a tool performs a destructive action, it stages a rollback function.
        """
        if transaction_id in self._active_transactions:
            self._active_transactions[transaction_id].append(rollback_action)
            
    def savepoint(self, transaction_id: TransactionId) -> str:
        if transaction_id in self._active_transactions:
            # A savepoint is just the current index of the staged actions
            return str(len(self._active_transactions[transaction_id]))
        return "0"
        
    def rollback_to_savepoint(self, transaction_id: TransactionId, savepoint_id: str):
        if transaction_id in self._active_transactions:
            try:
                target_len = int(savepoint_id)
                actions = self._active_transactions[transaction_id]
                
                # Rollback everything after the savepoint
                while len(actions) > target_len:
                    action = actions.pop()
                    try:
                        action()
                    except Exception:
                        pass
            except ValueError:
                pass
