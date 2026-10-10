"""Request-local simulated budgets; amounts below are not actual spending."""
import json
import math
from dataclasses import dataclass, field
from decimal import Decimal

class BudgetExceeded(ValueError):
    pass

def token_units(value):
    text=value if isinstance(value,str) else json.dumps(value,sort_keys=True,default=str)
    return math.ceil(len(text)/4)

@dataclass
class RequestBudget:
    token_cap: int = 50000
    cost_cap: str = '0.10'
    price_per_thousand: str = '0.002'
    receipts: list = field(default_factory=list)
    exceeded: bool = field(default=False,init=False)
    crew_started: bool = field(default=False,init=False)

    def __post_init__(self):
        if self.token_cap<1 or Decimal(self.cost_cap)<=0 or Decimal(self.price_per_thousand)<0:
            raise ValueError('Invalid budget configuration')

    def charge(self, stage, inputs, output):
        prompt,completion=token_units(inputs),token_units(output)
        used=sum(r['total_tokens'] for r in self.receipts)
        new=used+prompt+completion
        cost=Decimal(new)*Decimal(self.price_per_thousand)/1000
        if new>self.token_cap or cost>Decimal(self.cost_cap):
            self.exceeded=True
            raise BudgetExceeded('Simulated per-request token or cost budget exceeded')
        self.receipts.append({'stage':stage,'prompt_tokens':prompt,'completion_tokens':completion,
                             'total_tokens':prompt+completion})

    def preflight(self, query):
        # Input alone is a conservative lower bound before history/crew/cache.
        units=token_units(query)
        if units>self.token_cap or Decimal(units)*Decimal(self.price_per_thousand)/1000>Decimal(self.cost_cap):
            self.exceeded=True
            raise BudgetExceeded('Input exceeds simulated request budget')

    def report(self):
        used=sum(r['total_tokens'] for r in self.receipts)
        return {'token_cap':self.token_cap,'cost_cap_usd':self.cost_cap,
                'simulated_tokens':used,'simulated_cost_usd':str(Decimal(used)*Decimal(self.price_per_thousand)/1000),
                'price_per_thousand_usd':self.price_per_thousand,'actual_expenditure_usd':'0',
                'accounting':'ceil(serialized characters / 4), input plus output per actual model call',
                'receipts':self.receipts}
