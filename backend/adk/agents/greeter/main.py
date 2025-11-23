# In a file like adk-samples/python/agents/greeter_agent.py

import logging
from dataclasses import dataclass, field
from adk.agent import Agent
from adk.message import Message, MessageType

# It's good practice to set up a logger for your agent
logger = logging.getLogger(__name__)

class GreeterAgent(Agent):
    # Suggested Improvement: A dedicated state class
    @dataclass
    class GreeterState:
        known_users: set[str] = field(default_factory=set)

        def to_dict(self) -> dict:
            return {"known_users": list(self.known_users)}

        @classmethod
        def from_dict(cls, data: dict) -> "GreeterState":
            return cls(known_users=set(data.get("known_users", [])))

    """
    A simple agent that greets users when they connect and
    responds to their messages.
    """

    def __init__(self, agent_id: str, state: dict | None = None):
        """
        Initializes the GreeterAgent.

        Args:
            agent_id: A unique identifier for this agent instance.
            state: A dictionary to restore the agent's state.
        """
        super().__init__(agent_id)
        # Load state or set defaults
        self.state = self.GreeterState.from_dict(state or {})
        logger.info(f"GreeterAgent '{self.agent_id}' initialized.")

    async def on_start(self):
        """
        Called when the agent is first started.
        A good place for setup logic.
        """
        logger.info(f"GreeterAgent '{self.agent_id}' is starting up.")
        # Announce that the agent is online
        await self.send_message(Message(
            content="Greeter Agent is now online and ready to chat!",
            recipient_id="broadcast" # Assuming a special ID for broadcasting
        ))

    async def on_message(self, message: Message):
        """
        Handles incoming messages from users.
        """
        logger.debug(f"Received message from '{message.sender_id}': {message.content}")

        # Greet new users
        if message.sender_id not in self.state.known_users:
            self.state.known_users.add(message.sender_id)
            response_content = f"Hello, {message.sender_id}! Welcome. It's nice to meet you."
        else:
            response_content = f"Welcome back, {message.sender_id}! You said: '{message.content}'"

        # Create and send a response
        response_message = Message(
            content=response_content,
            recipient_id=message.sender_id
        )
        await self.send_message(response_message)

    def get_state(self) -> dict:
        """
        Serializes the agent's current state to a dictionary.
        This is crucial for persistence and recovery.
        """ # In GreeterAgent.get_state:
        return self.state.to_dict()

    async def on_stop(self):
        """
        Called when the agent is shutting down.
        Used for cleanup tasks.
        """
        logger.info(f"GreeterAgent '{self.agent_id}' is shutting down.")
        # You could save final state here or send a final message
