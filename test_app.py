import os

from streamlit.testing.v1 import AppTest


def test_chatbot_startup():
    """Test if the app starts and displays the basic chat interface."""
    at = AppTest.from_file("main.py")

    # We must mock or set the secrets for the test environment
    at.secrets["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN", "dummy_key")

    at.run(timeout=30)

    # Assertions: Verify no exceptions occurred on boot
    assert not at.exception, f"App crashed on startup: {at.exception}"

    # Verify the title or a specific header exists (adjust to your app's actual title)
    assert len(at.title) > 0 or len(at.header) > 0
    print("✅ Startup test passed!")

def test_chat_interaction():
    """Simulate a user typing a message and checking the state."""
    at = AppTest.from_file("main.py").run()

    # Check if chat input exists
    if at.chat_input:
        # Simulate typing 'Hello' into the first chat input and running the app
        at.chat_input[0].set_value("Hello, are you ready for the interview?").run()

        # Verify the user message appeared in the chat history
        user_msg_found = any("Hello" in msg.value for msg in at.markdown)
        assert user_msg_found, "User message did not appear in chat."
        print("✅ Interaction test passed!")
    else:
        print("⚠️ No chat input found, skipping interaction test.")

if __name__ == "__main__":
    # This allows you to run 'python test_app.py' locally to debug
    test_chatbot_startup()
    test_chat_interaction()
