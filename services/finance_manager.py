class NotFoundError(Exception):
    pass

class FinanceManager:
    def __init__(self, file_manager):
        self._file_manager = file_manager
        self._user = None
        self._accounts = []
        self._categories = []
        self._budgets = []
        self._transactions = []
        self.load_data()

    def load_data(self):
        data = self._file_manager.load()
        if isinstance(data, dict):
            self._transactions = data.get("transactions", [])
        else:
            self._transactions = []
        
    def save_data(self):
        data = {
            "transactions": self._transactions
        }
        self._file_manager.save(data)

    def add_transaction(self, tx):
    
        if hasattr(tx, 'label') and tx.label().lower() == 'expense':
            if not getattr(tx, '_category', None):
                raise ValueError("Expense must have a valid category.")
        
        self._transactions.append(tx)
        self.save_data()

    def update_transaction(self, tx_id, updated_data: dict):
       
        for tx in self._transactions:
            if getattr(tx, '_id', None) == tx_id:
                for key, value in updated_data.items():
                    setattr(tx, f"_{key}", value)
                self.save_data()
                return
        raise NotFoundError(f"Transaction with ID {tx_id} not found.")

    def delete_transaction(self, tx_id):
       
        for i, tx in enumerate(self._transactions):
            if getattr(tx, '_id', None) == tx_id:
                del self._transactions[i]
                self.save_data()
                return
        raise NotFoundError(f"Transaction with ID {tx_id} not found.")

    def search(self, text: str):
   
        results = []
        text_lower = text.lower()
        for tx in self._transactions:
            note = str(getattr(tx, '_note', '')).lower()
            category = str(getattr(tx, '_category', '')).lower()
            if text_lower in note or text_lower in category:
                results.append(tx)
        return results

    def filter(self, category=None, tx_type=None, date_from=None, date_to=None):
      
        filtered = self._transactions
        
        if category is not None:
            filtered = [tx for tx in filtered if getattr(tx, '_category', None) == category]
            
        if tx_type is not None:
            filtered = [tx for tx in filtered if hasattr(tx, 'label') and tx.label().lower() == tx_type.lower()]
            
        if date_from is not None:
            filtered = [tx for tx in filtered if str(getattr(tx, '_date', '')) >= str(date_from)]
            
        if date_to is not None:
            filtered = [tx for tx in filtered if str(getattr(tx, '_date', '')) <= str(date_to)]
            
        return filtered