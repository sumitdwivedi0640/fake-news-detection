from typing import List, TypedDict

try:
    from langgraph.graph import END, StateGraph  # type: ignore
except Exception:  # pragma: no cover
    END = None
    StateGraph = None

from src.core.logger import logger
from src.services.classifier import ClassifierService
from src.services.reasoner import ReasonerService
from src.services.retriever import RetrieverService
from src.services.shap_explainer import SHAPService


class AgentState(TypedDict, total=False):
    news: str
    prediction: str
    confidence: float
    evidence: List[str]
    explanation: str
    shap: dict
    error: str


class FakeNewsAgentGraph:
    def __init__(self) -> None:
        self.classifier = ClassifierService()
        self.retriever = RetrieverService()
        self.reasoner = ReasonerService()
        self.shap_service = SHAPService(self.classifier)
        self.graph = self._build_graph()

    def _classifier_node(self, state: AgentState) -> AgentState:
        try:
            result = self.classifier.predict(state["news"])
            shap_data = self.shap_service.explain(state["news"])
            return {**state, **result, "shap": shap_data}
        except Exception as exc:
            logger.exception("Classifier node failed: %s", exc)
            return {**state, "error": f"classifier_failed: {exc}"}

    def _retriever_node(self, state: AgentState) -> AgentState:
        try:
            evidence = self.retriever.fetch_news_articles(state["news"])
            return {**state, "evidence": evidence}
        except Exception as exc:
            logger.exception("Retriever node failed: %s", exc)
            return {**state, "evidence": [], "error": f"retriever_failed: {exc}"}

    def _reasoner_node(self, state: AgentState) -> AgentState:
        if state.get("error"):
            return {**state, "explanation": "Analysis partially failed due to an internal error."}
        try:
            explanation = self.reasoner.generate_explanation(
                news=state["news"],
                prediction=state["prediction"],
                evidence=state.get("evidence", []),
            )
            return {**state, "explanation": explanation}
        except Exception as exc:
            logger.exception("Reasoner node failed: %s", exc)
            return {**state, "explanation": "Explanation generation failed.", "error": f"reasoner_failed: {exc}"}

    def _build_graph(self):
        if StateGraph is None or END is None:
            logger.warning("langgraph is not installed. Falling back to sequential pipeline mode.")
            return None

        workflow = StateGraph(AgentState)
        workflow.add_node("classifier", self._classifier_node)
        workflow.add_node("retriever", self._retriever_node)
        workflow.add_node("reasoner", self._reasoner_node)

        workflow.set_entry_point("classifier")
        workflow.add_edge("classifier", "retriever")
        workflow.add_edge("retriever", "reasoner")
        workflow.add_edge("reasoner", END)
        return workflow.compile()

    def run(self, news: str) -> AgentState:
        initial_state: AgentState = {"news": news}
        if self.graph is None:
            # Fallback path when langgraph dependency is unavailable.
            state = self._classifier_node(initial_state)
            state = self._retriever_node(state)
            state = self._reasoner_node(state)
            return state
        return self.graph.invoke(initial_state)
