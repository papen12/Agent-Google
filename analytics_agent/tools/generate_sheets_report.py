import gspread
from google.oauth2.service_account import Credentials
from google.adk.tools import FunctionTool
import pandas as pd
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def _get_sheets_client():
    creds = Credentials.from_service_account_file(
        "credentials.json", 
        scopes=SCOPES
    )
    return gspread.authorize(creds)

def generate_sheets_report(
    report_title: str,
    data: list[dict],
    share_with_email: str = None
) -> dict:
    """
    Genera un reporte en Google Sheets con los datos de ventas proporcionados.
    
    Args:
        report_title: Título del reporte (ej: "Reporte Q4 2025 - Ventas")
        data: Lista de diccionarios con los datos del reporte
        share_with_email: Email opcional para compartir el sheet automáticamente
    
    Returns:
        dict con la URL del sheet y el ID del documento
    """
    try:
        client = _get_sheets_client()
        
        # Crear nuevo spreadsheet
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        sheet_name = f"{report_title} | {timestamp}"
        spreadsheet = client.create(sheet_name)
        
        worksheet = spreadsheet.sheet1
        worksheet.update_title("Datos de Ventas")
        
        if not data:
            return {"error": "No hay datos para generar el reporte"}
        
        # Encabezados desde las keys del primer dict
        headers = list(data[0].keys())
        rows = [list(row.values()) for row in data]
        
        # Escribir todo de una sola vez (más eficiente)
        worksheet.update([headers] + rows, "A1")
        
        # Formato: negrita en encabezados
        worksheet.format("A1:Z1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.2, "green": 0.5, "blue": 0.8},
        })
        
        # Hoja de resumen automática
        summary_sheet = spreadsheet.add_worksheet(
            title="Resumen", rows=20, cols=5
        )
        summary_data = [
            ["Metrica", "Valor"],
            ["Total de registros", len(data)],
            ["Fecha de generación", timestamp],
            ["Generado por", "incaicos_v Agent"],
        ]
        summary_sheet.update(summary_data, "A1")
        summary_sheet.format("A1:B1", {"textFormat": {"bold": True}})
        
        # Compartir si se proporcionó email
        if share_with_email:
            spreadsheet.share(
                share_with_email,
                perm_type="user",
                role="writer"
            )
        
        # Hacer accesible con el link
        spreadsheet.share(
            "", 
            perm_type="anyone", 
            role="reader"
        )
        
        sheet_url = spreadsheet.url
        
        return {
            "success": True,
            "url": sheet_url,
            "spreadsheet_id": spreadsheet.id,
            "sheet_name": sheet_name,
            "records_written": len(data),
            "message": f"Reporte generado exitosamente con {len(data)} registros"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al generar el reporte en Google Sheets"
        }

# Envolver como FunctionTool para ADK
sheets_report_tool = FunctionTool(func=generate_sheets_report)