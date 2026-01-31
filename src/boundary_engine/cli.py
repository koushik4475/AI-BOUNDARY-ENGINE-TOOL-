"""
CLI interface for AI Boundary Engine.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from boundary_engine import BoundaryEngine, Decision

app = typer.Typer(
    name="boundary",
    help="AI Boundary Engine - Analyze queries for safety and clarity",
    add_completion=False
)
console = Console()


@app.command()
def check(
    query: Optional[str] = typer.Argument(None, help="Query to analyze"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="File with queries (one per line)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed analysis"),
):
    """
    Analyze a query or batch of queries.
    
    Examples:
        boundary check "How to make a bomb"
        boundary check --file queries.txt
        boundary check "What is AI?" --json
    """
    engine = BoundaryEngine()
    
    if file:
        # Batch mode
        if not file.exists():
            console.print(f"[red]Error: File '{file}' not found[/red]")
            raise typer.Exit(1)
        
        queries = file.read_text().strip().split('\n')
        results = engine.batch_analyze(queries)
        
        if json_output:
            output = [r.model_dump(exclude_none=True) for r in results]
            console.print_json(json.dumps(output, indent=2))
        else:
            _display_batch_results(results)
    
    elif query:
        # Single query mode
        result = engine.analyze(query)
        
        if json_output:
            console.print_json(result.model_dump_json(indent=2, exclude_none=True))
        else:
            _display_result(result, verbose)
    
    else:
        console.print("[yellow]Please provide a query or use --file option[/yellow]")
        console.print("Run 'boundary check --help' for usage information")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from boundary_engine import __version__
    console.print(f"AI Boundary Engine v{__version__}")


@app.command()
def info():
    """Show engine information and statistics."""
    engine = BoundaryEngine()
    
    table = Table(title="AI Boundary Engine Info")
    table.add_column("Component", style="cyan")
    table.add_column("Details", style="white")
    
    table.add_row("Rules Loaded", str(len(engine.rule_engine.rules)))
    table.add_row("Intent Categories", str(len(engine.embedding_analyzer.intents)))
    table.add_row("Embedding Model", engine.config.embedding_model)
    table.add_row("Refuse Threshold", f"{engine.config.refuse_threshold:.2f}")
    table.add_row("Clarify Threshold", f"{engine.config.clarify_threshold:.2f}")
    
    console.print(table)


def _display_result(result, verbose: bool = False):
    """Display single result in human-readable format."""
    # Decision with color
    decision_colors = {
        Decision.ANSWER: "green",
        Decision.REFUSE: "red",
        Decision.CLARIFY: "yellow"
    }
    
    color = decision_colors.get(result.decision, "white")
    
    rprint(f"\n[bold]Decision:[/bold] [{color}]{result.decision}[/{color}]")
    rprint(f"[bold]Confidence:[/bold] {result.confidence:.2f}")
    
    # Reasons
    rprint(f"\n[bold]Reasons:[/bold]")
    for reason in result.reasons:
        rprint(f"  • {reason}")
    
    # Risk tags
    if result.risk_tags:
        tags_str = ", ".join(tag for tag in result.risk_tags)
        rprint(f"\n[bold]Risk Tags:[/bold] {tags_str}")
    
    # Verbose output
    if verbose:
        if result.rule_matches:
            rprint(f"\n[bold]Matched Rules:[/bold]")
            for match in result.rule_matches:
                rprint(f"  • {match.rule_name} (confidence: {match.confidence:.2f})")
        
        if result.intent_scores:
            rprint(f"\n[bold]Top Intents:[/bold]")
            for score in result.intent_scores[:3]:
                rprint(f"  • {score.intent}: {score.similarity:.2f}")
        
        if result.ambiguity:
            rprint(f"\n[bold]Ambiguity:[/bold]")
            rprint(f"  Score: {result.ambiguity.score:.2f}")
            if result.ambiguity.reasons:
                for reason in result.ambiguity.reasons:
                    rprint(f"  • {reason}")
    
    rprint()


def _display_batch_results(results):
    """Display batch results in table format."""
    table = Table(title="Batch Analysis Results")
    table.add_column("Query", style="cyan", no_wrap=False, max_width=40)
    table.add_column("Decision", style="white")
    table.add_column("Confidence", justify="right", style="white")
    table.add_column("Top Reason", style="white", no_wrap=False)
    
    for result in results:
        # Truncate query
        query_display = result.query[:37] + "..." if len(result.query) > 40 else result.query
        
        # Color decision
        decision_colors = {
            Decision.ANSWER: "[green]ANSWER[/green]",
            Decision.REFUSE: "[red]REFUSE[/red]",
            Decision.CLARIFY: "[yellow]CLARIFY[/yellow]"
        }
        decision_display = decision_colors.get(result.decision, result.decision)
        
        # Top reason
        top_reason = result.reasons[0] if result.reasons else "N/A"
        if len(top_reason) > 40:
            top_reason = top_reason[:37] + "..."
        
        table.add_row(
            query_display,
            decision_display,
            f"{result.confidence:.2f}",
            top_reason
        )
    
    console.print(table)


if __name__ == "__main__":
    app()
