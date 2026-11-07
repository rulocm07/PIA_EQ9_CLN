"""Exporta contrato desde el código real. Ejecución: python scripts/export_openapi.py"""
from pathlib import Path
import yaml
from src.api.main import app

out=Path('docs/api/openapi.yaml')
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(yaml.safe_dump(app.openapi(),allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
print('Exportado',out)
