"""
Connect nodes and edges together to builds and compile the Langgraph

StateGraph : A graph whose nodes communicate by reading and writing to a shared state.
"""
from langgraph.graph import StateGraph, END
from nodes import (
    parse_jd_node,
    score_resume_node,
    route_decision_node,
    rank_node,
    generate_questions_node,
    report_node,
    should_continue,
)
from state import create_initial_state
from state import ResumeState

def build_graph() :
    """Steps:
    1. Create StateGraph with ResumeState
    2. Add all nodes
    3. Set entry point
    4. Add edges between nodes
    5. Add conditional edge for loop
    6. Compile and return
"""
    # step 1 : create graph with state
    graph = StateGraph(ResumeState)

    # step 2 : Add all nodes
    graph.add_node("parse_jd", parse_jd_node)
    graph.add_node("score_resume", score_resume_node)
    graph.add_node("route_decision", route_decision_node)
    graph.add_node("rank", rank_node)
    graph.add_node("generate_questions", generate_questions_node)
    graph.add_node("report", report_node)

    # step 3 : set entry point
    graph.set_entry_point("parse_jd")

    # ste 4 - Add normal edges
    # parse_jd always goest score resume
    graph.add_edge("parse_jd", "score_resume")

    # score_resume always goes to route_decision
    graph.add_edge("score_resume", "route_decision")

    # rank always goes to generate_questions
    graph.add_edge("rank", "generate_questions")

    # generate_questions always goes to report
    graph.add_edge("generate_questions", "report")

    # report always goes to END
    graph.add_edge("report", END)


    # step 5 : Add conditional edge (the loop)
   # After route_decision check if more resumes exist
    # If yes  → go back to score_resume
    # If no   → go to rank
    graph.add_conditional_edges(
        "route_decision", # from this node
        should_continue,
        {
            "score_resume" : "score_resume", # loop back
            "rank" : "rank" # move forward
        }
    )

    # step 6 : Compile
    app = graph.compile()
    return  app

def run_screener(job_description : str, resumes : list) -> dict :
    print("Resume screener using Langgraph")

    print(f"Resumes to screen : {len(resumes)}")

    # Create initial state
    initial_state = create_initial_state(
        job_description = job_description,
        resumes= resumes,
    )

    # Build and run graph
    app = build_graph()
    result = app.invoke(initial_state)

    print("Screening complete!")
    print(f"  Shortlisted: {len(result.get('shortlisted', []))}")
    print(f"  Rejected:    {len(result.get('rejected', []))}")

    return  result

if __name__ == "__main__":
    from sample_data import SAMPLE_JD, SAMPLE_RESUMES

    result = run_screener(SAMPLE_JD, SAMPLE_RESUMES)

    print("\n\nFINAL RESULTS")
    print("=" * 55)

    print("\nSHORTLISTED CANDIDATES:")
    for c in result.get("ranked_candidates", []):
        print(f"  {c['name']:<20} Score: {c['score']}/100")
        print(f"    Matched: {', '.join(c['matched_skills'][:3])}")
        print(f"    Summary: {c['summary']}")

    print("\nREJECTED CANDIDATES:")
    for c in result.get("rejected", []):
        print(f"  {c['name']:<20} Score: {c['score']}/100")
        print(f"    Missing: {', '.join(c['missing_skills'][:3])}")

    print("\nINTERVIEW QUESTIONS — Top Candidates:")
    for iq in result.get("interview_questions", []):
        print(f"\n  {iq['candidate_name']}:")
        for i, q in enumerate(iq["questions"], 1):
            print(f"    {i}. {q}")

    print("\nFINAL REPORT:")
    print(result.get("final_report", "No report generated"))
