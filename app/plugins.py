from click import Group
from litestar.plugins import CLIPluginProtocol

from app.commands.metro import metro_group
from app.commands.users import users_group


class CLIPlugin(CLIPluginProtocol):
    def on_cli_init(self, cli: Group) -> None:
        cli.add_command(metro_group)
        cli.add_command(users_group)
