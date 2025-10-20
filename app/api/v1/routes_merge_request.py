import json
import openai
import gitlab
from cerebras.cloud.sdk import Cerebras

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from app.core.config import settings
from app.db.session import get_db

from app.models.ai_providers import ProvidersTypes
from app.schemas.merge_request import MergeRequestInfoResponse, MergeRequestInput

from app.repositories import templates, providers, models


router_merge = APIRouter(prefix="/merge-request")


def process_with_open_router(model: str, messages: []):
    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPEN_ROUTER_API_KEY,
    )

    llm_response = client.chat.completions.create(model=model, messages=messages)

    return llm_response


def process_with_cerebras(model: str, messages: []):
    client = Cerebras(api_key=settings.CEREBRAS_API_KEY)

    llm_response = client.chat.completions.create(
        messages=messages,
        model=model,
    )

    return llm_response


def get_ai_mr_data(
    diffs: str,
    template: str,
    title: str,
    user_context: str,
    provider_type: ProvidersTypes,
    model: str,
):
    system_prompt = f"""
        You are an assistant that writes GitLab Merge Request (MR) titles and descriptions based on provided information.
        You must not make network calls, execute tools, or include anything outside the strict output format.
        Your only goal is to generate a professional, concise, and accurate MR title and description, following a provided template.

        Inputs Provided:
        - PROJECT_CONTEXT: A short description of what this project does.
        - DIFF_TEXT: The complete unified diff of all changes between the feature branch and target branch .
        - TITLE_TEMPLATE: A short string template for the MR title.
        - DESCRIPTION_TEMPLATE: A Markdown template for the MR description body .
        - USER_NOTES: Optional human-written notes that provide context, intent, or goals for this MR.

        Output Contract (Strict):
        Return only the following two sections. Any text outside these tags will be ignored and considered an error.

        [title:start]
        <one line MR title>
        [title:end]
        [description:start]
        <Markdown-formatted MR description>
        [description:end]

        Rules:
        - Do not add anything before, between, or after these tags.
        - The title must fit in one line (max 120 characters, no trailing period).
        - The description must be valid Markdown that GitLab will render properly.
        - If any information is missing, insert a 'TODO:' note (e.g., 'TODO: Add Jira ticket link').

        Behavior Rules:
        1. Understand what changed:
        - Use the DIFF_TEXT to infer what files, features, or behaviors changed.
        - Focus on what the developer changed, why, and potential effects.

        2. Use templates correctly:
        - Replace placeholders like {{what_changed}}, {{why}}, {{impact}}, etc. with real information.
        - If the template doesn’t include placeholders, fill it naturally with what fits.

        3. Writing style:
        - Professional and concise.
        - Neutral tone (avoid 'I' or 'we').
        - Use short sentences and bullet points for clarity.
        - Use Markdown headers (##) for sections.
        - If code snippets are useful, use fenced code blocks.

        4. Sections (if not provided in template):
        ## What changed
        {{what_changed}}

        ## Why
        {{why}}

        ## Implementation details
        {{implementation}}

        ## Risks / Breaking changes
        {{risks}}

        ## Testing
        {{testing}}

        ## Rollback plan
        {{rollback}}

        ## Links
        {{links}}

        5. Accuracy:
        - Never invent code, issue numbers, or links that don’t exist.
        - Use TODO if the data isn’t in context.
        - Summarize diffs — don’t paste large code blocks.

        6. Token discipline:
        - Prioritize 'What changed', 'Why', 'Testing', and 'Risks' sections if output must be truncated.
        - Keep total output concise (usually under 1000 tokens).

        Example Output:
        [title:start]
        feat(giftcards): add API endpoints and validation for gift card creation
        [title:end]
        [description:start]
        ## What changed
        - Added POST /api/giftcards endpoint for issuing new cards.
        - Implemented validation logic for card amount and expiration.
        - Updated GiftCardService and related unit tests.

        ## Why
        To support gift card creation for upcoming promo campaigns.

        ## Risks / Breaking changes
        - New validation could block some edge cases if amount/expiry are misconfigured.

        ## Testing
        - Added unit tests in tests/services/test_giftcards.py.
        - Verified 200/400 responses with mock data.

        ## Rollback plan
        Revert the new service class or disable the /api/giftcards route.

        ## Links
        TODO: Add Jira or issue link.
        [description:end]
    """

    user_message = f"""
        PROJECT_CONTEXT:
        {user_context or 'TODO: No project context provided.'}

        DIFF_TEXT:
        {diffs}

        TITLE_TEMPLATE:
        {title}

        DESCRIPTION_TEMPLATE:
        {template}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    if provider_type == ProvidersTypes.open_router:
        llm_response = process_with_open_router(model, messages)
    elif provider_type == ProvidersTypes.cerebras:
        llm_response = process_with_cerebras(model, messages)

    try:
        return llm_response.choices[0].message.content
    except (AttributeError, IndexError, KeyError):
        return None


def extract_section(text, start_tag, end_tag):
    """Extract text between two markers safely using split."""
    try:
        return text.split(start_tag, 1)[1].split(end_tag, 1)[0].strip()
    except IndexError:
        return None  # In case tags are missing


def truncate_diff(diff_text: str, max_lines: int = 50) -> str:
    """Keep full diff if small, otherwise truncate with context"""
    if not diff_text:
        return ""

    lines = diff_text.split("\n")
    if len(lines) <= max_lines:
        return diff_text

    # Keep first max_lines/2 and last max_lines/2 lines to preserve context
    half = max_lines // 2
    truncated = (
        lines[:half]
        + [f"\n... ({len(lines) - max_lines} lines omitted) ...\n"]
        + lines[-half:]
    )
    return "\n".join(truncated)


def build_optimized_diffs(compare):

    return {
        "commits": [
            {
                "message": commit["message"],
                "author": commit["author_name"],
                "timestamp": commit["created_at"],
            }
            for commit in compare["commits"]
        ],
        "files_changed": [
            {
                "path": diff["new_path"],
                "status": (
                    "deleted"
                    if diff["deleted_file"]
                    else "new" if diff["new_file"] else "modified"
                ),
                "additions": diff.get("diff", "").count("\n+"),
                "deletions": diff.get("diff", "").count("\n-"),
                "diff": truncate_diff(diff.get("diff", "")),
            }
            for diff in compare["diffs"]
        ],
        "total_commits": len(compare["commits"]),
        "total_files": len(compare["diffs"]),
    }


@router_merge.post("", response_model=MergeRequestInfoResponse)
async def create_merge_request_with_ai(
    merge_request_input: MergeRequestInput, db: AsyncSession = Depends(get_db)
):
    provider = await providers.get_provider_by_id(db, merge_request_input.provider_id)

    if provider is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Provider with id: {merge_request_input.provider_id} not found",
        )

    model = await models.get_model(db, merge_request_input.model)

    if model is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            derail=f"Model {merge_request_input.model} not found",
        )

    if model.provider_id is not provider.id:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"The Model {merge_request_input.model} is not from the Provider{provider.name}",
        )

    template = await templates.get_template(db, merge_request_input.template_id)

    if template is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Template not found")

    gl = gitlab.Gitlab("https://gitlab.com", private_token=merge_request_input.pat)

    project = gl.projects.get(merge_request_input.project_id)

    compare = project.repository_compare(
        merge_request_input.target_branch, merge_request_input.origin_branch
    )

    mr_data = get_ai_mr_data(
        json.dumps(build_optimized_diffs(compare)),
        template.template,
        template.title,
        merge_request_input.context_ai,
        provider.type,
        model.name,
    )

    if mr_data is None:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calling ai api provider. Try again later",
        )

    title = extract_section(mr_data, "[title:start]", "[title:end]")
    description = extract_section(mr_data, "[description:start]", "[description:end]")

    return MergeRequestInfoResponse(
        title=title,
        description=description,
    )
