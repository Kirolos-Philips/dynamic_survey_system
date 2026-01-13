from rest_framework.exceptions import ValidationError

from apps.surveys.models import Question, QuestionLogic


class SubmissionValidatorService:
    def __init__(
        self,
        survey_data: dict,
        answers_map: dict,
        is_completed: bool = False,
    ):
        self.survey_data = survey_data
        self.answers_map = answers_map
        self.is_completed = is_completed
        # Cache for question visibility and allowed choices
        self._visibility_cache = {}
        self._allowed_choices_cache = {}

    def validate(self):
        # 1. Validate provided answers
        for q_id, answer_value in self.answers_map.items():
            if q_id not in self.survey_data["questions_map"]:
                raise ValidationError({"q_id": f"Invalid question ID: {q_id}"})

            question_data = self.survey_data["questions_map"][q_id]

            # Check visibility first
            if not self.is_question_visible(q_id):
                raise ValidationError(
                    f"Question {q_id} is hidden and should not be answered."
                )

            self.validate_answer_type(question_data, answer_value)
            self.validate_allowed_choices(question_data, answer_value)

        # 2. If submission is final, check for missing required questions
        if self.is_completed:
            self.check_required_questions()

    def is_question_visible(self, q_id: str) -> bool:
        if q_id in self._visibility_cache:
            return self._visibility_cache[q_id]

        rules = self.survey_data["logic_map"].get(q_id, [])
        if not rules:
            self._visibility_cache[q_id] = True
            return True

        has_show_rules = any(r["action"] == "show" for r in rules)
        show_matched = False
        hide_matched = False

        for rule in rules:
            trigger_val = self.answers_map.get(str(rule["trigger_question"]))
            is_match = self.evaluate_condition(
                trigger_val, rule["operator"], rule["value"]
            )

            if is_match:
                if rule["action"] == "show":
                    show_matched = True
                elif rule["action"] == "hide":
                    hide_matched = True

        visible = (show_matched if has_show_rules else True) and not hide_matched
        self._visibility_cache[q_id] = visible
        return visible

    def evaluate_condition(self, val1, operator, val2) -> bool:
        if val1 is None:
            return False

        # Type-safe normalized comparison
        v1 = str(val1).strip().lower()
        v2 = str(val2).strip().lower()

        try:
            if operator == QuestionLogic.OperatorChoices.EQUALS:
                return v1 == v2
            if operator == QuestionLogic.OperatorChoices.NOT_EQUALS:
                return v1 != v2
            if operator == QuestionLogic.OperatorChoices.GREATER_THAN:
                try:
                    return float(v1) > float(v2)
                except (ValueError, TypeError):
                    return v1 > v2
            if operator == QuestionLogic.OperatorChoices.LESS_THAN:
                try:
                    return float(v1) < float(v2)
                except (ValueError, TypeError):
                    return v1 < v2
            if operator == QuestionLogic.OperatorChoices.CONTAINS:
                return v2 in v1
        except (ValueError, TypeError):
            return False
        return False

    def validate_allowed_choices(self, question_data: dict, answer_value):
        q_id = str(question_data["id"])
        rules = self.survey_data["logic_map"].get(q_id, [])
        if not rules or question_data["type"] not in ["radio", "dropdown", "checkbox"]:
            return

        choice_map = {c["id"]: str(c["value"]) for c in question_data["choices"]}
        allowed_values, rule_applied = self._filter_choices_by_rules(choice_map, rules)

        if rule_applied:
            submitted_values = (
                answer_value if isinstance(answer_value, list) else [answer_value]
            )
            for val in submitted_values:
                if str(val) not in allowed_values:
                    raise ValidationError(
                        f"Invalid choice '{val}' for question {q_id}."
                    )

    def _filter_choices_by_rules(self, choice_map: dict, rules: list) -> tuple:
        """Helper to process cumulative choice filtering logic."""
        allowed_values = set(choice_map.values())
        rule_applied = False
        has_limit_match = False

        for rule in rules:
            trigger_val = self.answers_map.get(str(rule["trigger_question"]))
            if not self.evaluate_condition(
                trigger_val, rule["operator"], rule["value"]
            ):
                continue

            action = rule["action"]
            target_ids = rule.get("target_choices", [])
            target_values = {choice_map[cid] for cid in target_ids if cid in choice_map}

            if action == "limit_choices":
                if not has_limit_match:
                    allowed_values.clear()
                    has_limit_match = True
                allowed_values.update(target_values)
                rule_applied = True
            elif action in ["include_choices", "exclude_choices"]:
                if action == "include_choices":
                    allowed_values.update(target_values)
                else:
                    allowed_values -= target_values
                rule_applied = True

        return allowed_values, rule_applied

    def check_required_questions(self):
        for q_id in self.survey_data["questions_map"]:
            # Only check if it's visible or would be visible
            if self.is_question_visible(q_id):
                if q_id not in self.answers_map or self.answers_map[q_id] in [None, ""]:
                    raise ValidationError(
                        f"Question {q_id} is required and has not been answered."
                    )

    def validate_answer_type(self, question_data: dict, value):
        try:
            Question.QuestionType(question_data["type"]).validate_answer_type(value)
        except Exception:
            raise ValidationError(
                f"Answer for question {question_data['id']} is not of type "
                f"{question_data['type']}."
            ) from None
