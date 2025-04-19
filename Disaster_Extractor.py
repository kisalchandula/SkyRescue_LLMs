from typing import Optional, Literal
import json
from pydantic import BaseModel, Field
import anthropic

from config import AnthropicConfig


def pprint(model: BaseModel):
    print(json.dumps(model.model_dump(), indent=2))


class DisasterEvent(BaseModel):
    """
    Extracted disaster event details from a Bluesky post.
    """
    location: Optional[str] = Field(description="Detected location of the disaster, if mentioned.")
    severity: Literal["low", "medium", "high", "unknown"] = Field(description=""" 
        The estimated severity of the disaster event.
        Use 'unknown' if severity cannot be determined from the post.
    """)
    reasoning: str = Field(description=""" 
        The reasoning behind the location and severity classification.
        Explain why a certain severity and location were assigned based on the post text.
    """)


class ClaudeDisasterExtractor:
    """
    A class to extract disaster event information from Bluesky posts using Claude's API.
    """

    def __init__(self):
        """
        Initialize the ClaudeDisasterExtractor.
        """
        config = AnthropicConfig()

        self.llm = anthropic.Client(api_key=config.api_key)  # Initialize the Anthropic client

        self.prompt = """
        You are an expert at analyzing social media posts related to disasters.
        Your task is to extract:
        - The disaster's LOCATION (if available).
        - The SEVERITY of the disaster (low, medium, high, or unknown).
        - A REASONING explaining your conclusions.

        Here is the post:
        {text}
        """  # Use the prompt directly here instead of PromptTemplate for simplicity

    def extract_disaster_info(self, text: str) -> DisasterEvent:
        """
        Extract disaster event information from the post text.

        Args:
            text (str): The text of the Bluesky post.

        Returns:
            DisasterEvent: Extracted information about the disaster event.
        """
        response = self.llm.completions.create(
            prompt=self.prompt.format(text=text),
            model="claude-v1"  # Specify the Claude model (adjust according to your API)
        )

        # Process the response and map it to the DisasterEvent model
        # Assuming response['text'] contains the structured result
        result = response.get('text', '')
        # You need to parse and process this result to create a DisasterEvent instance
        # (Example logic may vary based on actual output format)
        event_data = {
            "location": "Extracted location from response",
            "severity": "Extracted severity from response",
            "reasoning": result
        }
        return DisasterEvent(**event_data)


if __name__ == "__main__":
    # initialize the disaster extractor
    extractor = ClaudeDisasterExtractor()

    # Example 1 -> clear disaster, high severity
    post = "Massive earthquake shakes downtown Los Angeles, multiple buildings collapsed."
    response = extractor.extract_disaster_info(post)
    print(post)
    pprint(response)

    # Example 2 -> unclear severity
    post = "Flooding reported in parts of Jakarta following heavy rains."
    response = extractor.extract_disaster_info(post)
    print(post)
    pprint(response)
