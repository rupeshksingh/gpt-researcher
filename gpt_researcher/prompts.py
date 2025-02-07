import warnings
from datetime import date, datetime, timezone

from .utils.enum import ReportSource, ReportType, Tone
from typing import List, Dict, Any


def generate_search_queries_prompt(
    question: str,
    parent_query: str,
    report_type: str,
    max_iterations: int = 3,
    context: List[Dict[str, Any]] = [],
):
    """Generates the search queries prompt for the given question."""

    if (
        report_type == ReportType.DetailedReport.value
        or report_type == ReportType.SubtopicReport.value
    ):
        task = f"{parent_query} - {question}"
    else:
        task = question

    context_prompt = f"""
You are a specialized tender research assistant tasked with generating search queries to find relevant tender information for: "{task}".
Context: {context}

Use this context to inform and refine your search queries. The context provides real-time tender information that can help you generate more specific and relevant queries. Consider any current tender notices, deadlines, amendments, or specific requirements mentioned in the context that could enhance the search queries.
""" if context else ""

    dynamic_example = ", ".join([f'"query {i+1}"' for i in range(max_iterations)])

    return f"""Write {max_iterations} search queries to find tender opportunities and related information for the following task: "{task}"

Focus on finding:
- Active tender notices
- Pre-qualification requirements
- Technical specifications
- Submission deadlines
- Similar past tenders
- Tender amendments or corrigenda

Assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.

{context_prompt}
You must respond with a list of strings in the following format: [{dynamic_example}].
The response should contain ONLY the list.
"""

def generate_report_prompt(
    question: str,
    context,
    report_source: str,
    report_format="apa",
    total_words=1000,
    tone=None,
    language="english",
):
    """Generates the tender report prompt for the given question and research summary."""

    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = f"""
You MUST write all tender portal URLs and source documents at the end of the report as references. Make sure to not add duplicated sources.
Every url should be hyperlinked: [tender portal/document name](url)
Additionally, you MUST include hyperlinks to the relevant URLs wherever they are referenced in the report.

eg: Tender Authority. (Year, Month Date). Tender Title. Portal Name. [tender portal name](url)
"""
    else:
        reference_prompt = f"""
You MUST write all used tender document names at the end of the report as references, and make sure to not add duplicated sources.
"""

    tone_prompt = f"Write the report in a {tone.value} tone." if tone else ""

    return f"""
Information: "{context}"
---
Using the above information, analyze the following tender opportunity or task: "{question}" in a detailed report --
The report should focus on key tender requirements, eligibility criteria, submission process, 
important dates, and technical specifications. Include all relevant numbers, amounts, and deadlines.
The report should be well structured, comprehensive, and at least {total_words} words long.
You should strive to include all critical tender information using the provided sources.

Please follow all of the following guidelines in your report:
- You MUST analyze eligibility criteria, technical requirements, and financial requirements separately
- You MUST write the report with markdown syntax and {report_format} format
- You MUST prioritize official tender documents and notices over secondary sources
- You MUST highlight any critical deadlines, pre-bid meetings, or submission requirements
- You MUST include any past performance requirements or similar experience criteria
- Use in-text citation references in {report_format} format with markdown hyperlinks at the end of relevant sentences
- Include a complete reference list of tender documents and sources at the end
- {reference_prompt}
- {tone_prompt}

You MUST write the report in the following language: {language}.
Please be thorough and accurate, as this is critical for tender participation.
Assume that the current date is {date.today()}.
"""

