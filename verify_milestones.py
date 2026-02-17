
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import logging

# Setup path
sys.path.append(os.getcwd())

print("Setting up mocks...", flush=True)
# Mock modules that might be missing or problematic
sys.modules['telegram'] = MagicMock()
sys.modules['telegram.ext'] = MagicMock()

# Import the class to test
print("Importing SignalTracker...", flush=True)
try:
    from crypto_bot_pro_v35 import SignalTracker, AdvancedTradingConfig
    print("Import successful!", flush=True)
except ImportError as e:
    print(f"ImportError: {e}", flush=True)
    # Try to mock dependencies that might cause this
    sys.modules['binance'] = MagicMock()
    sys.modules['binance.client'] = MagicMock()
    sys.modules['binance.enums'] = MagicMock()
    sys.modules['pandas'] = MagicMock()
    sys.modules['numpy'] = MagicMock()
    sys.modules['ta'] = MagicMock()
    try:
        from crypto_bot_pro_v35 import SignalTracker, AdvancedTradingConfig
        print("Import successful after mocking!", flush=True)
    except Exception as e2:
        print(f"Fatal Import Error: {e2}", flush=True)
        sys.exit(1)

class TestMilestones(unittest.TestCase):
    def setUp(self):
        # Config setup
        self.config = MagicMock()
        self.config.PROFIT_MILESTONES = [1.0, 2.0, 3.0]
        self.config.MIN_NEURAL_DESTACADA = 50.0
        self.config.MIN_TECHNICAL_DESTACADA = 40.0
        self.config.MIN_ALIGNMENT_DESTACADA = 33.0
        
        # Telegram client mock
        self.telegram_client = MagicMock()
        self.telegram_client.sent_milestones = {}
        
        # SignalTracker setup
        self.tracker = SignalTracker(self.config)
        self.tracker.set_telegram_client(self.telegram_client)
        
    def test_milestone_notification(self):
        print("\nTesting Milestone Notification...", flush=True)
        
        # 1. Add a signal
        signal_hash = "test_hash_123"
        signal_data = {
            'symbol': 'BTCUSDT',
            'entry_price': 50000.0,
            'neural_score': 90.0,
            'technical_percentage': 80.0,
            'alignment_percentage': 85.0,
            'stop_loss': 49000.0,
            'take_profit': 51500.0
        }
        
        with self.tracker.lock:
            self.tracker.tracked_signals[signal_hash] = {
                'status': 'CONFIRMADA', 
                'signal_data': signal_data,
                'entry_price': 50000.0,
                'entry_price_confirmada': 50000.0,
                'current_price': 50000.0,
                'is_buy': True,
                'max_profit': 0.0,
                'start_time': None
            }
            
        # 2. Update progress to 1.1% (First Milestone is 1.0%)
        current_price = 50000.0 * 1.011 # +1.1%
        print(f"Updating price to {current_price} (+1.1%)", flush=True)
        
        self.tracker.update_signal_progress(signal_hash, current_price)
        
        # 3. Verify Telegram call
        if self.telegram_client.send_message.call_count == 1:
            print("Telegram send_message was called once.", flush=True)
        else:
            print(f"Telegram send_message called {self.telegram_client.send_message.call_count} times.", flush=True)
            
        self.telegram_client.send_message.assert_called_once()
        args = self.telegram_client.send_message.call_args[0][0]
        # print(f"Telegram Message Sent:\n{args}", flush=True)
        
        self.assertIn("HITO 1 ALCANZADO", args)
        self.assertIn("BTCUSDT", args)
        # Match HTML format
        self.assertIn("Profit Actual:</b> +1.10%", args)
        print("Milestone 1 Verified OK", flush=True)
        
        # 4. Verify sent_milestones updated
        self.assertIn(1.0, self.telegram_client.sent_milestones['BTCUSDT'])
        
        # 5. Update to 1.5% (No new milestone)
        self.telegram_client.send_message.reset_mock()
        current_price = 50000.0 * 1.015
        print(f"Updating price to {current_price} (+1.5%)", flush=True)
        self.tracker.update_signal_progress(signal_hash, current_price)
        self.telegram_client.send_message.assert_not_called()
        print("No duplicate milestone OK", flush=True)
        
        # 6. Update to 2.1% (Second Milestone 2.0%)
        current_price = 50000.0 * 1.021
        print(f"Updating price to {current_price} (+2.1%)", flush=True)
        self.tracker.update_signal_progress(signal_hash, current_price)
        self.telegram_client.send_message.assert_called_once()
        args = self.telegram_client.send_message.call_args[0][0]
        self.assertIn("HITO 2 ALCANZADO", args)
        print("Milestone 2 Verified OK", flush=True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
