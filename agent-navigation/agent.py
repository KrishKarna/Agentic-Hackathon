class NavigationAgent:
    def __init__(self):
        self.last_message = None
        self.target_object = None
        self.target_position = None

    def decide(self, intent, scene, text):
        message = self._compute_message(intent, scene, text)

        if message == self.last_message:
            return None

        self.last_message = message
        return message

    def _compute_message(self, intent, scene, text):

        if intent == "check_obstacle":
            return self._check_obstacles(scene)

        elif intent == "describe_scene":
            return self._describe_scene(scene)

        elif intent == "find_object":
            return self._find_object(scene)

        elif intent == "find_entrance":
            return self._find_entrance(scene, text)

        elif intent == "read_sign":
            return self._read_sign(text)

        else:
            return "Sorry, I don't understand that request yet."

    def _check_obstacles(self, scene):
        near_objects = [
            obj for obj in scene
            if obj["distance"] == "near"
        ]

        if not near_objects:
            return "Path looks clear."

        warnings = []

        for obj in near_objects:
            position = obj["position"]
            name = obj["object"]

            if position == "center":
                warnings.append(f"{name} directly ahead")
            else:
                warnings.append(f"{name} on your {position}")

        return "Careful, " + ", ".join(warnings) + "."

    def _describe_scene(self, scene):
        if not scene:
            return "I cannot detect any objects."

        descriptions = []

        for obj in scene:
            name = obj["object"]
            position = obj["position"]
            distance = obj["distance"]

            descriptions.append(
                f"{name} on your {position}, {distance} away"
            )

        return "I see " + "; ".join(descriptions) + "."

    def _find_object(self, scene):
        if self.target_object is None:
            return "What object should I look for?"

        objects = [
            obj for obj in scene
            if obj["object"] == self.target_object
        ]

        if not objects:
            return f"I cannot see a {self.target_object}. Try turning slowly."

        if self.target_position is None:
            self.target_position = objects[0]["position"]

        matching = [
            obj for obj in objects
            if obj["position"] == self.target_position
        ]

        target = matching[0] if matching else objects[0]

        if target["distance"] == "near":
            return f"You are close to the {self.target_object}."

        return (
            f"{self.target_object.capitalize()} is on your "
            f"{target['position']}, {target['distance']} away."
        )

    def _find_entrance(self, scene, text):
        entrance_words = [
            "entrance",
            "entry",
            "enter",
            "exit"
        ]

        for item in text:
            content = item.get("content", "").lower()

            for word in entrance_words:
                if word in content:
                    position = item.get("position", "ahead")

                    return (
                        f"{word.capitalize()} sign detected "
                        f"on your {position}."
                    )

        return "I cannot identify an entrance yet."

    def _read_sign(self, text):
        if not text:
            return "No readable text found nearby."

        readable = [
            item["content"]
            for item in text
            if item.get("content")
        ]

        if not readable:
            return "No readable text found nearby."

        return "Sign says: " + ", ".join(readable)

    def set_target(self, object_name):
        self.target_object = object_name.lower()
        self.target_position = None
        self.last_message = None

    def reset_target(self):
        self.target_object = None
        self.target_position = None
        self.last_message = None


if __name__ == "__main__":

    agent = NavigationAgent()

    scene = [
        {
            "object": "person",
            "position": "center",
            "distance": "near"
        },
        {
            "object": "cell phone",
            "position": "right",
            "distance": "far"
        },
        {
            "object": "backpack",
            "position": "left",
            "distance": "medium"
        }
    ]

    print(agent.decide("check_obstacle", scene, []))

    agent.reset_target()
    print(agent.decide("describe_scene", scene, []))

    agent.reset_target()
    agent.set_target("cell phone")
    print(agent.decide("find_object", scene, []))

    agent.reset_target()
    print(
        agent.decide(
            "read_sign",
            [],
            [
                {
                    "content": "EXIT",
                    "position": "right"
                }
            ]
        )
    )