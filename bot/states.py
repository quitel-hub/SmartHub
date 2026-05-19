"""
@file states.py
@brief Модуль керування станами користувача в Telegram-боті.

Використовує механізм Finite State Machine (FSM) бібліотеки aiogram 
для реалізації поведінкового патерну State (Стан). Це дозволяє 
контролювати життєвий цикл взаємодії користувача з ботом.
"""

from aiogram.fsm.state import State, StatesGroup


# PATTERN 6: STATE
class UserState(StatesGroup):
    """
    @brief Клас станів користувача (FSM).
    
    Реалізація патерну State. Керує життєвим циклом взаємодії користувача.
    Основне призначення — блокування користувацького вводу під час 
    асинхронної обробки фотографій, щоб запобігти спаму запитами 
    до пулу OCR (ProcessorPool).
    """
    idle = State()       
    processing = State() 