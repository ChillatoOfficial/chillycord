import chillycord
from chillycord import app_commands

import traceback

# The guild in which this slash command will be registered.
# It is recommended to have a test guild to separate from your "production" bot
TEST_GUILD = chillycord.Object(0)
# The ID of the channel where reports will be sent to
REPORTS_CHANNEL_ID = 0


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
        await self.tree.sync(guild=TEST_GUILD)


# Define a modal dialog for reporting issues or feedback
class ReportModal(chillycord.ui.Modal, title='Your Report'):
    topic = chillycord.ui.Label(
        text='Topic',
        description='Select the topic of the report.',
        component=chillycord.ui.Select(
            placeholder='Choose a topic...',
            options=[
                chillycord.SelectOption(label='Bug', description='Report a bug in the bot'),
                chillycord.SelectOption(label='Feedback', description='Provide feedback or suggestions'),
                chillycord.SelectOption(label='Feature Request', description='Request a new feature'),
                chillycord.SelectOption(label='Performance', description='Report performance issues'),
                chillycord.SelectOption(label='UI/UX', description='Report user interface or experience issues'),
                chillycord.SelectOption(label='Security', description='Report security vulnerabilities'),
                chillycord.SelectOption(label='Other', description='Other types of reports'),
            ],
        ),
    )
    report_title = chillycord.ui.Label(
        text='Title',
        description='A short title for the report.',
        component=chillycord.ui.TextInput(
            style=chillycord.TextStyle.short,
            placeholder='The bot does not respond to commands',
            max_length=120,
        ),
    )
    description = chillycord.ui.Label(
        text='Description',
        description='A detailed description of the report.',
        component=chillycord.ui.TextInput(
            style=chillycord.TextStyle.paragraph,
            placeholder='When I use /ping, the bot does not respond at all. There are no error messages.',
            max_length=2000,
        ),
    )
    images = chillycord.ui.Label(
        text='Images',
        description='Upload any relevant images for your report (optional).',
        component=chillycord.ui.FileUpload(
            max_values=10,
            custom_id='report_images',
            required=False,
        ),
    )
    footer = chillycord.ui.TextDisplay(
        'Please ensure your report follows the server rules. Any kind of abuse will result in a ban.'
    )

    def to_view(self, interaction: chillycord.Interaction) -> chillycord.ui.LayoutView:
        # Tell the type checker what our components are...
        assert isinstance(self.topic.component, chillycord.ui.Select)
        assert isinstance(self.description.component, chillycord.ui.TextInput)
        assert isinstance(self.report_title.component, chillycord.ui.TextInput)
        assert isinstance(self.images.component, chillycord.ui.FileUpload)

        topic = self.topic.component.values[0]
        title = self.report_title.component.value
        description = self.description.component.value
        files = self.images.component.values

        view = chillycord.ui.LayoutView()
        container = chillycord.ui.Container()
        view.add_item(container)

        container.add_item(chillycord.ui.TextDisplay(f'-# User Report\n## {topic}'))

        timestamp = chillycord.utils.format_dt(interaction.created_at, 'F')
        footer = chillycord.ui.TextDisplay(f'-# Reported by {interaction.user} (ID: {interaction.user.id}) | {timestamp}')

        container.add_item(chillycord.ui.TextDisplay(f'### {title}'))
        container.add_item(chillycord.ui.TextDisplay(f'>>> {description}'))

        if files:
            gallery = chillycord.ui.MediaGallery()
            gallery.items = [chillycord.MediaGalleryItem(media=attachment.url) for attachment in files]
            container.add_item(gallery)

        container.add_item(footer)
        return view

    async def on_submit(self, interaction: chillycord.Interaction[MyClient]):
        view = self.to_view(interaction)

        # Send the report to the designated channel
        reports_channel = interaction.client.get_partial_messageable(REPORTS_CHANNEL_ID)
        await reports_channel.send(view=view)
        await interaction.response.send_message('Thank you for your report! We will look into it shortly.', ephemeral=True)

    async def on_error(self, interaction: chillycord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


client = MyClient()


@client.tree.command(guild=TEST_GUILD, description='Report an issue or provide feedback.')
async def report(interaction: chillycord.Interaction):
    # Send the modal with an instance of our `ReportModal` class
    # Since modals require an interaction, they cannot be done as a response to a text command.
    # They can only be done as a response to either an application command or a button press.
    await interaction.response.send_modal(ReportModal())


client.run('token')
