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
    def test_get_number_occupied_spots(self, distance_sensor: Mock):
        distance_sensor.side_effect = [True, False, True]
        garage = ParkingGarage()
        number_of_occupied_spots = garage.get_number_occupied_spots()
        self.assertEqual(2, number_of_occupied_spots)

    @patch.object(SDL_DS3231, "read_datetime")
    def test_calculate_parking_fee(self, rtc: Mock):
        rtc.return_value = datetime(2025, 11, 20, 15, 24)
        garage = ParkingGarage()
        fee = garage.calculate_parking_fee(datetime(2025, 11, 20, 12, 30))
        self.assertEqual(7.50, fee)

    @patch.object(SDL_DS3231, "read_datetime")
    def test_calculate_parking_fee_more_minutes(self, rtc: Mock):
        rtc.return_value = datetime(2025, 11, 20, 15, 40)
        garage = ParkingGarage()
        fee = garage.calculate_parking_fee(datetime(2025, 11, 20, 12, 30))
        self.assertEqual(10, fee)

    @patch.object(SDL_DS3231, "read_datetime")
    def test_calculate_parking_fee_on_weekend(self, rtc: Mock):
        rtc.return_value = datetime(2025, 11, 22, 15, 24)
        garage = ParkingGarage()
        fee = garage.calculate_parking_fee(datetime(2025, 11, 22, 12, 30))
        self.assertEqual(9.375, fee)

    @patch.object(ParkingGarage, "change_servo_angle")
    def test_open_garage_door(self, motor: Mock):
        garage = ParkingGarage()
        garage.open_garage_door()
        self.assertTrue(garage.door_open)
        motor.assert_called_once_with(12)


    @patch.object(ParkingGarage, "change_servo_angle")
    def test_close_garage_door(self, motor: Mock):
        garage = ParkingGarage()
        garage.door_open = True
        garage.close_garage_door()
        self.assertFalse(garage.door_open)
        motor.assert_called_once_with(2)

    @patch.object(GPIO, "output")
    def test_turn_on_red_light(self, light: Mock):
        garage = ParkingGarage()
        garage.turn_on_red_light()
        self.assertTrue(garage.red_light_on)
        light.assert_called_once_with(garage.LED_PIN, True)

    @patch.object(GPIO, "output")
    def test_turn_off_red_light(self, mock_light: Mock):
        garage = ParkingGarage()
        garage.turn_off_red_light()
        mock_light.assert_called_with(garage.LED_PIN, False)
        self.assertFalse(garage.red_light_on)

    @patch.object(GPIO, "output")
    @patch.object(ParkingGarage, "get_number_occupied_spots")
    def test_manage_light_when_parking_full(self, mock_spots: Mock, mock_light: Mock):
        mock_spots.return_value = 3
        garage = ParkingGarage()
        garage.manage_red_light()
        mock_light.assert_called_with(garage.LED_PIN, True)
        self.assertTrue(garage.red_light_on)

    @patch.object(GPIO, "output")
    @patch.object(ParkingGarage, "get_number_occupied_spots")
    def test_manage_light_parking_not_full(self, mock_spots: Mock, mock_light: Mock):
        mock_spots.return_value = 2
        garage = ParkingGarage()
        garage.manage_red_light()
        mock_light.assert_called_with(garage.LED_PIN, False)
        self.assertFalse(garage.red_light_on)