def curate_sources(query, sources, max_results=10):
    return f"""Your goal is to evaluate and curate the provided content for the tender research task: "{query}" 
    while prioritizing official tender documents, notices, and amendments.

The final curated list will be used for tender analysis, so prioritize:
- Official tender notices and documents
- Technical specifications and requirements
- Financial criteria and bid requirements
- Pre-qualification criteria
- Similar past tender information
- Any amendments or corrigenda

EVALUATION GUIDELINES:
1. Assess each source based on:
   - Authority: Prioritize official tender portals and issuing authorities
   - Relevance: Include directly related tender documents and supporting information
   - Currency: Focus on current tender notices and latest amendments
   - Completeness: Favor sources with detailed technical and financial requirements
   - Supporting Data: Include sources with past tender data or market information
2. Source Selection:
   - Include up to {max_results} most relevant sources
   - Prioritize primary tender documents over secondary analyses
   - Include both technical and financial requirement sources
   - Retain any relevant past tender information for comparison
3. Content Retention:
   - Keep all official tender specifications and requirements intact
   - Retain complete eligibility criteria and submission requirements
   - Preserve any numerical data, deadlines, or critical dates
   - Maintain accuracy of technical specifications

SOURCES LIST TO EVALUATE:
{sources}

You MUST return your response in the EXACT sources JSON list format as the original sources.
The response MUST not contain any markdown format or additional text (like ```json), just the JSON list!
"""

def generate_resource_report_prompt(
    question, context, report_source: str, report_format="apa", tone=None, total_words=1000, language=None
):
    """Generates the tender resource report prompt."""

    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = f"""
            You MUST include all relevant tender portal URLs and document sources.
            Every url should be hyperlinked: [tender portal/document name](url)
            """
    else:
        reference_prompt = f"""
            You MUST write all used tender document names as references, without duplicates.
        """

    return (
        f'"""{context}"""\n\nBased on the above information, generate a resource recommendation report for the tender'
        f' topic: "{question}". The report should analyze each recommended resource,'
        " explaining how it contributes to understanding the tender requirements and submission process.\n"
        "Focus on official tender documents, technical specifications, and submission requirements.\n"
        "Ensure that the report is well-structured, detailed, and follows Markdown syntax.\n"
        "Include all relevant dates, amounts, and technical specifications.\n"
        f"The report should have a minimum length of {total_words} words.\n"
        f"{reference_prompt}"
    )

def generate_custom_report_prompt(
    query_prompt, context, report_source: str, report_format="apa", tone=None, total_words=1000, language: str = "english"
):
    return f'"{context}"\n\n{query_prompt}'


def generate_outline_report_prompt(
    question, context, report_source: str, report_format="apa", tone=None,  total_words=1000, language: str = "english"
):
    """Generates the outline report prompt for the given question and research summary.
    Args: question (str): The question to generate the outline report prompt for
            research_summary (str): The research summary to generate the outline report prompt for
    Returns: str: The outline report prompt for the given question and research summary
    """

    return (
        f'"""{context}""" Using the above information, generate an outline for a research report in Markdown syntax'
        f' for the following question or topic: "{question}". The outline should provide a well-structured framework'
        " for the research report, including the main sections, subsections, and key points to be covered."
        f" The research report should be detailed, informative, in-depth, and a minimum of {total_words} words."
        " Use appropriate Markdown syntax to format the outline and ensure readability."
    )


def get_report_by_type(report_type: str):
    report_type_mapping = {
        ReportType.ResearchReport.value: generate_report_prompt,
        ReportType.ResourceReport.value: generate_resource_report_prompt,
        ReportType.OutlineReport.value: generate_outline_report_prompt,
        ReportType.CustomReport.value: generate_custom_report_prompt,
        ReportType.SubtopicReport.value: generate_subtopic_report_prompt,
    }
    return report_type_mapping[report_type]


def auto_agent_instructions():
    return """
This task involves researching tender opportunities and requirements, focusing on specific types of tenders and their requirements. The research is conducted by specialized tender agents with distinct expertise areas.

Agent
The agent is determined by the type of tender and specific expertise needed. Agents are categorized by their specialization, with corresponding emojis.

examples:
task: "analyze construction tender requirements for metro project"
response: 
{
    "server": "🏗️ Construction Tender Agent",
    "agent_role_prompt": "You are an experienced construction tender analyst AI assistant. Your primary goal is to analyze technical specifications, BOQs, and compliance requirements for construction tenders."
}

task: "evaluate IT system procurement tender"
response: 
{ 
    "server": "💻 IT Procurement Agent",
    "agent_role_prompt": "You are a specialized IT procurement analyst AI assistant. Your main objective is to analyze technical requirements, compatibility specifications, and service level agreements in IT tenders."
}

task: "review medical equipment tender specifications"
response:
{
    "server": "🏥 Healthcare Procurement Agent",
    "agent_role_prompt": "You are an expert medical procurement AI assistant. Your main purpose is to analyze medical equipment specifications, compliance requirements, and regulatory standards in healthcare tenders."
}
"""

