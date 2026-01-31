# IMPORTANT:
# Import all CLI command GROUPS so they can self-register

from contract_costs.cli.commands import prepare  # noqa
from contract_costs.cli.commands import apply    # noqa
from contract_costs.cli.commands import add      # noqa
from contract_costs.cli.commands import edit     # noqa
from contract_costs.cli.commands import init     # noqa
from contract_costs.cli.commands import run      # noqa
from contract_costs.cli.commands import reports   # noqa
from contract_costs.cli.commands import show   # noqa
from contract_costs.cli.commands import set   # noqa
from contract_costs.cli.commands import login   # noqa
from contract_costs.cli.commands import logout   # noqa
from contract_costs.cli.commands import whoami   # noqa
from contract_costs.cli.commands import use_organization   # noqa
from contract_costs.cli.commands import remove   # noqa
from contract_costs.cli.commands import accept_organization   # noqa