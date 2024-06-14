# copied file from the main branch of speech_system

def get_issue(issue_object):
    if not issue_object:
        return None
    issue_name = issue_object["method"]
    if issue_name == "simple_issue":
        return SimpleIssue(issue_object)
    elif issue_name == "too_few_parts":
        return TooFewParts(issue_object)
    elif issue_name == "too_few_slots":
        return TooFewSlots(issue_object)
    elif issue_name == "too_few_pivots":
        return TooFewPivots(issue_object)
    elif issue_name == "inverse_kinematic_failed":
        return InverseKinematicFailed(issue_object)
    elif issue_name == "collision_occurred_issue":
        return CollisionOccurredIssue(issue_object)
    elif issue_name == "time_out_issue":
        return TimeOutIssue(issue_object)
    elif issue_name == "not_graspable_issue":
        return NotGraspableIssue(issue_object)
    elif issue_name == "not_container_issue":
        return NotContainerIssue(issue_object)
    elif issue_name == "robot_collision_issue":
        return RobotCollisionIssue(issue_object)
    elif issue_name == "pour_into_pattern":
        return PourIntoPattern(issue_object)
    elif issue_name == "too_few_pattern_places":
        return TooFewPatternPlaces(issue_object)


class OutputUtterance:
    def __init__(self, recognition = None, is_hotword: bool = False, issue_object=None, docs=None):
        self.recognition = recognition
        self.is_hotword = is_hotword
        self.issue = get_issue(issue_object)
        self.docs = docs


class Answer(OutputUtterance):
    def __init__(self, id: int, recognition, source_layer: str, docs, acknowledged: bool):
        super().__init__(recognition=recognition, docs=docs)
        self.id = id
        self.source_layer = source_layer
        self.acknowledged = acknowledged

    def serialize(self, res: dict) -> dict:
        res['ID'] = self.id
        res['type'] = 'feedback_answer'
        res['Source_Layer'] = self.source_layer
        res['Acknowledged'] = str(self.acknowledged).lower()
        return res


class Issue:
    def __init__(self, args):
        self.args = args

    def to_utterance(self):
        pass


class SimpleIssue(Issue):
    def to_utterance(self):
        if self.args["msg"] == 'notify':
            return "Instruction completed successfully"
        return self.args["msg"]


class TooFewParts(Issue):
    def to_utterance(self):
        part_spec = self.args["part_spec"]
        existing_amount = self.args["existing_amount"]
        noun = part_spec["type"]
        is_singular = existing_amount == 1
        type_verbalization = noun + "s" if is_singular else ""
        if existing_amount == 0:
            return "There are no " + part_spec["color"] + " " + noun + "s in this scene."
        verb = "is" if is_singular else "are"
        instead = "" if part_spec["is_all"] else " instead of " + str(part_spec["amount"])
        return "There " + verb + " only " + str(existing_amount) + " " + part_spec["color"] + " " + type_verbalization + \
               instead + "."


class TooFewSlots(Issue):
    def to_utterance(self):
        object_amount = self.args["object_amount"]
        rejected_objects = self.args["rejected_objects"]
        is_pattern = self.args["is_pattern"]
        if object_amount <= rejected_objects:
            return "There are no free places for the objects."
        movable_amount = object_amount - rejected_objects
        if is_pattern:
            return "Only " + str(movable_amount) + " out of " + str(object_amount) + " objects can be placed in " \
                                                                                     "the pattern."
        slot_verbalization = "place is" if movable_amount == 1 else "places are"
        return "Only " + str(movable_amount) + slot_verbalization + " free."


class TooFewPivots(Issue):
    def to_utterance(self):
        object_amount = self.args["object_amount"]
        rejected_objects = self.args["rejected_objects"]
        operation_name = self.args["operation_name"]
        if object_amount <= rejected_objects:
            return "There is no such relations object."
        movable_amount = object_amount - rejected_objects
        movable_objects = "object" if movable_amount == 1 else "objects"
        return "Only " + str(movable_amount) + " " + movable_objects + "can be moved because there are too few " \
                                                                       "relation objects."


class InverseKinematicFailed(Issue):
    def to_utterance(self):
        object_amount = int(self.args["object_amount"])
        rejected_objects = int(self.args["rejected_objects"])
        start_error = int(self.args["start_error"])
        goal_error = int(self.args["goal_error"])
        explanation = ""
        if start_error > 0 and goal_error > 0:
            explanation = "because both object and target positions are out of robot range."
        elif start_error > 0:
            explanation = "because the object positions are outside the robot range."
        elif goal_error > 0:
            explanation = "because the target positions are out of robot range."
        if object_amount <= rejected_objects:
            return "The task cannot be performed " + explanation
        movable_amount = object_amount - rejected_objects
        movable_objects = "object" if movable_amount == 1 else "objects"
        return "Only " + str(movable_amount) + " " + movable_objects + " can be changed, " + explanation


class CollisionOccurredIssue(Issue):
    def to_utterance(self):
        collision_amount = self.args["collision_amount"]
        collision_amount_verbalization = "collision" if collision_amount == 1 else "collisions"
        return str(collision_amount) + " " + collision_amount_verbalization + " would occur during execution."


class TimeOutIssue(Issue):
    def to_utterance(self):
        return "The robot could not perform the movement."


class NotGraspableIssue(Issue):
    def to_utterance(self):
        part_spec = self.args["part_spec"]
        type_verbalization = part_spec + "s"
        return type_verbalization + " are not tangible for me."


class NotContainerIssue(Issue):
    def to_utterance(self):
        part_spec = self.args["part_spec"]
        type_verbalization = part_spec + "s"
        return type_verbalization + " are not containers."


class RobotCollisionIssue(Issue):
    def to_utterance(self):
        return "A robot collision would occur during the movement."


class PourIntoPattern(Issue):
    def to_utterance(self):
        return "You cannot pour into a pattern."


class TooFewPatternPlaces(Issue):
    def to_utterance(self):
        part_spec = self.args["part_spec"]
        existing_amount = self.args["existing_amount"]
        is_singular = existing_amount == 1
        type_verbalization = part_spec + " place" if is_singular \
            else part_spec + " places"

        if existing_amount == 0:
            return "There are no " + type_verbalization + " in this scene."

        verb = "exists" if existing_amount == 1 else "exist"
        instead = "" if part_spec["is_all"] else " instead of " + str(part_spec["amount"])
        return "There " + verb + " only " + str(existing_amount) + " " + type_verbalization + instead + "."
