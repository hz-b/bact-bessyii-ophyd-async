from dataclasses import dataclass


@dataclass(frozen=True)
class TopUpPolicy:
    target_current: float
    acceptable_loss: float

    def reinjection_required(self, actual_current: float) -> bool:
        return actual_current < (self.target_current - self.acceptable_loss)
