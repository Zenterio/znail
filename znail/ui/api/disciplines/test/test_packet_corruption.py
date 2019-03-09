import unittest
from unittest.mock import call, patch

from znail.netem.disciplines import PacketCorruption
from znail.netem.tc import Tc
from znail.ui import app


class TestPacketCorruption(unittest.TestCase):

    def setUp(self):
        tc_clear_patcher = patch.object(Tc, 'clear')
        self.tc_clear = tc_clear_patcher.start()
        self.addCleanup(tc_clear_patcher.stop)

        tc_apply_patcher = patch.object(Tc, 'apply')
        self.tc_apply = tc_apply_patcher.start()
        self.addCleanup(tc_apply_patcher.stop)

        self.client = app.test_client()

    def tearDown(self):
        self.client.post('/api/disciplines/packet_corruption/clear')

    def test_empty(self):
        response = self.client.get('/api/disciplines/packet_corruption')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'percent': None})

    def test_can_be_set(self):
        response = self.client.post('/api/disciplines/packet_corruption', json={'percent': 1.0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'ok'})

        last_call = self.tc_apply.call_args_list[-1]
        self.assertEqual(last_call, call({'corrupt': PacketCorruption(percent=1.0)}))

        response = self.client.get('/api/disciplines/packet_corruption')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'percent': 1.0})

    def test_can_be_updated(self):
        response = self.client.post('/api/disciplines/packet_corruption', json={'percent': 1.0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'ok'})

        last_call = self.tc_apply.call_args_list[-1]
        self.assertEqual(last_call, call({'corrupt': PacketCorruption(percent=1.0)}))

        response = self.client.get('/api/disciplines/packet_corruption')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'percent': 1.0})

        response = self.client.post('/api/disciplines/packet_corruption', json={'percent': 2.0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'ok'})

        last_call = self.tc_apply.call_args_list[-1]
        self.assertEqual(last_call, call({'corrupt': PacketCorruption(percent=2.0)}))

        response = self.client.get('/api/disciplines/packet_corruption')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'percent': 2.0})

    def test_can_not_be_set_to_invalid_value(self):
        response = self.client.post('/api/disciplines/packet_corruption', json={'invalid': 'data'})
        self.assertEqual(response.status_code, 422)

    def test_bad_request(self):
        response = self.client.post('/api/disciplines/packet_corruption')
        self.assertEqual(response.status_code, 400)

    def test_can_be_cleared(self):
        response = self.client.post('/api/disciplines/packet_corruption/clear')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'ok'})

        last_call = self.tc_apply.call_args_list[-1]
        self.assertEqual(last_call, call({}))
