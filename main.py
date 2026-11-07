from datetime import datetime
from typing import List, Dict, Any


class Account:
    """Базовый класс банковского счёта."""

    def __init__(self, account_holder: str, balance: float = 0.0) -> None:
        if balance < 0:
            raise ValueError("Начальный баланс не может быть отрицательным")
        self.holder = account_holder
        self._balance = balance
        self.operations_history: List[Dict[str, Any]] = []

    def get_balance(self) -> float:
        """Метод, возвращающий текущий баланс."""
        return self._balance

    def get_history(self) -> List[Dict[str, Any]]:
        """Метод возвращающий историю операций."""
        return self.operations_history

    def _log_operation(
        self, op_type: str, amount: float, status: str, **kwargs: Any
    ) -> None:
        """Метод, записывающий совершенную операцию в историю.

        Создает структурированную запись о транзакции, фиксирует дату
        и время в строковом формате. Через **kwargs добавляет
        в словарь специфичные поля (например, для дочернего класса credit_used).
        """
        now = datetime.now()
        record = {
            'date_time': now.strftime("%Y-%m-%d %H:%M:%S"),
            'type': op_type,
            'amount': amount,
            'balance_after': self._balance,
            'status': status,
        }
        record.update(kwargs)
        self.operations_history.append(record)

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self._balance += amount
        self._log_operation('deposit', amount, 'success')
        return True

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")

        if self._balance < amount:
            self._log_operation('withdraw', amount, 'fail')
            return False

        self._balance -= amount
        self._log_operation('withdraw', amount, 'success')
        return True


class CreditAccount(Account):
    """Кредитный счёт, наследующий функциональность Account."""

    def __init__(
        self,
        account_holder: str,
        balance: float = 0.0,
        credit_limit: float = 0.0
    ) -> None:
        if credit_limit < 0:
            raise ValueError("Кредитный лимит не может быть отрицательным")
        super().__init__(account_holder, balance)
        self.credit_limit = credit_limit

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self._balance += amount
        self._log_operation(
            'deposit', amount, 'success', credit_used=self._balance < 0
        )
        return True

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")

        if self._balance - amount < -self.credit_limit:
            self._log_operation('withdraw', amount, 'fail', credit_used=False)
            return False

        before = self._balance
        self._balance -= amount
        credit_used = before < 0 or self._balance < 0
        self._log_operation(
            'withdraw', amount, 'success', credit_used=credit_used
        )
        return True

    def get_available_credit(self) -> float:
        """Возвращает количество доступных кредитных средств."""
        return self.credit_limit + self._balance

if __name__ == '__main__':
    # Тест для проверки кода
    client_acc = Account("Руслан", 500.0)
    client_acc.deposit(200.0)
    client_acc.withdraw(100.0)
    client_acc.withdraw(900.0)

    print(f"Баланс базового счета: {client_acc.get_balance()}")
    print("История базового счета:")
    for op in client_acc.get_history():
        print(
            f"  [{op['date_time']}] {op['type']} | {op['amount']} | "
            f"Баланс: {op['balance_after']} | {op['status']}"
        )

    print("-" * 50)

    credit_acc = CreditAccount("Екатерина", balance=100.0, credit_limit=300.0)
    credit_acc.withdraw(250.0)

    print(f"Баланс кредитного счета: {credit_acc.get_balance()}")
    print(f"Доступный лимит: {credit_acc.get_available_credit()}")
    print("История кредитного счета:")
    for op in credit_acc.get_history():
        credit_info = (
            f" | Кредит: {op['credit_used']}" if 'credit_used' in op else ""
        )
        print(
            f"  [{op['date_time']}] {op['type']} | {op['amount']} | "
            f"Баланс: {op['balance_after']} | {op['status']}{credit_info}"
        )
