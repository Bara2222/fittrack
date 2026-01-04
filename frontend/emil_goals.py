"""
Goals initialization for test user Emil
This will be imported and used in the frontend to initialize goals for Emil
"""

EMIL_GOALS = [
    {
        'icon': '💪',
        'name': 'Bench Press 100kg',
        'description': 'Dosáhnout bench pressu 100kg s čistou technikou',
        'current': 80.0,
        'target': 100.0,
        'unit': 'kg',
        'deadline': '31.03.2026',
        'completed': False,
        'type': 'strength'
    },
    {
        'icon': '⚖️',
        'name': 'Zhubnout na 72.5kg',
        'description': 'Snížit váhu o 3kg zdravým způsobem',
        'current': 75.5,
        'target': 72.5,
        'unit': 'kg',
        'deadline': '28.02.2026',
        'completed': False,
        'type': 'weight'
    },
    {
        'icon': '🎯',
        'name': '10 Pull-upů',
        'description': 'Zvládnout 10 shybů v sérii bez dopomoci',
        'current': 6,
        'target': 10,
        'unit': 'opakování',
        'deadline': '15.04.2026',
        'completed': False,
        'type': 'strength'
    },
    {
        'icon': '🔥',
        'name': 'Trénink 4x týdně',
        'description': 'Pravidelně trénovat alespoň 4x týdně po dobu 2 měsíců',
        'current': 3,
        'target': 4,
        'unit': 'tréninky/týden',
        'deadline': '31.03.2026',
        'completed': False,
        'type': 'frequency'
    }
]

def initialize_emil_goals():
    """Initialize goals for Emil user"""
    return EMIL_GOALS.copy()  # Return a copy to avoid reference issues