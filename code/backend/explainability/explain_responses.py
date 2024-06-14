class ExplainResponses:
    _self = None
    _initialized = False

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.explanation = ""

    def collect_explanation(self, text: str) -> None:
        self.explanation += text + '| '

    def clear_explanation(self) -> None:
        self.explanation = ""

    def overall_explanation(self) -> str:
        return self.explanation
