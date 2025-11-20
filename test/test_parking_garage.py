from datetime import datetime
from unittest import TestCase
from unittest.mock import patch
from unittest.mock import Mock
from mock_folder import GPIO
from mock_folder.SDL_DS3231 import SDL_DS3231
from src.parking_garage import ParkingGarage
from src.parking_garage import ParkingGarageError

class TestParkingGarage(TestCase):

    @patch.object(GPIO, "input")
    def test_check_occupancy(self, mock_distance_sensor: Mock):
        mock_distance_sensor.return_value = True
        system = ParkingGarage()
        outcome = system.check_occupancy(system.INFRARED_PIN2)
        self.assertTrue(outcome)