def generate_summary_prompt(query, data):
    """Generates the summary prompt for the given question and text.
    Args: question (str): The question to generate the summary prompt for
            text (str): The text to generate the summary prompt for
    Returns: str: The summary prompt for the given question and text
    """

    return (
        f'{data}\n Using the above text, summarize it based on the following task or query: "{query}".\n If the '
        f"query cannot be answered using the text, YOU MUST summarize the text in short.\n Include all factual "
        f"information such as numbers, stats, quotes, etc if available. "
    )


################################################################################################

# DETAILED REPORT PROMPTS

def generate_subtopics_prompt() -> str:
    return """
Provided the main tender topic:

{task}

and research data:

{data}

- Construct a list of subtopics that will form the sections of a comprehensive tender analysis report
- These are possible subtopics: {subtopics}
- There should NOT be any duplicate subtopics
- Limit the number of subtopics to a maximum of {max_subtopics}
- Order the subtopics logically for a tender analysis report

"IMPORTANT!":
- Every subtopic MUST be relevant to the tender requirements and provided research data ONLY!
- Focus on critical aspects like eligibility, technical requirements, financial criteria, and submission process

{format_instructions}
"""

[Rest of the functions remain structurally same with tender-focused content modifications]

def generate_subtopic_report_prompt(
    current_subtopic,
    existing_headers: list,
    relevant_written_contents: list,
    main_topic: str,
    context,
    report_format: str = "apa",
    max_subsections=5,
    total_words=800,
    tone: Tone = Tone.Objective,
    language: str = "english",
) -> str:
    return f"""
Context:
"{context}"

Main Topic and Subtopic:
Using the latest information available, construct a detailed report on the subtopic: {current_subtopic} under the main topic: {main_topic}.
You must limit the number of subsections to a maximum of {max_subsections}.

Content Focus:
- The report should focus on answering the question, be well-structured, informative, in-depth, and include facts and numbers if available.
- Use markdown syntax and follow the {report_format.upper()} format.

IMPORTANT:Content and Sections Uniqueness:
- This part of the instructions is crucial to ensure the content is unique and does not overlap with existing reports.
- Carefully review the existing headers and existing written contents provided below before writing any new subsections.
- Prevent any content that is already covered in the existing written contents.
- Do not use any of the existing headers as the new subsection headers.
- Do not repeat any information already covered in the existing written contents or closely related variations to avoid duplicates.
- If you have nested subsections, ensure they are unique and not covered in the existing written contents.
- Ensure that your content is entirely new and does not overlap with any information already covered in the previous subtopic reports.

"Existing Subtopic Reports":
- Existing subtopic reports and their section headers:

    {existing_headers}

- Existing written contents from previous subtopic reports:

    {relevant_written_contents}

"Structure and Formatting":
- As this sub-report will be part of a larger report, include only the main body divided into suitable subtopics without any introduction or conclusion section.

- You MUST include markdown hyperlinks to relevant source URLs wherever referenced in the report, for example:

    ### Section Header
    
    This is a sample text. ([url website](url))

- Use H2 for the main subtopic header (##) and H3 for subsections (###).
- Use smaller Markdown headers (e.g., H2 or H3) for content structure, avoiding the largest header (H1) as it will be used for the larger report's heading.
- Organize your content into distinct sections that complement but do not overlap with existing reports.
- When adding similar or identical subsections to your report, you should clearly indicate the differences between and the new content and the existing written content from previous subtopic reports. For example:

    ### New header (similar to existing header)

    While the previous section discussed [topic A], this section will explore [topic B]."

"Date":
Assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.

"IMPORTANT!":
- You MUST write the report in the following language: {language}.
- The focus MUST be on the main topic! You MUST Leave out any information un-related to it!
- Must NOT have any introduction, conclusion, summary or reference section.
- You MUST include hyperlinks with markdown syntax ([url website](url)) related to the sentences wherever necessary.
- You MUST mention the difference between the existing content and the new content in the report if you are adding the similar or same subsections wherever necessary.
- The report should have a minimum length of {total_words} words.
- Use an {tone.value} tone throughout the report.

Do NOT add a conclusion section.
"""


