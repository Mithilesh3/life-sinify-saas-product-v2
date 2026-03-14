from typing import Dict, Any
from openai import AzureOpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

azure_client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_OPENAI_API_VERSION,
)

DEPLOYMENT_NAME = settings.AZURE_OPENAI_DEPLOYMENT


def build_prompt(flat_data: Dict[str, Any], scores: Dict[str, Any]) -> str:
    return f"""
User Profile:
{flat_data}

System Scores:
{scores}

Generate a structured professional life analysis report.
"""


def generate_ai_narrative(flat_data: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
    prompt = build_prompt(flat_data, scores)

    response = azure_client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are a behavioral intelligence strategist."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1500,
    )

    content = response.choices[0].message.content

    usage = response.usage

    logger.info(
        f"AI Usage - Prompt: {usage.prompt_tokens}, "
        f"Completion: {usage.completion_tokens}, "
        f"Total: {usage.total_tokens}"
    )

    return {
        "ai_full_narrative": content,
        "token_usage": usage.total_tokens,
    }