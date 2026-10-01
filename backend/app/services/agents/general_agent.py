from __future__ import annotations

import json
import logging

from app.services.agents.base_agent import BaseAgent
from app.core.ai_engine.context import AIContext
from app.core.ai_engine.response import AIResponse
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class GeneralAgent(BaseAgent):
    """
    General AI Agent

    Responsibilities
    ----------------
    - Answer general questions
    - Explain AI/ML concepts
    - Explain uploaded datasets
    - Explain generated code
    - Synthesize results from previous agents
    - Provide Data Science guidance
    """

    @property
    def name(self) -> str:
        return "General Agent"

    @property
    def capabilities(self) -> list[str]:
        return [
            "general"
        ]

    async def execute(
        self,
        context: AIContext,
    ) -> AIResponse:

        logger.info(
            f"{self.name} started."
        )

        try:

            # =================================================
            # Previous Agent Results
            # =================================================

            previous_results = (
                context.task_results
                if context.task_results
                else {}
            )

            # =================================================
            # Determine Whether This Is A Synthesis Task
            # =================================================

            is_synthesis = len(
                previous_results
            ) > 0

            # =================================================
            # Format Previous Results
            # =================================================

            previous_results_text = ""

            if is_synthesis:

                formatted_results = {}

                for capability, result in previous_results.items():

                    # Avoid sending huge internal objects
                    # directly to the LLM.

                    if isinstance(result, dict):

                        formatted_results[
                            capability
                        ] = result

                    elif isinstance(result, str):

                        formatted_results[
                            capability
                        ] = result

                    else:

                        try:

                            formatted_results[
                                capability
                            ] = str(result)

                        except Exception:

                            formatted_results[
                                capability
                            ] = "Result unavailable."


                try:

                    previous_results_text = json.dumps(
                        formatted_results,
                        indent=2,
                        default=str
                    )

                except Exception:

                    previous_results_text = str(
                        formatted_results
                    )


            # =================================================
            # Dataset Context
            # =================================================

            dataset_context = ""

            if context.dataset is not None:

                dataset = context.dataset

                try:

                    dataset_context = f"""
CURRENT DATASET

Dataset name:
{context.dataset_name or "Uploaded dataset"}

Rows:
{len(dataset)}

Columns:
{list(dataset.columns)}

Data types:
{dataset.dtypes.astype(str).to_dict()}

Missing values:
{dataset.isnull().sum().to_dict()}

Duplicate rows:
{int(dataset.duplicated().sum())}

Sample:
{dataset.head(5).to_string()}
"""

                except Exception as e:

                    logger.warning(
                        f"Dataset context failed: {e}"
                    )

                    dataset_context = """
A dataset is uploaded, but detailed
dataset information could not be extracted.
"""

            else:

                dataset_context = """
NO DATASET IS CURRENTLY UPLOADED.
"""


            # =================================================
            # Build Prompt
            # =================================================

            if is_synthesis:

                prompt = f"""
You are the final synthesis agent of DataNova AI.

The user asked:

{context.message}

Other DataNova AI agents have already executed tasks.

Their results are provided below:

-------------------------------
PREVIOUS AGENT RESULTS
-------------------------------

{previous_results_text}

-------------------------------
DATASET CONTEXT
-------------------------------

{dataset_context}

Your job is to produce the FINAL answer for the user.

IMPORTANT RULES:

1. Use the previous agent results as the primary source.

2. DO NOT repeat the entire analysis.

3. DO NOT perform the same analysis again.

4. Combine the useful findings into one clear answer.

5. If charts were generated, mention that they were generated.

6. If recommendations were generated, summarize the most useful ones.

7. If machine-learning results exist, clearly state the recommended
   model and relevant evaluation information.

8. If code was generated by another task, explain THAT code rather
   than generating a completely different solution.

9. Do not invent statistics or results.

10. Keep the final response professional and concise.

11. Structure the answer using useful headings and bullet points
    when appropriate.

Return ONLY the final answer.
"""

            else:

                prompt = f"""
You are DataNova AI, an intelligent data analysis
and programming assistant.

You are an expert in:

- Data Science
- Machine Learning
- Artificial Intelligence
- Python
- SQL
- Statistics
- Data Visualization
- Exploratory Data Analysis

{dataset_context}

USER REQUEST:

{context.message}

INSTRUCTIONS:

1. Answer the user's request directly.

2. If the user asks about the uploaded dataset,
   use the dataset information provided above.

3. Do not claim that you cannot access the dataset
   when dataset information is available.

4. If the user asks for a simple explanation,
   use simple language.

5. If the user asks for technical information,
   provide technically accurate details.

6. If the user asks for code, provide working code.

7. Do not invent dataset columns, values,
   statistics, or results.

8. Keep the answer professional and useful.

Return ONLY the answer.
"""


            # =================================================
            # Call AI
            # =================================================

            llm_response = AIService.ask(
                prompt
            )


            # =================================================
            # Handle Failure
            # =================================================

            if not llm_response.success:

                return AIResponse(
                    success=False,
                    message=llm_response.message,
                    data=None,
                )


            # =================================================
            # Extract Answer
            # =================================================

            answer = (
                llm_response.data
                or llm_response.message
                or "No response generated."
            )


            # =================================================
            # Memory
            # =================================================

            if hasattr(context, "memory"):

                try:

                    context.memory.conversation_history.append(
                        {
                            "role": "user",
                            "content": context.message,
                        }
                    )

                    context.memory.conversation_history.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                except Exception as memory_error:

                    logger.warning(
                        f"Memory update failed: "
                        f"{memory_error}"
                    )


            # =================================================
            # Final Response
            # =================================================

            return AIResponse(
                success=True,
                message=answer,
                data={
                    "answer": answer,
                    "synthesis": is_synthesis,
                    "source_tasks": list(
                        previous_results.keys()
                    ),
                },
            )


        except Exception as e:

            logger.exception(
                "GeneralAgent failed."
            )

            return AIResponse(
                success=False,
                message=str(e),
                data=None,
            )