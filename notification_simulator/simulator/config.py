# config.py
# All configuration parameters for the simulation

CONFIG = {
    "channels": ["email", "push", "sms", "in_app"],
    "max_retries": 3,
    "base_backoff_seconds": 2, # Wait time multiplier for retries
    "rate_limits_per_sec": {
        "email": 5,
        "push": 10,
        "sms": 2,
        "in_app": 20
    },
    # Simulation timing (in seconds) - artificially slows down for visualization
    "simulated_delay": {
        "gateway": 0.5,
        "preference_check": 0.5,
        "online_check": 0.5,
        "fanout": 0.4,
        "worker_process": 1.0,
        "slow_mode_multiplier": 3.0
    },
    # Defined Event Types and their corresponding initial channels
    "events": {
        "user.signup": {
            "type": "user.signup",
            "priority": "normal",
            "default_channels": ["email", "in_app"]
        },
        "order.placed": {
            "type": "order.placed",
            "priority": "normal",
            "default_channels": ["email", "push", "sms"]
        },
        "password.reset": {
            "type": "password.reset",
            "priority": "critical",
            "default_channels": ["email"]
        },
        "promo.flash_sale": {
            "type": "promo.flash_sale",
            "priority": "promotional",
            "default_channels": ["email", "push"]
        }
    }
}
