"""
User interaction prompts and setup wizard
"""

import getpass
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

from core.config import Config

console = Console()

def setup_wizard(config: Config):
    """Run the initial setup wizard"""
    
    console.print(Panel.fit(
        "[bold blue]🚀 Local AI Assistant Setup[/bold blue]\n"
        "Let's configure your secure AI assistant",
        border_style="blue"
    ))
    
    # Create admin user
    _setup_admin_user(config)
    
    # Configure paths
    _setup_paths(config)
    
    # Configure applications
    _setup_applications(config)
    
    # Finalize setup
    config.mark_configured()
    
    console.print(Panel.fit(
        "[bold green]✅ Setup Complete![/bold green]\n"
        "Your Local AI Assistant is ready to use.",
        border_style="green"
    ))

def _setup_admin_user(config: Config):
    """Setup the initial admin user"""
    console.print("\n[bold]👤 Admin User Setup[/bold]")
    
    username = Prompt.ask("Admin username", default="admin")
    
    while True:
        password = getpass.getpass("Admin password (min 8 chars): ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            console.print("[red]Passwords don't match. Please try again.[/red]")
            continue
        
        if len(password) < 8:
            console.print("[red]Password must be at least 8 characters. Please try again.[/red]")
            continue
        
        break
    
    # Hash and store password
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    config.add_user(username, password_hash, "admin")
    
    console.print(f"[green]✓ Admin user '{username}' created[/green]")

def _setup_paths(config: Config):
    """Setup allowlisted paths"""
    console.print("\n[bold]📁 Path Configuration[/bold]")
    
    current_paths = config.allowlisted_paths
    
    # Show current paths
    table = Table(title="Current Allowlisted Paths")
    table.add_column("Path", style="cyan")
    table.add_column("Exists", style="green")
    
    for path in current_paths:
        exists = "✓" if Path(path).exists() else "✗"
        table.add_row(path, exists)
    
    console.print(table)
    
    # Ask if user wants to modify
    if Confirm.ask("\nModify allowlisted paths?", default=False):
        console.print("\n[dim]Enter additional paths (one per line, empty line to finish):[/dim]")
        
        new_paths = current_paths.copy()
        while True:
            path = Prompt.ask("Path (or press Enter to finish)", default="")
            if not path:
                break
            
            path = str(Path(path).expanduser().resolve())
            if path not in new_paths:
                new_paths.append(path)
                console.print(f"[green]✓ Added: {path}[/green]")
            else:
                console.print(f"[yellow]Already exists: {path}[/yellow]")
        
        config.data["allowlisted_paths"] = new_paths
        config.save()

def _setup_applications(config: Config):
    """Setup whitelisted applications"""
    console.print("\n[bold]🚀 Application Configuration[/bold]")
    
    current_apps = config.whitelisted_apps
    
    # Show current apps
    table = Table(title="Current Whitelisted Applications")
    table.add_column("Application", style="cyan")
    
    for app in current_apps:
        table.add_row(app)
    
    console.print(table)
    
    # Ask if user wants to modify
    if Confirm.ask("\nModify whitelisted applications?", default=False):
        console.print("\n[dim]Enter additional applications (one per line, empty line to finish):[/dim]")
        
        new_apps = current_apps.copy()
        while True:
            app = Prompt.ask("Application name (or press Enter to finish)", default="")
            if not app:
                break
            
            if app not in new_apps:
                new_apps.append(app)
                console.print(f"[green]✓ Added: {app}[/green]")
            else:
                console.print(f"[yellow]Already exists: {app}[/yellow]")
        
        config.data["whitelisted_apps"] = new_apps
        config.save()

def get_user_confirmation(message: str, sensitivity: str = "medium") -> bool:
    """Get user confirmation with appropriate prompting"""
    
    if sensitivity == "high":
        console.print(f"\n[red bold]HIGH SENSITIVITY OPERATION[/red bold]")
        console.print(f"[yellow]{message}[/yellow]")
        console.print("\n[red]Type 'I AUTHORIZE' to proceed (case sensitive):[/red]")
        
        response = Prompt.ask("Authorization")
        return response == "I AUTHORIZE"
    
    elif sensitivity == "medium":
        return Confirm.ask(f"\n{message}", default=False)
    
    return True