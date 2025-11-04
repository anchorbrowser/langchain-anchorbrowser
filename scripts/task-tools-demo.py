import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from langchain_anchorbrowser import (
    AnchorTaskCreateTool,
    AnchorTaskListTool,
    AnchorTaskDeleteTool,
    AnchorTaskRunTool,
    AnchorTaskDeployTool,
    AnchorTaskListExecutionsTool,
    AnchorTaskToolKit,
)

# Set up API key
if not os.environ.get("ANCHORBROWSER_API_KEY"):
    print("Error: ANCHORBROWSER_API_KEY environment variable not set")
    print("Please set it with: export ANCHORBROWSER_API_KEY=your_api_key")
    sys.exit(1)

print("=== Anchor Browser Task Tools Demo ===\n")

# Example 1: List all tasks
print("Example 1: List all tasks")
print("-" * 40)

list_tool = AnchorTaskListTool()
try:
    tasks_result = list_tool.invoke({
        "page": "1",
        "limit": "10"
    })
    tasks_data = json.loads(tasks_result)
    tasks_list = tasks_data.get('data', {}).get('tasks', [])
    total = tasks_data.get('data', {}).get('total', 0)
    print(f"Found {len(tasks_list)} task(s) (in page 1, total: {total})")
    if tasks_list:
        for task in tasks_list:  # Show first 3
            print(f"  - {task.get('name')} (ID: {task.get('id', 'N/A')}) {"--DELETED" if task.get('deleted', False) else ""}")
except Exception as e:
    print(f"Error listing tasks: {e}")

print("\n" + "="*50 + "\n")

# Example 2: Create a new task
print("Example 2: Create a new task")
print("-" * 40)

create_tool = AnchorTaskCreateTool()
task_name = "demo-task1"

# Example TypeScript task code (base64 encoded)
task_code = "aW1wb3J0IEFuY2hvckNsaWVudCBmcm9tICdhbmNob3Jicm93c2VyJzsKCi8vIEluaXRpYWxpemUgdGhlIEFuY2hvciBjbGllbnQgd2l0aCB5b3VyIEFQSSBrZXkKY29uc3QgYW5jaG9yQ2xpZW50ID0gbmV3IEFuY2hvckNsaWVudCh7CiAgICBhcGlLZXk6IHByb2Nlc3MuZW52LkFOQ0hPUl9BUElfS0VZLAp9KTsKCi8vIEV4cG9ydCB0aGUgbWFpbiBmdW5jdGlvbiBhcyB0aGUgZGVmYXVsdCBleHBvcnQKZXhwb3J0IGRlZmF1bHQgYXN5bmMgZnVuY3Rpb24gcnVuKCkgewoKICAgIC8vIENyZWF0ZSBhIG5ldyBicm93c2VyIGluc3RhbmNlCiAgICBjb25zdCBicm93c2VyID0gYXdhaXQgYW5jaG9yQ2xpZW50LmJyb3dzZXIuY3JlYXRlKCk7CiAgICBjb25zdCBwYWdlID0gYnJvd3Nlci5jb250ZXh0cygpWzBdLnBhZ2VzKClbMF07CgogICAgLy8gQWNjZXNzIGlucHV0IHZhbHVlcwogICAgY29uc3QgdGFyZ2V0VXJsID0gcHJvY2Vzcy5lbnYuQU5DSE9SX1RBUkdFVF9VUkw7CiAgICBjb25zdCBtYXhQYWdlcyA9IHBhcnNlSW50KHByb2Nlc3MuZW52LkFOQ0hPUl9NQVhfUEFHRVMgfHwgJzEwJyk7CgogICAgLy8gSW1wbGVtZW50IHlvdXIgYXV0b21hdGlvbiBsb2dpYwogICAgYXdhaXQgcGFnZS5nb3RvKHRhcmdldFVybCk7CiAgICBjb25zb2xlLmxvZyhgU2NyYXBpbmcgdXAgdG8gJHttYXhQYWdlc30gcGFnZXMgZnJvbSAke3RhcmdldFVybH1gKTsKCiAgICAvLyBBbHdheXMgY2xvc2UgdGhlIGJyb3dzZXIgd2hlbiBkb25lCiAgICBhd2FpdCBicm93c2VyLmNsb3NlKCk7CgogICAgLy8gUmV0dXJuIGEgcmVzdWx0IG9iamVjdCB3aXRoIHN1Y2Nlc3Mgc3RhdHVzIGFuZCBtZXNzYWdlCiAgICByZXR1cm4gewogICAgICAgIHN1Y2Nlc3M6IHRydWUsCiAgICAgICAgbWVzc2FnZTogJ1Rhc2sgY29tcGxldGVkIHN1Y2Nlc3NmdWxseScKICAgIH07Cn0="

try:
    create_result = create_tool.invoke({
        "name": task_name,
        "description": "A demo task for Anchor Browser LangChain tools",
        "language": "typescript",
        "code": task_code
    })
    create_data = json.loads(create_result)
    task_id = create_data.get("data", {}).get("id") or create_data.get("id")
    print(f"Task created successfully!")
    print(f"Task ID: {task_id}")
    print(f"Task Name: {task_name}")
