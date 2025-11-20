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
    def test_check_occupancy(self, distance_sensor: Mock):
        distance_sensor.return_value = True
        system = ParkingGarage()
        outcome = system.check_occupancy(system.INFRARED_PIN2)
        self.assertTrue(outcome)

    def test_check_occupancy_raises_error(self):
        garage = ParkingGarage()
        self.assertRaises(ParkingGarageError, garage.check_occupancy, garage.LED_PIN)

    @patch.object(GPIO, "input")
    def test_get_number_occupied_spots(self,distance_sensor: Mock):
        distance_sensor.side_effect = [True,False,True]
        garage = ParkingGarage()
        number_of_occupied_spots = garage.get_number_occupied_spots()
        self.assertEqual(2, number_of_occupied_spots)

    @patch.object(SDL_DS3231, "read_datetime")
    def test_calculate_parking_fee(self,rtc: Mock):
        rtc.return_value = datetime(2025,11,20,15,24)
        garage = ParkingGarage()
        fee = garage.calculate_parking_fee(datetime(2025,11,20,12,30))
        self.assertEqual(7.50, fee)