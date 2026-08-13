"""
Configurações gerais do FinanceOS
"""

import os

# Informações da aplicação
APP_NAME = "FinanceOS"
APP_VERSION = "0.2.0"
AUTHOR = "Alison S. Nascimento"

# Configuração da página
PAGE_TITLE = "FinanceOS"
PAGE_ICON = "💰"
LAYOUT = "wide"

# Tema
SIDEBAR_STATE = "expanded"

# Configurações externalizáveis para produção. Nenhuma identidade privilegiada
# deve ficar gravada no repositório público.
ADMIN_USER = os.environ.get("FINANCEOS_ADMIN_USER", "").strip().lower()
ALLOW_REGISTRATION = os.environ.get("FINANCEOS_ALLOW_REGISTRATION", "false").strip().lower() in {
    "1", "true", "yes", "sim", "on",
}
SESSION_TIMEOUT_MINUTES = max(5, int(os.environ.get("FINANCEOS_SESSION_TIMEOUT_MINUTES", "30")))