except Exception as e:
    print(f"Task creation failed: {e}")
    task_id = None
    # Try to find existing task
    try:
        tasks_result = list_tool.invoke({"page": "1", "limit": "10"})
        tasks_data = json.loads(tasks_result)
        tasks_list = tasks_data.get('data', {}).get('tasks', [])
        for task in tasks_list:
            if 'demo-task' in task.get('name', ''):
                task_id = task.get('id')
                task_name = task.get('name')
                print(f"Using existing task: {task_name} (ID: {task_id})")
                break
    except:
        pass

if not task_id:
    print("Could not create or find a task. Exiting demo.")
    sys.exit(1)

print("\n" + "="*50 + "\n")

# Example 3: Deploy task code
print("Example 3: Deploy task code")
print("-" * 40)

deploy_tool = AnchorTaskDeployTool()

try:
    deploy_result = deploy_tool.invoke({
        "task_id": task_id,
        "version": "1",
        "code": task_code
    })
    deploy_data = json.loads(deploy_result)
    print("Task deployed successfully!")
    if deploy_data.get("version"):
        print(f"Version: {deploy_data.get('version')}")
except Exception as e:
    print(f"Deploy failed (task may already have code deployed): {e}")

print("\n" + "="*50 + "\n")

# Example 4: Run a task
print("Example 4: Run a task")
print("-" * 40)

run_tool = AnchorTaskRunTool()

# Optional: provide environment variables (keys must start with ANCHOR_)
inputs_json = '{"ANCHOR_TARGET_URL": "https://example.com", "ANCHOR_MAX_PAGES": "10"}'

try:
    run_result = run_tool.invoke({
        "task_id": task_id,
        "version": "1",  # or "draft", or a version number like "1.0"
        # session_id is not passed - system will create a new session automatically
        "inputs": inputs_json  # Optional: environment variables (keys must start with ANCHOR_)
    })
    run_data = json.loads(run_result)
    print("Task execution started!")
    execution_id = run_data.get("execution_id") or run_data.get("id")
    if execution_id:
        print(f"Execution ID: {execution_id}")
    if run_data.get("status"):
        print(f"Status: {run_data.get('status')}")
except Exception as e:
    print(f"Run task error: {e}")

print("\n" + "="*50 + "\n")

# Example 5: List task executions
print("Example 5: List task executions")
print("-" * 40)

executions_tool = AnchorTaskListExecutionsTool()

try:
    # List all executions
    print("\n--- All Executions ---")
    executions_result = executions_tool.invoke({
        "task_id": task_id,
        "page": "1",
        "limit": "10"
    })
    print(executions_result)
    
    # List executions filtered by status
    print("\n--- Filtered by Status (success) ---")
    try:
        filtered_result = executions_tool.invoke({
            "task_id": task_id,
            "page": "1",
            "limit": "10",
            "status": "success",
            "version": "1"
        })
        print(filtered_result)
    except Exception as e:
        print(f"Filtered query error: {e}")
    
    # List executions filtered by status
    print("\n--- Filtered by Status (failure) ---")
    try:
        filtered_result = executions_tool.invoke({
            "task_id": task_id,
            "page": "1",
            "limit": "10",
            "status": "failure",
            "version": "1"
        })
        print(filtered_result)
    except Exception as e:
        print(f"Filtered query error: {e}")
except Exception as e:
    print(f"Error listing executions: {e}")

print("\n" + "="*50 + "\n")

# Example 6: Using the Task Toolkit
print("Example 6: Using the Task Toolkit")
print("-" * 40)

toolkit = AnchorTaskToolKit()
tools = toolkit.get_tools()

print(f"The AnchorTaskToolKit provides {len(tools)} tools:")
for tool in tools:
    print(f"  - {tool.name}")

# Example: Use a tool from the toolkit
print(f"\nUsing 'list_tasks' from toolkit:")
list_tool_from_kit = next(t for t in tools if t.name == "list_tasks")
try:
    result = list_tool_from_kit.invoke({"page": "1", "limit": "3"})
    result_data = json.loads(result)
    tasks_list = result_data.get('data', {}).get('tasks', [])
    total = result_data.get('data', {}).get('total', 0)
    print(f"  Found {len(tasks_list)} task(s) (total: {total})")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*50 + "\n")

# Cleanup (optional)
print("Example 7: Delete task (optional cleanup)")
print("-" * 40)

# Uncomment the following lines to delete the task after the demo
# delete_tool = AnchorTaskDeleteTool()
# try:
#     delete_result = delete_tool.invoke({"task_id": task_id})
#     print(f"Task {task_name} deleted successfully")
# except Exception as e:
#     print(f"Delete error: {e}")

print(f"Task '{task_name}' (ID: {task_id}) was created for this demo.")
print("Uncomment the delete code above to remove it, or delete it manually via the API.")

print("\n=== Demo Complete ===")

