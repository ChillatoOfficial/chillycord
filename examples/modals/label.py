import datetime
import chillycord
from chillycord import app_commands

import traceback

# The guild in which this slash command will be registered.
# It is recommended to have a test guild to separate from your "production" bot
TEST_GUILD = chillycord.Object(0)


class MyClient(chillycord.Client):
    # Suppress error on the User attribute being None since it fills up later
    user: chillycord.ClientUser

    def __init__(self) -> None:
        # Just default intents and a `chillycord.Client` instance
        # We don't need a `commands.Bot` instance because we are not
        # creating text-based commands.
        intents = chillycord.Intents.default()
        super().__init__(intents=intents)

        # We need an `chillycord.app_commands.CommandTree` instance
        # to register application commands (slash commands in this case)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self) -> None:
        # Sync the application command with Discord.
        await self.tree.sync(guild=TEST_GUILD)


class TimeoutModal(chillycord.ui.Modal, title='Timeout Member'):
    # We can use a Label to attach a rich label and description to our item.
    duration = chillycord.ui.Label(
        text='Duration',
        description='How long to timeout the member for.',
        component=chillycord.ui.Select(
            options=[
                chillycord.SelectOption(label='1 minute', value='60'),
                chillycord.SelectOption(label='5 minutes', value='300'),
                chillycord.SelectOption(label='10 minutes', value='600'),
                chillycord.SelectOption(label='30 minutes', value='1800'),
                chillycord.SelectOption(label='1 hour', value='3600'),
            ],
        ),
    )

    reason = chillycord.ui.Label(
        text='Reason',
        description='The reason for the timeout.',
        component=chillycord.ui.TextInput(
            style=chillycord.TextStyle.short,
            max_length=256,
        ),
    )

    def __init__(self, member: chillycord.Member) -> None:
        self.member = member
        super().__init__()

    async def on_submit(self, interaction: chillycord.Interaction):
        # Tell the type checker what our components are...
        assert isinstance(self.duration.component, chillycord.ui.Select)
        assert isinstance(self.reason.component, chillycord.ui.TextInput)

        until = chillycord.utils.utcnow() + datetime.timedelta(seconds=int(self.duration.component.values[0]))
        await self.member.timeout(until, reason=self.reason.component.value)
        await interaction.response.send_message(
            f'Timeout {self.member.mention} until {chillycord.utils.format_dt(until)} with reason: {self.reason.component.value}',
            ephemeral=True,
        )

    async def on_error(self, interaction: chillycord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


client = MyClient()


@client.tree.command(guild=TEST_GUILD, description='Timeout a member')
async def timeout(interaction: chillycord.Interaction, member: chillycord.Member):
    # Send the modal with an instance of our `TimeoutModal` class
    # Since modals require an interaction, they cannot be done as a response to a text command.
    # They can only be done as a response to either an application command or a button press.

    # Do note that this example is illustrative, Discord comes with this timeout feature natively
    # and does not need this command or modal.
    await interaction.response.send_modal(TimeoutModal(member))


client.run('token')
