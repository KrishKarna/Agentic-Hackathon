def check_emergency(scene):

    emergency_objects = [
        "person",
        "chair",
        "backpack",
        "bottle",
        "table",
        "cell phone"
    ]

    for obj in scene:

        name = obj.get("object")
        position = obj.get("position")
        distance = obj.get("distance")

        if (
            name in emergency_objects
            and position == "center"
            and distance == "near"
        ):

            return (
                f"Stop. {name.capitalize()} "
                "directly ahead."
            )

    return None