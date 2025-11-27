"""CLI wrapper for the email_collector package.

This file provides a small command-line entrypoint that delegates
the heavy lifting to the reorganized modules in the package.
"""

try:
    # normal package import (works when run as module)
    from .processor import process_cvs
except Exception:
    # fallback when the file is executed directly (python email_collector.py)
    # add package folder to sys.path and import the local module
    import sys
    import os
    import asyncio

    pkg_dir = os.path.dirname(__file__)
    # repo root is three levels up from this file: /<repo>/backend/email_collector/email_collector.py
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(pkg_dir)))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    # Try package import first (if repo root inserted)
    try:
        from backend.email_collector.processor import process_cvs
    except Exception:
        # Fallback to direct local import when executing inside the package folder
        from processor import process_cvs


async def _run_cli(target_job="statisticien"):
    print("=" * 60)
    print("🎯 EXTRACTEUR DE CV PAR POSTE")
    print("=" * 60)

    # while True:
    #     target_job = input("📝 Entrez le poste à filtrer (ex: Statisticien) : ").strip()
    #     if target_job:
    #         break
    #     print("❌ Le poste est obligatoire. Veuillez entrer un poste.\n")

    # max_emails_input = input("📧 Nombre maximum d'emails à analyser (défaut: 50) : ").strip()
    # max_emails = int(max_emails_input) if max_emails_input.isdigit() else 50

    print("\n🚀 Démarrage du traitement...\n")
    try:
        result = process_cvs(target_job_title=target_job, max_emails=100)
        await print(f" Terminé — {result['processed']} CV(s) traités. Fichier: {result['json_file']}")
    except KeyboardInterrupt:
        print("\n Interruption par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur : {e}")


if __name__ == "__main__":
    _run_cli("statisticien")