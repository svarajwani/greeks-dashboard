import unittest
from unittest.mock import patch, MagicMock
from producer import produce_quote

# python

class TestProducer(unittest.TestCase):
    @patch("producer.requests.get")
    @patch("producer.KafkaProducer")
    def test_produce_one_quote(self, mock_kafka_producer, mock_requests_get):
        # Mock Polygon.io API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "results": [{"symbol": "AAPL", "bid": 150.0, "ask": 151.0}]
        }
        mock_requests_get.return_value = mock_response

        # Mock Kafka producer
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        # Call the function under test
        produce_quote()

        # Assert Polygon.io API was called
        mock_requests_get.assert_called_once()

        # Assert Kafka producer sent the quote to 'quotes' topic
        mock_producer_instance.send.assert_called_once()
        args, kwargs = mock_producer_instance.send.call_args
        self.assertEqual(args[0], "quotes")
        self.assertIn("AAPL", str(args[1]))

if __name__ == "__main__":
    unittest.main()