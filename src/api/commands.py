# ==================== FLASK COMMANDS ====================
# Flask commands are functions you can run from the terminal
# Useful for maintenance tasks, populating the DB, cronjobs, etc.

# Import click to handle command-line arguments
import click
# Import the database instance
from api.models import db

"""
This file allows you to add custom commands using the @app.cli.command decorator
Flask commands are useful for running tasks outside the API but with access to the DB
Example: Import Bitcoin price every night at 12am, populate test data, etc.
"""

# Main function that registers all commands in the Flask application
def setup_commands(app):
    
    """ 
    Example command "insert-test-users" that you can run from the terminal
    Usage: $ flask insert-test-users 5
    Note: 5 is the number of users to create
    """
    # Decorator that registers the command with the name "insert-test-users"
    @app.cli.command("insert-test-users")  # Define the command name
    # Decorator that defines "count" as a required argument for the command
    @click.argument("count")  # The command expects to receive a number
    def insert_test_users(count):  # Function that executes when calling the command
        # This code is commented out because the User model was replaced
        # print("Creating test users")
        # for x in range(1, int(count) + 1):  # Loop to create N users
        #     user = User()  # Create a new User instance
        #     user.email = "test_user" + str(x) + "@test.com"  # Assign email
        #     user.password = "123456"  # Assign password
        #     user.is_active = True  # Mark as active
        #     db.session.add(user)  # Add the user to the DB session
        #     db.session.commit()  # Save the user to the database
        #     print("User: ", user.email, " created.")  # Confirm creation

        # Print confirmation message
        print("All test users created")

    # Additional command to insert test data (not yet implemented)
    @app.cli.command("insert-test-data")  # Register the command
    def insert_test_data():  # Function that will be executed
        pass  # Does nothing yet (pending implementation)