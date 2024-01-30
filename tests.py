import unittest
from unittest.mock import patch, MagicMock
from main import handle_message, handle_location, send_flight_information, creating_graph, creating_map, format_data, status_data, format_flight_details, format_flight_details_location

class TestFlightBot(unittest.TestCase):

    @patch('main.bot')
    @patch('main.fr_api')
    def test_handle_message_with_live_flight(self, mock_fr_api, mock_bot):
        mock_message = MagicMock()
        mock_message.text = 'flight123'
        mock_fr_api.search.return_value = {'live': [{'detail': {'reg': 'reg123'}}]}
        mock_fr_api.get_flights.return_value = ['flight1']
        mock_fr_api.get_flight_details.return_value = 'flight_details'
        handle_message(mock_message)
        mock_bot.reply_to.assert_called()
        mock_bot.send_message.assert_called()

    @patch('main.bot')
    @patch('main.fr_api')
    def test_handle_message_without_live_flight(self, mock_fr_api, mock_bot):
        mock_message = MagicMock()
        mock_message.text = 'flight123'
        mock_fr_api.search.return_value = {'live': None}
        handle_message(mock_message)
        mock_bot.reply_to.assert_called()

    @patch('main.bot')
    @patch('main.fr_api')
    def test_handle_location(self, mock_fr_api, mock_bot):
        mock_message = MagicMock()
        mock_message.location.latitude = 1.0
        mock_message.location.longitude = 1.0
        mock_fr_api.get_bounds_by_point.return_value = 'bounds'
        mock_fr_api.get_flights.return_value = ['flight1']
        handle_location(mock_message)
        mock_bot.reply_to.assert_called()
        mock_bot.send_message.assert_called()

    @patch('main.bot')
    def test_send_flight_information_with_photo_url(self, mock_bot):
        send_flight_information('chat_id', {'aircraft': {'images': {'medium': [{'link': 'photo_url'}]}}}, 'reg123', 'current_flight')
        mock_bot.send_media_group.assert_called()

    @patch('main.bot')
    def test_send_flight_information_without_photo_url(self, mock_bot):
        send_flight_information('chat_id', {'aircraft': {'images': {'medium': []}}}, 'reg123', 'current_flight')
        mock_bot.send_media_group.assert_called()

    def test_format_data_with_data(self):
        data = MagicMock()
        data.altitude = 1000
        data.ground_speed = 500
        data.heading = 90
        result = format_data(data)
        self.assertIn('Altitude: 1000', result)
        self.assertIn('Ground Speed: 500', result)
        self.assertIn('Heading: 90', result)

    def test_format_data_without_data(self):
        result = format_data(None)
        self.assertEqual(result, 'Aircraft data not found.')

    def test_status_data_with_in_flight_status(self):
        data = MagicMock()
        data.altitude = 1000
        result = status_data(data)
        self.assertEqual(result, '  Status: In Flight\n')

    def test_status_data_with_on_ground_status(self):
        data = MagicMock()
        data.altitude = 50
        result = status_data(data)
        self.assertEqual(result, '  Status: On Ground\n')

    def test_status_data_without_data(self):
        result = status_data(None)
        self.assertEqual(result, '  Status: N/A \n')

if __name__ == '__main__':
    unittest.main()