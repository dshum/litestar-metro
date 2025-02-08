from typing import cast

import anyio
import click

from app.configs import sqlalchemy_config
from app.schemas import UserCreate
from app.services import UserService


@click.group(name="users", help="Manage users.")
def users_group() -> None:
    ...


@users_group.command(name="create", help="Create user")
@click.option(
    "--username",
    help="Username",
    type=click.STRING,
    required=False,
)
@click.option(
    "--password",
    help="Password",
    type=click.STRING,
    required=False,
)
@click.option(
    "--first-name",
    help="First name",
    type=click.STRING,
    required=False,
)
@click.option(
    "--last-name",
    help="Last name",
    type=click.STRING,
    required=False,
)
def create_user(
        username: str | None,
        password: str | None,
        first_name: str | None,
        last_name: str | None,
) -> None:
    async def _create_user(user: UserCreate):
        async with sqlalchemy_config.get_session() as db_session:
            user_service = UserService(db_session)
            user = await user_service.create(data=user.to_dict(), auto_commit=True)
            click.echo(f"Created user {user.username}")

    username = username or click.prompt("Username")
    password = password or click.prompt("Password", hide_input=True, confirmation_prompt=True)
    first_name = first_name or click.prompt("First name")
    last_name = last_name or click.prompt("Last name")

    user_create = UserCreate(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
    )

    anyio.run(_create_user, cast("User", user_create))
