class NavigationAgent:
    def __init__(self):
        self.last_message = None
        self.target_position = None   # remember WHICH object (by position), not its old data

    def decide(self, intent, scene, text):
        message = self._compute_message(intent, scene, text)

        if message == self.last_message:
            return None

        self.last_message = message
        return message

    def _compute_message(self, intent, scene, text):
        if intent == "find_seat":
            chairs = [obj for obj in scene if obj["object"] == "chair"]

            if not chairs:
                return "No chair detected yet. Try turning slowly."

            # lock onto the first chair's position the first time we see one
            if self.target_position is None:
                self.target_position = chairs[0]["position"]

            # find the chair matching our locked target position, using CURRENT data
            matching = [c for c in chairs if c["position"] == self.target_position]
            chair = matching[0] if matching else chairs[0]

            if chair["distance"] == "near":
                return "You are close to the chair now."
            return f"Chair found on your {chair['position']}, {chair['distance']} away."

        elif intent == "check_obstacle":
            near_objects = [obj for obj in scene if obj["distance"] == "near"]
            if near_objects:
                names = ", ".join(obj["object"] for obj in near_objects)
                return f"Careful, {names} nearby."
            return "Path looks clear."

        elif intent == "read_sign":
            if text:
                readable = ", ".join(t["content"] for t in text)
                return f"Sign says: {readable}"
            return "No readable text found nearby."

        else:
            return "Sorry, I don't understand that request yet."

    def reset_target(self):
        self.target_position = None
        self.last_message = None


if __name__ == "__main__":
    agent = NavigationAgent()

    print(agent.decide("find_seat", [{"object": "chair", "position": "left", "distance": "far"}], []))
    print(agent.decide("find_seat", [{"object": "chair", "position": "left", "distance": "far"}], []))
    print(agent.decide("find_seat", [{"object": "chair", "position": "left", "distance": "near"}], []))
    print(agent.decide("check_obstacle", [{"object": "person", "position": "center", "distance": "near"}], []))
    print(agent.decide("read_sign", [], [{"content": "EXIT", "position": "right"}]))

    agent.reset_target()
    print(agent.decide("find_seat", [], []))