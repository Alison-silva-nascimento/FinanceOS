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

# Configurações externalizáveis para produção. O padrão preserva a instalação atual.
ADMIN_USER = os.environ.get("FINANCEOS_ADMIN_USER", "alison.nascimento").strip().lower()
SESSION_TIMEOUT_MINUTES = max(5, int(os.environ.get("FINANCEOS_SESSION_TIMEOUT_MINUTES", "30")))
