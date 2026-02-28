import time
import schedule
from pathlib import Path
from datetime import date, timedelta
from typing import Optional, List

from core.api import WakaTimeAPI, WakaTimeAPIError
from core.mail import EmailSender
from core.config import setup_logger, EXECUTION_TIME, DEVELOPER_MAIL, DEVELOPER_NAME, ENABLE_EMAIL_INSIGHTS
from src.orchestrator.repository import WakaTimeRepository
from core.models import DailySummary

logger = setup_logger(__name__)

# Diretório de templates relativo ao projeto
TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

class WakaTimeOrchestrator:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.repo = WakaTimeRepository()
        self.email = EmailSender(templates_dir=str(TEMPLATES_DIR))
    
    def extract_and_save(self, target_date: Optional[date] = None) -> bool:
        if target_date is None:
            target_date = date.today() - timedelta(days=1)
        
        logger.info(f"Iniciando extração para {target_date}")
        
        try:
            with WakaTimeAPI(self.api_token) as api:
                summary = api.get_summaries_for_date(target_date)
            
            self.repo.save_summary(summary)
            
            total_hours = summary.grand_total.total_seconds / 3600
            logger.info(f"Dados de {target_date} salvos! Total: {total_hours:.2f}h")

            # Envia email de insights (se ativado)
            if ENABLE_EMAIL_INSIGHTS:
                self._send_insights_email(summary)
            else:
                logger.info("Envio de email de insights desativado via configuração.")

            return True
            
        except WakaTimeAPIError as e:
            logger.error(f"Erro WakaTime API: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return False
    
    def _send_insights_email(self, summary: DailySummary) -> None:
        """Envia email com o resumo de insights para o desenvolvedor."""
        try:
            total_hours = f"{summary.grand_total.total_seconds / 3600:.1f}"
            total_text = summary.grand_total.text or f"{total_hours}h"

            variables = {
                "developer_name": DEVELOPER_NAME,
                "date": summary.range.date,
                "total_hours": total_hours,
                "total_text": total_text,
                "languages": self._build_stat_table(summary.languages),
                "projects": self._build_stat_table(summary.projects),
                "editors": self._build_stat_table(summary.editors),
            }

            success = self.email.send_template(
                to=DEVELOPER_MAIL,
                subject=f"📊 Dev Insights — {summary.range.date}",
                template_name="insights.html",
                variables=variables,
            )

            if success:
                logger.info(f"Email de insights enviado para {DEVELOPER_MAIL}")
            else:
                logger.warning("Falha ao enviar email de insights")

        except Exception as e:
            logger.error(f"Erro ao preparar email de insights: {e}")

    @staticmethod
    def _build_stat_table(items: Optional[List] = None) -> str:
        """Gera uma tabela HTML a partir de uma lista de stats."""
        if not items:
            return '<p style="color: #8b949e; font-size: 14px;">Nenhum dado disponível.</p>'

        rows = ""
        for item in items:
            percent = getattr(item, "percent", 0) or 0
            text = getattr(item, "text", "") or ""
            rows += f"""
            <tr>
              <td class="name-cell">{item.name}</td>
              <td>{text}</td>
              <td style="width: 30%;">
                <div class="progress-bar">
                  <div class="progress-fill" style="width: {percent:.0f}%;"></div>
                </div>
              </td>
              <td style="text-align: right; color: #8b949e;">{percent:.1f}%</td>
            </tr>"""

        return f"""
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>Tempo</th>
              <th>Progresso</th>
              <th style="text-align: right;">%</th>
            </tr>
          </thead>
          <tbody>{rows}
          </tbody>
        </table>"""

    def backfill(self, start_date: date, end_date: date) -> int:
        logger.info(f"Backfill de {start_date} até {end_date}")
        success_count = 0
        current = start_date
        
        while current <= end_date:
            if self.extract_and_save(current):
                success_count += 1
            current += timedelta(days=1)
            time.sleep(1)
        
        logger.info(f"Backfill finalizado. {success_count} dias.")
        return success_count
    
    def run_scheduled(self) -> None:
        logger.info(f"Agendado para {EXECUTION_TIME}")
        schedule.every().day.at(EXECUTION_TIME).do(self.extract_and_save)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def run_once(self) -> None:
        logger.info("Execução única...")
        self.extract_and_save(target_date=date.today() - timedelta(days=1))
