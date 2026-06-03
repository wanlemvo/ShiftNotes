from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage

from shiftnotes_agent.state import ShiftNotesState
from shiftnotes_agent.logger import get_logger, log_node_entry, log_node_exit, log_error

load_dotenv()
logger = get_logger("retrieve_and_generate")

# Initialize OpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
embeddings = OpenAIEmbeddings()

# ChromaDB collection name
CHROMA_COLLECTION = "shiftnotes_reports"


def retrieve_and_generate(state: ShiftNotesState) -> ShiftNotesState:
    run_id = state.get("run_id", "unknown")
    log_node_entry(logger, "retrieve_and_generate", run_id)

    try:
        if state.get("error"):
            return state

        detected_signals = state.get("detected_signals", [])

        if not detected_signals:
            log_node_exit(logger, "retrieve_and_generate", run_id, "no signals — skipping RAG")
            return {
                **state,
                "retrieved_context": "",
                "generated_briefing": "No operational signals detected this period."
            }

        # --- Step 1: Retrieve historical context from ChromaDB ---
        retrieved_context = _retrieve_context(detected_signals)

        # --- Step 2: Generate briefing with OpenAI ---
        generated_briefing = _generate_briefing(detected_signals, retrieved_context)

        log_node_exit(logger, "retrieve_and_generate", run_id, "briefing generated")

        return {
            **state,
            "retrieved_context": retrieved_context,
            "generated_briefing": generated_briefing
        }

    except Exception as e:
        log_error(logger, "retrieve_and_generate", run_id, str(e))
        return {
            **state,
            "error": f"retrieve_and_generate failed: {str(e)}"
        }


def _retrieve_context(detected_signals: list[dict]) -> str:
    """
    Searches ChromaDB for historical reports similar to
    the signals we just detected.
    """
    try:
        vectorstore = Chroma(
            collection_name=CHROMA_COLLECTION,
            embedding_function=embeddings,
            persist_directory="./chroma_db"
        )

        # Build a query from the detected signals
        signal_names = []
        for report in detected_signals:
            for signal in report.get("signals_found", []):
                signal_names.append(signal["name"])

        query = f"operational issues: {', '.join(set(signal_names))}"
        docs = vectorstore.similarity_search(query, k=3)

        if docs:
            return "\n".join(d.page_content for d in docs)
        else:
            return "No historical context available yet."

    except Exception:
        # ChromaDB might be empty on first run — that's fine
        return "No historical context available yet."


def _generate_briefing(detected_signals: list[dict], context: str) -> str:
    """
    Uses OpenAI to generate a plain-English operational briefing
    from the detected signals and historical context.
    """
    # Summarize signals for the prompt
    signal_summary = _summarize_signals(detected_signals)

    system_prompt = """You are an operational intelligence assistant for a hospitality company.
Your job is to write clear, concise weekly briefings for Ted, the General Manager.
Write in plain English. Be direct. Focus on what requires attention.
Format: short paragraphs, no bullet points, under 200 words."""

    user_prompt = f"""Write a weekly operational briefing based on these detected signals:

{signal_summary}

Historical context from past reports:
{context}

Write the briefing now."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = llm.invoke(messages)
    return response.content


def _summarize_signals(detected_signals: list[dict]) -> str:
    """Converts detected signals list into readable summary for the prompt."""
    from collections import Counter

    all_signals = []
    kiosks_affected = []

    for report in detected_signals:
        kiosks_affected.append(report.get("kiosk", "Unknown"))
        for signal in report.get("signals_found", []):
            all_signals.append(signal["name"])

    counts = Counter(all_signals)
    kiosk_counts = Counter(kiosks_affected)

    lines = []
    for signal, count in counts.most_common():
        lines.append(f"- {signal.replace('_', ' ').title()}: {count} reports")

    lines.append("\nKiosks with signals:")
    for kiosk, count in kiosk_counts.most_common():
        lines.append(f"- {kiosk}: {count} reports flagged")

    return "\n".join(lines)