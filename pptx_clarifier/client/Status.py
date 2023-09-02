import datetime


class Status:
    """Used to store the status of a request to the server."""

    def __init__(self, response):
        """
        Initialize a Status object from a JSON response from the server.

        Args:
            response: A JSON response from the server.

        Returns:
            A Status object.
        """
        response = response.json()
        self.status = response['status']
        self.filename = response['filename']
        self.timestamp = datetime.datetime.fromtimestamp(response['timestamp'])
        self.explanation = response['explanation']

    @property
    def is_done(self):
        """
        Returns:
            True if the status is 'done', False otherwise.
        """
        return self.status == 'done'

    @property
    def is_pending(self):
        """
        Returns:
            True if the status is 'pending', False otherwise.
        """
        return self.status == 'pending'

    def __str__(self) -> str:
        """
        Returns:
            A string representation of the Status object.
        """
        return f"Status: {self.status}\n" \
               f"Filename: {self.filename}\n" \
               f"Timestamp: {self.timestamp}\n" \
               f"Explanation: {self.explanation}"

