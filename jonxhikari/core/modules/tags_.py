import tanjun

from jonxhikari import SlashClient


component = tanjun.Component()







@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
