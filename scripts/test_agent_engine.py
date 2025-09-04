"""
Fixed version of the Agent Engine test script.

This script demonstrates how to properly use the Vertex AI Agent Engine SDK
with synchronous methods as a workaround for the async method issues.

Original issue: Using await at module level caused SyntaxError
Additional issue discovered: async methods have server-side coroutine handling problems
Solution: Use synchronous methods which work correctly
"""

from vertexai import agent_engines


def main():
    # Get the Agent Engine instance
    adk_app = agent_engines.get(
        "projects/johanesa-playground-326616/locations/us-central1/reasoningEngines/6293573771064246272"
    )

    print("=== Agent Engine Information ===")
    print(f"Display name: {adk_app.display_name}")
    print(f"Resource name: {adk_app.resource_name}")
    print(f"Created: {adk_app.create_time}")
    print(f"Updated: {adk_app.update_time}")

    # Show available operations
    schemas = adk_app.operation_schemas()
    operations = [schema['name'] for schema in schemas]
    print(f"\nAvailable operations: {operations}")

    # Create a session
    print("\n=== Creating Session ===")
    session = adk_app.create_session(user_id="123")
    session_id = session['id']
    print(f"✓ Session created with ID: {session_id}")

    # List all sessions for the user
    print("\n=== Listing Sessions ===")
    sessions_response = adk_app.list_sessions(user_id="123")
    sessions = sessions_response.get('sessions', [])
    print(f"✓ Found {len(sessions)} session(s) for user '123'")
    for i, sess in enumerate(sessions, 1):
        print(f"  {i}. Session ID: {sess['id']}")

    # Get the specific session we just created
    print("\n=== Getting Specific Session ===")
    retrieved_session = adk_app.get_session(
        user_id="123", session_id=session_id)
    print(f"✓ Retrieved session: {retrieved_session['id']}")

    # Test the agent with a query
    print("\n=== Testing Agent Query ===")
    try:
        print("Sending query to agent...")
        events = list(adk_app.stream_query(
            user_id="123",
            session_id=session_id,
            message="What can you help me with regarding BigQuery?"
        ))

        if events:
            # Get the final response
            final_event = events[-1]
            if 'content' in final_event and 'parts' in final_event['content']:
                response_text = final_event['content']['parts'][0].get(
                    'text', 'No text response')
                print(f"✓ Agent response: {response_text[:200]}...")
            else:
                print(f"✓ Received {len(events)} event(s) from agent")
        else:
            print("No events received from agent")

    except Exception as e:
        print(f"Error querying agent: {e}")

    # Clean up - delete the session
    print("\n=== Cleanup ===")
    try:
        adk_app.delete_session(user_id="123", session_id=session_id)
        print("✓ Session deleted successfully")
    except Exception as e:
        print(f"Error deleting session: {e}")

    print("\n=== Summary ===")
    print("✓ Successfully demonstrated Agent Engine usage with synchronous methods")
    print("Note: async methods (async_create_session, async_list_sessions) have server-side issues")
    print("Recommendation: Use synchronous methods until async issues are resolved")


if __name__ == "__main__":
    main()