def generate_draft_titles_prompt(
    current_subtopic: str,
    main_topic: str,
    context: str,
    max_subsections: int = 5
) -> str:
    return f"""
"Context":
"{context}"

"Main Topic and Subtopic":
Using the latest information available, construct a draft section title headers for a detailed report on the subtopic: {current_subtopic} under the main topic: {main_topic}.

"Task":
1. Create a list of draft section title headers for the subtopic report.
2. Each header should be concise and relevant to the subtopic.
3. The header should't be too high level, but detailed enough to cover the main aspects of the subtopic.
4. Use markdown syntax for the headers, using H3 (###) as H1 and H2 will be used for the larger report's heading.
5. Ensure the headers cover main aspects of the subtopic.

"Structure and Formatting":
Provide the draft headers in a list format using markdown syntax, for example:

### Header 1
### Header 2
### Header 3

"IMPORTANT!":
- The focus MUST be on the main topic! You MUST Leave out any information un-related to it!
- Must NOT have any introduction, conclusion, summary or reference section.
- Focus solely on creating headers, not content.
"""


def generate_report_introduction(question: str, research_summary: str = "", language: str = "english") -> str:
    return f"""{research_summary}\n 
Using the above latest information, Prepare a detailed report introduction on the topic -- {question}.
- The introduction should be succinct, well-structured, informative with markdown syntax.
- As this introduction will be part of a larger report, do NOT include any other sections, which are generally present in a report.
- The introduction should be preceded by an H1 heading with a suitable topic for the entire report.
- You must include hyperlinks with markdown syntax ([url website](url)) related to the sentences wherever necessary.
Assume that the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.
- The output must be in {language} language.
"""


def generate_report_conclusion(query: str, report_content: str, language: str = "english") -> str:
    """
    Generate a concise conclusion summarizing the main findings and implications of a research report.

    Args:
        query (str): The research task or question.
        report_content (str): The content of the research report.
        language (str): The language in which the conclusion should be written.

    Returns:
        str: A concise conclusion summarizing the report's main findings and implications.
    """
    prompt = f"""
    Based on the research report below and research task, please write a concise conclusion that summarizes the main findings and their implications:
    
    Research task: {query}
    
    Research Report: {report_content}

    Your conclusion should:
    1. Recap the main points of the research
    2. Highlight the most important findings
    3. Discuss any implications or next steps
    4. Be approximately 2-3 paragraphs long
    
    If there is no "## Conclusion" section title written at the end of the report, please add it to the top of your conclusion. 
    You must include hyperlinks with markdown syntax ([url website](url)) related to the sentences wherever necessary.

    IMPORTANT: The entire conclusion MUST be written in {language} language.

    Write the conclusion:
    """

    return prompt


report_type_mapping = {
    ReportType.ResearchReport.value: generate_report_prompt,
    ReportType.ResourceReport.value: generate_resource_report_prompt,
    ReportType.OutlineReport.value: generate_outline_report_prompt,
    ReportType.CustomReport.value: generate_custom_report_prompt,
    ReportType.SubtopicReport.value: generate_subtopic_report_prompt,
}


def get_prompt_by_report_type(report_type):
    prompt_by_type = report_type_mapping.get(report_type)
    default_report_type = ReportType.ResearchReport.value
    if not prompt_by_type:
        warnings.warn(
            f"Invalid report type: {report_type}.\n"
            f"Please use one of the following: {', '.join([enum_value for enum_value in report_type_mapping.keys()])}\n"
            f"Using default report type: {default_report_type} prompt.",
            UserWarning,
        )
        prompt_by_type = report_type_mapping.get(default_report_type)
    return prompt_by_type

