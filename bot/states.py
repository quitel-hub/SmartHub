from aiogram.fsm.state import State, StatesGroup


# PATTERN 6: STATE
class UserState(StatesGroup):
    """
    State pattern implementation: Manages the lifecycle of a user's interaction.
    Prevents the user from spamming multiple processing requests.
    """
    idle = State()       
    processing = State() 