import argparse
import sys
import json

# Ensure UTF-8 output encoding across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from app.agent.core import AcademicCopilotAgent

def main():
    parser = argparse.ArgumentParser(description="Academic Copilot Agent CLI (LangChain)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: audit
    audit_parser = subparsers.add_parser("audit", help="Run full academic audit on a class session")
    audit_parser.add_argument("--course", default="Ciencia de Datos", help="Course keyword")
    audit_parser.add_argument("--recording-id", default=None, help="Target recording ID")

    # Command: chat
    chat_parser = subparsers.add_parser("chat", help="Interactive terminal chat with Academic Copilot")

    args = parser.parse_args()
    agent = AcademicCopilotAgent()

    if args.command == "audit":
        print(f"\n[*] Launching Academic Copilot Agent for: {args.course}...")
        result = agent.run_audit(course_keyword=args.course, recording_id=args.recording_id)
        
        print("\n" + "=" * 60)
        print("  AGENT REASONING TRACE (ReAct Loop)")
        print("=" * 60)
        for trace in result.execution_trace:
            print(f"\n[Step {trace.step_number}] Tool: {trace.tool_name}")
            print(f"Thought: {trace.thought}")
            print(f"Observation: {trace.tool_output}")

        print("\n" + "=" * 60)
        print("  FINAL AGENT AUDIT REPORT")
        print("=" * 60)
        print(result.final_response)

    elif args.command == "chat":
        print("\n=== Academic Copilot Agent Interactive Console ===")
        print("Type 'exit' or 'quit' to finish.\n")
        while True:
            try:
                user_input = input("You > ")
                if user_input.strip().lower() in ["exit", "quit"]:
                    break
                resp = agent.chat(user_input)
                print(f"\nAgent > {resp.get('reply')}\n")
            except (KeyboardInterrupt, EOFError):
                break
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
