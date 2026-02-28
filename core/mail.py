import smtplib
import logging
import os
from string import Template
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Optional, Union, Dict
from core import config

logger = logging.getLogger(__name__)

class EmailSender:
    """
    Componente reutilizável para envio de e-mails via SMTP.
    """

    def __init__(
        self,
        host: str = config.SMTP_HOST,
        port: int = config.SMTP_PORT,
        user: str = config.SMTP_USER,
        password: str = config.SMTP_PASS,
        from_email: str = config.SMTP_FROM,
        templates_dir: str = "templates",
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.from_email = from_email
        self.templates_dir = Path(templates_dir)

    def send_template(
        self,
        to: Union[str, List[str]],
        subject: str,
        template_name: str,
        variables: Dict[str, str],
        attachments: Optional[List[str]] = None,
    ) -> bool:
        """
        Carrega um template da pasta 'templates/', preenche as variáveis e envia.

        Args:
            to: Destinatário(s).
            subject: Assunto.
            template_name: Nome do arquivo (ex: 'exemplo.html').
            variables: Dicionário com valores para substituir no template.
            attachments: Lista de arquivos anexos.
        """
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            logger.error(f"Template não encontrado: {template_path}")
            return False

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Renderiza o template usando string.Template
            rendered_body = Template(content).safe_substitute(variables)
            
            # Assume HTML se o arquivo terminar em .html
            is_html = template_name.lower().endswith(".html")
            
            return self.send(to, subject, rendered_body, is_html, attachments)
        except Exception as e:
            logger.error(f"Erro ao processar template {template_name}: {e}")
            return False

    def send(
        self,
        to: Union[str, List[str]],
        subject: str,
        body: str,
        is_html: bool = False,
        attachments: Optional[List[str]] = None,
    ) -> bool:
        """
        Envia um e-mail.

        Args:
            to: Destinatário(s) do e-mail.
            subject: Assunto do e-mail.
            body: Conteúdo do e-mail (texto ou HTML).
            is_html: Define se o corpo é HTML.
            attachments: Lista de caminhos para arquivos anexos.

        Returns:
            bool: True se enviado com sucesso, False caso contrário.
        """
        if not self.user or not self.password:
            logger.error("SMTP_USER ou SMTP_PASS não configurados.")
            return False

        if isinstance(to, list):
            to_str = ", ".join(to)
        else:
            to_str = to

        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = to_str
        msg["Subject"] = subject

        # Adiciona corpo
        msg.attach(MIMEText(body, "html" if is_html else "plain"))

        # Adiciona anexos
        if attachments:
            for file_path in attachments:
                try:
                    with open(file_path, "rb") as f:
                        part = MIMEApplication(f.read(), Name=file_path.split("/")[-1])
                    part["Content-Disposition"] = f'attachment; filename="{file_path.split("/")[-1]}"'
                    msg.attach(part)
                except Exception as e:
                    logger.error(f"Erro ao anexar arquivo {file_path}: {e}")

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            logger.info(f"E-mail enviado com sucesso para {to_str}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {e}")
            return False

# Instância padrão para uso rápido
email_sender = EmailSender()
