class DisasterPostClassifier:
    """
    A class to classify whether a post is related to a disaster or not.
    """
    def __init__(self):
        self.disaster_keywords = [
            "earthquake", "wildfire", "flood", "hurricane", "tsunami", "storm", "avalanche", "drought"
        ]

    def classify_post(self, text: str) -> bool:
        """
        Classify the post as disaster-related based on keywords. (Future replace by binary Classifier like Logistic-regression)

        Args:
            text (str): The content of the Bluesky post.

        Returns:
            bool: True if the post is related to a disaster, False otherwise.
        """
        # Search for disaster-related keywords in the post text
        text = text.lower()
        return any(keyword in text for keyword in self.disaster_keywords)
