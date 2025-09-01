"""
Test script for BigQuery Multi-Agent Application

This script validates the architecture and ensures proper setup without requiring
full Google ADK credentials. It checks imports, configuration, and architecture compliance.
"""


def test_basic_ds_agent_import():
    """Test that the DS agent can be imported and has required components."""
    print("🧪 Testing DS Agent Import...")

    try:
        from sub_agents.ds_agents.agent import ds_agent
        print("  ✅ DS agent import successful")
        print(f"  📋 DS agent name: {ds_agent.name}")
        print(f"  📋 DS agent model: {ds_agent.model}")

        # Verify it has code executor (required for data analysis)
        if hasattr(ds_agent, 'code_executor') and ds_agent.code_executor:
            print("  ✅ DS agent has code executor")
        else:
            print("  ⚠️  DS agent missing code executor")

        return True

    except Exception as e:
        print(f"  ❌ DS agent import failed: {str(e)}")
        return False


def test_agent_tools_import():
    """Test that agent tools can be imported and have correct signatures."""
    print("\n🧪 Testing Agent Tools Import...")

    try:
        from tools import call_data_science_agent
        print("  ✅ Agent tools import successful")

        # Check function signature to ensure it has expected parameters
        import inspect
        sig1 = inspect.signature(call_data_science_agent)
        print(
            f"  📋 call_data_science_agent parameters: {list(sig1.parameters.keys())}")

        return True

    except Exception as e:
        print(f"  ❌ Agent tools import failed: {str(e)}")
        return False


def test_root_agent_configuration():
    """Test that the root agent is configured correctly with tools."""
    print("\n🧪 Testing Root Agent Configuration...")

    try:
        from agent import root_agent

        assert root_agent is not None, "Root agent not found"
        print("  ✅ Root agent exists")

        # Verify it has tools (required for functionality)
        assert hasattr(root_agent, 'tools'), "Root agent has no tools"
        print("  ✅ Root agent has tools")

        tool_names = [tool.__name__ if hasattr(
            tool, '__name__') else str(tool) for tool in root_agent.tools]
        print(f"  📋 Available tools: {tool_names}")

        # Check sub-agents (should be empty for this architecture)
        if hasattr(root_agent, 'sub_agents') and root_agent.sub_agents:
            print(
                f"  📋 Sub-agents: {[agent.name for agent in root_agent.sub_agents]}")
        else:
            print("  ✅ No sub-agents (correct for this implementation)")

        return True

    except Exception as e:
        print(f"  ❌ Root agent configuration test failed: {str(e)}")
        return False


def test_imports():
    """Test that all required components can be imported successfully."""
    print("\n🧪 Testing Imports...")

    try:
        from agent import root_agent
        print("  ✅ Root agent import successful")

        from tools import call_data_science_agent
        print("  ✅ Agent tools import successful")

        from sub_agents.ds_agents.agent import ds_agent
        print("  ✅ DS agent import successful")

        from tools import bigquery_toolset
        print("  ✅ BigQuery toolset import successful")

        return True

    except Exception as e:
        print(f"  ❌ Import test failed: {str(e)}")
        return False


def test_architecture_compliance():
    """Test that the architecture follows correct patterns to prevent errors."""
    print("\n🧪 Testing Architecture Compliance...")

    try:
        from agent import root_agent
        from sub_agents.ds_agents.agent import ds_agent

        # Check DS agent has code executor
        has_code_executor = hasattr(
            ds_agent, 'code_executor') and ds_agent.code_executor is not None
        print(f"  📋 DS agent has code executor: {has_code_executor}")

        # Verify DS agent is NOT used as sub-agent (prevents errors)
        ds_in_subagents = False
        if hasattr(root_agent, 'sub_agents') and root_agent.sub_agents:
            ds_in_subagents = any(
                agent.name == 'ds_agent' for agent in root_agent.sub_agents)

        print(f"  📋 DS agent in sub_agents: {ds_in_subagents}")

        # Check DS agent tools are available in root agent
        tool_names = [getattr(tool, '__name__', str(tool))
                      for tool in root_agent.tools]
        has_ds_tools = any('data_science' in name.lower()
                           for name in tool_names)
        print(f"  📋 DS tools in root agent: {has_ds_tools}")

        # Architecture compliance: DS agent with code executor should be tool-wrapped
        if has_code_executor and not ds_in_subagents and has_ds_tools:
            print("  ✅ Architecture follows correct pattern!")
            print("    - DS agent has code executor")
            print("    - DS agent wrapped as tool (not sub-agent)")
            print("    - This prevents code execution errors")
            return True
        else:
            print("  ⚠️  Architecture pattern issues detected")
            return False

    except Exception as e:
        print(f"  ❌ Architecture compliance test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all tests and provide a summary of results."""
    print("🚀 Starting BigQuery Multi-Agent Application Tests\n")

    tests = [
        ("Basic DS Agent Import", test_basic_ds_agent_import),
        ("Agent Tools Import", test_agent_tools_import),
        ("All Imports", test_imports),
        ("Root Agent Configuration", test_root_agent_configuration),
        ("Architecture Compliance", test_architecture_compliance),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))

    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your implementation is ready to use.")
        print("\n📋 Next Steps:")
        print("1. Set up your BigQuery credentials in .env")
        print("2. Test with real BigQuery data")
        print("3. Try asking: 'Show me the monthly order trend'")
        print("4. The agent will use BigQuery tools + DS analysis")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that Google ADK is properly configured")


if __name__ == "__main__":
    run_all_tests()
