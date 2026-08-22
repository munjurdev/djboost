"""djboost remove api-docs — remove Swagger/ReDoc from urls.py."""
import re
from pathlib import Path
from rich import print
from djboost.generator import check_virtual_environment


def remove_api_docs_command():
    """Remove API documentation (Swagger/ReDoc) from the project."""
    check_virtual_environment()
    
    print("\n[bold green]🔄 Removing API Documentation...[/bold green]\n")
    
    # Find urls.py
    urls_files = list(Path(".").glob("*/urls.py"))
    if not urls_files:
        print("[red]Error: urls.py not found.[/red]")
        return
    
    urls_path = urls_files[0]
    urls_content = urls_path.read_text(encoding="utf-8")
    
    removed = []
    
    # 1. Remove SpectacularAPIView import
    if "SpectacularAPIView" in urls_content:
        urls_content = re.sub(
            r"from drf_spectacular\.views import SpectacularAPIView.*?\n",
            "",
            urls_content
        )
        removed.append("SpectacularAPIView import")
        print("[green]✔ Removed SpectacularAPIView import[/green]")
    
    # 2. Remove schema URL
    if "SpectacularAPIView.as_view" in urls_content:
        urls_content = re.sub(
            r"\s*path\('api/schema/', SpectacularAPIView\.as_view\(url_name='schema'\), name='schema'\),?\n",
            "",
            urls_content
        )
        removed.append("schema URL")
        print("[green]✔ Removed /api/schema/ URL[/green]")
    
    # 3. Remove Swagger UI URL
    if "SpectacularSwaggerView" in urls_content:
        urls_content = re.sub(
            r"\s*path\('api/schema/swagger-ui/', SpectacularSwaggerView\.as_view\(url_name='schema'\), name='swagger-ui'\),?\n",
            "",
            urls_content
        )
        removed.append("Swagger UI URL")
        print("[green]✔ Removed /api/schema/swagger-ui/ URL[/green]")
    
    # 4. Remove ReDoc URL
    if "SpectacularRedocView" in urls_content:
        urls_content = re.sub(
            r"\s*path\('api/schema/redoc/', SpectacularRedocView\.as_view\(url_name='schema'\), name='redoc'\),?\n",
            "",
            urls_content
        )
        removed.append("ReDoc URL")
        print("[green]✔ Removed /api/schema/redoc/ URL[/green]")
    
    # Save urls.py
    with open(urls_path, "w", encoding="utf-8") as f:
        f.write(urls_content)
    
    # 5. Remove drf-spectacular from requirements.txt
    requirements_path = Path("requirements.txt")
    if requirements_path.exists():
        content = requirements_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        new_lines = [line for line in lines if "spectacular" not in line.lower()]
        if len(new_lines) < len(lines):
            requirements_path.write_text("\n".join(new_lines), encoding="utf-8")
            print("[green]✔ Removed drf-spectacular from requirements.txt[/green]")
    
    print()
    if removed:
        print(f"[bold green]✅ API Documentation removed![/bold green]")
        print(f"  Removed: {', '.join(removed)}")
    else:
        print("[yellow]⚠ No API documentation found to remove.[/yellow]")
    print()
