#!/usr/bin/env python3
"""
AI Boundary Engine - Interactive Demo
Showcases the engine's capabilities
"""

import sys
from typing import List, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from boundary_engine import BoundaryEngine, Decision

console = Console()


def print_header():
    """Print demo header."""
    console.print()
    console.print("╔═══════════════════════════════════════════════════════════╗", style="bold cyan")
    console.print("║     AI BOUNDARY ENGINE - INTERACTIVE DEMO                 ║", style="bold cyan")
    console.print("║     Refusal Intelligence for AI Systems                   ║", style="bold cyan")
    console.print("╚═══════════════════════════════════════════════════════════╝", style="bold cyan")
    console.print()


def demo_basic_safety():
    """Demonstrate basic safety checks."""
    console.print("\n[bold yellow]━━━ DEMO 1: Basic Safety Checks ━━━[/bold yellow]\n")
    
    engine = BoundaryEngine()
    
    test_cases = [
        ("What is machine learning?", "✅ Safe educational query"),
        ("How to make a bomb", "❌ Dangerous illegal activity"),
        ("Explain quantum physics", "✅ Safe technical query"),
        ("Ways to hurt someone", "❌ Violent content"),
        ("Best practices for Python", "✅ Safe programming query"),
    ]
    
    table = Table(title="Safety Analysis Results")
    table.add_column("Query", style="cyan", no_wrap=False, max_width=35)
    table.add_column("Expected", style="white", max_width=25)
    table.add_column("Decision", justify="center", style="bold")
    table.add_column("Confidence", justify="right")
    table.add_column("Status", justify="center")
    
    for query, expected in test_cases:
        result = engine.analyze(query)
        
        # Determine status
        decision_str = result.decision.value
        if result.decision == Decision.ANSWER:
            status = "✅"
            decision_color = "[green]ANSWER[/green]"
        elif result.decision == Decision.REFUSE:
            status = "❌"
            decision_color = "[red]REFUSE[/red]"
        else:
            status = "⚠️ "
            decision_color = "[yellow]CLARIFY[/yellow]"
        
        table.add_row(
            query[:32] + "..." if len(query) > 35 else query,
            expected,
            decision_color,
            f"{result.confidence:.2f}",
            status
        )
    
    console.print(table)
    console.print()


def demo_ambiguity_detection():
    """Demonstrate ambiguity detection."""
    console.print("\n[bold yellow]━━━ DEMO 2: Ambiguity Detection ━━━[/bold yellow]\n")
    
    engine = BoundaryEngine()
    
    queries = [
        "How to fix it",
        "Explain this",
        "What is the process of photosynthesis in plants?",
        "Help",
        "Describe machine learning algorithms in detail",
    ]
    
    console.print("[dim]Queries that are too vague will be flagged for clarification...[/dim]\n")
    
    for query in queries:
        result = engine.analyze(query)
        
        if result.decision == Decision.CLARIFY:
            panel_color = "yellow"
            symbol = "⚠️ "
        else:
            panel_color = "green"
            symbol = "✅"
        
        panel = Panel(
            f"[bold]Query:[/bold] {query}\n"
            f"[bold]Decision:[/bold] {result.decision}\n"
            f"[bold]Reasons:[/bold] {', '.join(result.reasons[:2])}",
            title=f"{symbol} Analysis",
            border_style=panel_color
        )
        console.print(panel)
        console.print()


def demo_intent_analysis():
    """Demonstrate semantic intent analysis."""
    console.print("\n[bold yellow]━━━ DEMO 3: Semantic Intent Analysis ━━━[/bold yellow]\n")
    
    engine = BoundaryEngine()
    
    console.print("[dim]Embeddings catch intent, not just keywords...[/dim]\n")
    
    queries = [
        "How to create an incendiary device",  # No direct "bomb" keyword
        "Steps for unauthorized system access",  # No "hack" keyword
        "Educational overview of cryptography",  # Safe crypto topic
    ]
    
    for query in queries:
        result = engine.analyze(query)
        
        console.print(f"[bold cyan]Query:[/bold cyan] {query}")
        console.print(f"[bold]Decision:[/bold] {result.decision} ({result.confidence:.2f})")
        
        if result.intent_scores:
            console.print(f"[bold]Top Intents:[/bold]")
            for score in result.intent_scores[:3]:
                console.print(f"  • {score.intent}: {score.similarity:.3f}")
        
        console.print(f"[bold]Reasoning:[/bold] {result.reasons[0]}")
        console.print()


def demo_custom_rules():
    """Demonstrate custom rules."""
    console.print("\n[bold yellow]━━━ DEMO 4: Custom Rules ━━━[/bold yellow]\n")
    
    from boundary_engine.types import Rule, RiskTag
    
    console.print("[dim]Adding a custom company policy rule...[/dim]\n")
    
    # Create custom rule
    custom_rule = Rule(
        name="company_confidential",
        keywords=["internal roadmap", "proprietary", "trade secret", "confidential data"],
        decision=Decision.REFUSE,
        severity=0.95,
        reason="Company confidential information requested",
        tags=[RiskTag.PERSONAL_DATA]
    )
    
    engine = BoundaryEngine(custom_rules=[custom_rule])
    
    queries = [
        "What is our internal roadmap?",
        "General industry trends in AI",
    ]
    
    for query in queries:
        result = engine.analyze(query)
        
        matched_custom = any(m.rule_name == "company_confidential" for m in result.rule_matches)
        
        console.print(f"[bold cyan]Query:[/bold cyan] {query}")
        console.print(f"[bold]Decision:[/bold] {result.decision}")
        console.print(f"[bold]Custom Rule Matched:[/bold] {'Yes ✓' if matched_custom else 'No'}")
        console.print()


