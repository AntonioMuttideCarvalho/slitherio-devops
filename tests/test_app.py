import unittest

import app as slither_app


class SlitherAppTests(unittest.TestCase):
    def setUp(self):
        self.http_client = slither_app.app.test_client()
        self.socket_client = slither_app.socketio.test_client(
            slither_app.app,
            flask_test_client=self.http_client,
        )
        self.original_players = dict(slither_app.players)
        self.original_foods = [dict(food) for food in slither_app.foods]
        slither_app.players.clear()
        slither_app.foods[:] = []

    def tearDown(self):
        if self.socket_client.is_connected():
            self.socket_client.disconnect()
        slither_app.players.clear()
        slither_app.players.update(self.original_players)
        slither_app.foods[:] = self.original_foods

    def test_generate_food_respects_bounds(self):
        food = slither_app.generate_food()
        self.assertGreaterEqual(food["x"], 50)
        self.assertLessEqual(food["x"], 750)
        self.assertGreaterEqual(food["y"], 50)
        self.assertLessEqual(food["y"], 550)

    def test_index_route_returns_login_page(self):
        response = self.http_client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SLITHER.IO CLONE", response.data)

    def test_game_route_uses_query_name_and_default(self):
        response_with_name = self.http_client.get("/game?name=Ismael")
        self.assertEqual(response_with_name.status_code, 200)
        self.assertIn(b"Ismael", response_with_name.data)

        response_default = self.http_client.get("/game")
        self.assertEqual(response_default.status_code, 200)
        self.assertIn(b"Anonymous", response_default.data)

    def test_get_scores_sorts_descending_and_limits_top_10(self):
        for i in range(12):
            slither_app.players[f"sid-{i}"] = {
                "name": f"P{i}",
                "score": i,
                "x": 0,
                "y": 0,
                "color": "#000000",
            }

        scores = slither_app.get_scores()

        self.assertEqual(len(scores), 10)
        self.assertEqual(scores[0], ("P11", 11))
        self.assertEqual(scores[-1], ("P2", 2))

    def test_join_event_registers_player_and_emits_game_state(self):
        slither_app.foods[:] = [{"x": 100, "y": 100}]

        self.socket_client.emit("join", {"name": "Alice"})

        self.assertEqual(len(slither_app.players), 1)
        only_player = next(iter(slither_app.players.values()))
        self.assertEqual(only_player["name"], "Alice")
        self.assertIn("score", only_player)
        self.assertIn("color", only_player)

    def test_move_event_eats_food_and_increases_score(self):
        slither_app.foods[:] = [{"x": 200, "y": 200}]
        self.socket_client.emit("join", {"name": "Bob"})

        player_sid = next(iter(slither_app.players.keys()))
        previous_score = slither_app.players[player_sid]["score"]
        self.socket_client.get_received()

        self.socket_client.emit("move", {"x": 200, "y": 200})

        self.assertEqual(slither_app.players[player_sid]["score"], previous_score + 10)
        self.assertEqual(len(slither_app.foods), 1)
        self.assertNotEqual(slither_app.foods[0], {"x": 200, "y": 200})

    def test_disconnect_event_removes_player(self):
        self.socket_client.emit("join", {"name": "Carol"})
        self.assertEqual(len(slither_app.players), 1)

        self.socket_client.disconnect()

        self.assertEqual(len(slither_app.players), 0)


if __name__ == "__main__":
    unittest.main()