from langgraph.graph import StateGraph, START, END

from backend.app.agents.profileAnalyzer import ProfileAnalyzerAgent
from backend.app.agents.atsOptimizer import ATSOptimizerAgent
from backend.app.agents.resumeWriter import ResumeWriterAgent
from backend.app.agents.reviewAgent import ReviewerAgent

from backend.app.graph.state import ResumeState
from backend.app.llm.gemini import GeminiService


class ResumeGraph:

    def __init__(self):
        gemini_service = GeminiService()

        self.profile_agent = ProfileAnalyzerAgent(
            gemini_service
        )

        self.ats_agent = ATSOptimizerAgent(
            gemini_service
        )

        self.writer_agent = ResumeWriterAgent(
            gemini_service
        )

        self.reviewer_agent = ReviewerAgent(
            gemini_service
        )

    async def profile_node(
        self,
        state: ResumeState
    ) -> dict:

        result = await self.profile_agent.run(
            resume_text=state["resume_text"]
        )

        return {
            "profile_analysis": result
        }

    async def ats_node(
        self,
        state: ResumeState
    ) -> dict:

        result = await self.ats_agent.run(
            profile_analysis=state["profile_analysis"],
            job_description=state["job_description"]
        )

        return {
            "ats_analysis": result
        }

    async def writer_node(
        self,
        state: ResumeState
    ) -> dict:

        result = await self.writer_agent.run(
            resume_text=state["resume_text"],
            profile_analysis=state["profile_analysis"],
            ats_analysis=state["ats_analysis"],
            job_description=state["job_description"]
        )

        return {
            "generated_resume": result
        }

    async def reviewer_node(
        self,
        state: ResumeState
    ) -> dict:

        result = await self.reviewer_agent.run(
            original_resume=state["resume_text"],
            generated_resume=state["generated_resume"]
        )

        return {
            "review_result": result
        }

    def build(self):

        graph = StateGraph(ResumeState)

        graph.add_node(
            "profile_analyzer",
            self.profile_node
        )

        graph.add_node(
            "ats_optimizer",
            self.ats_node
        )

        graph.add_node(
            "resume_writer",
            self.writer_node
        )

        graph.add_node(
            "reviewer",
            self.reviewer_node
        )

        graph.add_edge(
            START,
            "profile_analyzer"
        )

        graph.add_edge(
            "profile_analyzer",
            "ats_optimizer"
        )

        graph.add_edge(
            "ats_optimizer",
            "resume_writer"
        )

        graph.add_edge(
            "resume_writer",
            "reviewer"
        )

        graph.add_edge(
            "reviewer",
            END
        )

        return graph.compile()