def demo_batch_processing():
    """Demonstrate batch processing."""
    console.print("\n[bold yellow]━━━ DEMO 5: Batch Processing ━━━[/bold yellow]\n")
    
    engine = BoundaryEngine()
    
    queries = [
        "What is AI?",
        "How to hack systems?",
        "Explain photosynthesis",
        "How to make explosives",
        "Best Python libraries?",
        "Ways to cause harm",
        "What is blockchain?",
    ]
    
    console.print(f"[dim]Processing {len(queries)} queries in batch...[/dim]\n")
    
    results = engine.batch_analyze(queries)
    
    # Stats
    answer_count = sum(1 for r in results if r.decision == Decision.ANSWER)
    refuse_count = sum(1 for r in results if r.decision == Decision.REFUSE)
    clarify_count = sum(1 for r in results if r.decision == Decision.CLARIFY)
    
    stats_panel = Panel(
        f"[green]✅ ANSWER: {answer_count}[/green]\n"
        f"[red]❌ REFUSE: {refuse_count}[/red]\n"
        f"[yellow]⚠️  CLARIFY: {clarify_count}[/yellow]\n\n"
        f"[bold]Total Processed: {len(results)}[/bold]",
        title="Batch Results",
        border_style="cyan"
    )
    console.print(stats_panel)
    console.print()


def demo_llm_integration():
    """Demonstrate LLM integration pattern."""
    console.print("\n[bold yellow]━━━ DEMO 6: LLM Integration Pattern ━━━[/bold yellow]\n")
    
    engine = BoundaryEngine()
    
    def safe_llm_wrapper(user_query: str) -> str:
        """Simulate safe LLM integration."""
        # Check boundary first
        boundary = engine.analyze(user_query)
        
        if boundary.decision == Decision.REFUSE:
            return f"❌ Request blocked: {boundary.reasons[0]}"
        
        if boundary.decision == Decision.CLARIFY:
            return f"⚠️  Clarification needed: {boundary.reasons[0]}"
        
        # Safe to proceed - simulate LLM response
        return f"✅ [Simulated LLM response to: '{user_query}']"
    
    console.print("[dim]Simulating LLM calls with safety wrapper...[/dim]\n")
    
    test_queries = [
        "Explain quantum computing",
        "How to make a bomb",
        "Fix it",
    ]
    
    for query in test_queries:
        response = safe_llm_wrapper(query)
        
        console.print(f"[bold cyan]User:[/bold cyan] {query}")
        console.print(f"[bold white]System:[/bold white] {response}")
        console.print()


def interactive_mode():
    """Interactive query testing."""
    console.print("\n[bold yellow]━━━ INTERACTIVE MODE ━━━[/bold yellow]\n")
    console.print("[dim]Type queries to test. Type 'quit' to exit.[/dim]\n")
    
    engine = BoundaryEngine()
    
    while True:
        try:
            query = console.input("[bold cyan]Enter query:[/bold cyan] ")
            
            if query.lower() in ['quit', 'exit', 'q']:
                console.print("\n[dim]Exiting...[/dim]")
                break
            
            if not query.strip():
                continue
            
            result = engine.analyze(query)
            
            # Display result
            decision_color = {
                Decision.ANSWER: "green",
                Decision.REFUSE: "red",
                Decision.CLARIFY: "yellow"
            }.get(result.decision, "white")
            
            console.print()
            console.print(f"[bold]Decision:[/bold] [{decision_color}]{result.decision}[/{decision_color}]")
            console.print(f"[bold]Confidence:[/bold] {result.confidence:.2f}")
            console.print(f"[bold]Reasons:[/bold]")
            for reason in result.reasons:
                console.print(f"  • {reason}")
            
            if result.risk_tags:
                console.print(f"[bold]Risk Tags:[/bold] {', '.join(str(t) for t in result.risk_tags)}")
            
            console.print()
        
        except KeyboardInterrupt:
            console.print("\n\n[dim]Interrupted. Exiting...[/dim]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]\n")


def main():
    """Run all demos."""
    print_header()
    
    try:
        # Auto demos
        demo_basic_safety()
        input("\n[Press Enter to continue...]")
        
        demo_ambiguity_detection()
        input("\n[Press Enter to continue...]")
        
        demo_intent_analysis()
        input("\n[Press Enter to continue...]")
        
        demo_custom_rules()
        input("\n[Press Enter to continue...]")
        
        demo_batch_processing()
        input("\n[Press Enter to continue...]")
        
        demo_llm_integration()
        input("\n[Press Enter to continue...]")
        
        # Interactive mode
        interactive_mode()
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted.[/yellow]")
        sys.exit(0)
    
    console.print("\n[bold green]✨ Demo completed! ✨[/bold green]\n")


if __name__ == "__main__":
    main()
