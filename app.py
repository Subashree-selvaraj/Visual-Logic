import os
import json
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
import graphviz # Import the graphviz library for Python
import streamlit.components.v1 as components # Keep for potential future use

# Load environment variables from a local .env file if present (helps local development)
load_dotenv()

# --------------------------
# Setup OpenRouter client
# --------------------------
# IMPORTANT: Fetch OpenRouter API key from environment variables (secrets for deployment).
try:
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        st.error("❌ OpenRouter API key not found. Please set the OPENROUTER_API_KEY environment variable.")
        st.stop() # Stop the app if API key is not available

    client = OpenAI(
        api_key=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1"
    )
except Exception as e:
    st.error(f"Failed to initialize OpenAI client. Please check your API key setup. Error: {e}")
    st.stop() # Stop the app if client cannot be initialized

# --------------------------
# Streamlit UI Config
# --------------------------
st.set_page_config(
    page_title="AI Code Flow Visualizer",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ AI Code-to-Interactive-Flowchart")

st.markdown("""
This app:
- Analyzes your code
- Breaks it into **simple, detailed steps**
- Visualizes it with **clear, colorful flowcharts** for easy understanding.
""")

# --------------------------
# Code Input
# --------------------------
code_input = st.text_area(
    "Paste your code here:",
    height=300,
    placeholder="e.g., def factorial(n): ..."
)

# --------------------------
# Model selection
# --------------------------
# Try to discover available models from the OpenRouter client so we don't select unavailable endpoints
available_models = []
try:
    resp = client.models.list()
    # Support both dict-like and object-like responses
    data = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
    if not data and isinstance(resp, list):
        data = resp

    if data:
        for m in data:
            model_id = None
            if isinstance(m, dict):
                model_id = m.get("id") or m.get("model")
            else:
                model_id = getattr(m, "id", None) or getattr(m, "model", None)
            if model_id:
                available_models.append(model_id)
except Exception as e:
    # Don't fail the app on model discovery errors; we'll show defaults below and surface the warning
    st.warning(f"Could not fetch model list from OpenRouter: {e}")

if not available_models:
    # Fallback: sensible defaults (may still be unavailable depending on OpenRouter account)
    available_models = [
        "openrouter/cypher-alpha:free",
        "mistralai/mistral-small-3.2-24b-instruct:free",
        "deepseek/deepseek-r1:free",
    ]

model_choice = st.selectbox("AI Model (choose an available model):", available_models, index=0)

# --------------------------
# Generate Button
# --------------------------
if st.button("Generate Diagram 🚀"):
    if not code_input.strip():
        st.warning("Please paste some code first!")
    else:
        with st.spinner("Analyzing code and generating visualization..."):
            # Prompt for Flowchart JSON
            flowchart_prompt = f"""
You are an expert developer assistant specialized in Data Structures and Algorithms (DSA) and code flow visualization.
Analyze the following Python code and break it down into a **highly detailed, step-by-step flowchart representation**.
Your goal is to make the logical flow, conditions, loops, and function calls **exceptionally clear and easy to understand for a student learning DSA**.

**For each step, be as specific as possible.**
- **Start/End:** Clearly mark the beginning and end of the function/program.
- **Initialization:** Detail variable declarations and initial values.
- **Conditions (If/Else):** Explicitly state the condition being checked and provide separate paths for "True" and "False" (or "Yes"/"No").
- **Loops (For/While)::** Show the loop initialization, condition, the body of the loop, and the iteration step. Clearly show the flow returning to the condition.
- **Function Calls:** Indicate when a function is called, including arguments passed. If it's a recursive call, show it clearly.
- **Return Statements:** Indicate what value is being returned.
- **Variable State:** Briefly mention important variable state changes if they are critical to understanding the flow (e.g., "Increment counter", "Update sum").

**Your output MUST be a JSON object with the following structure:**
  "nodes": a list of nodes, each with:
    - "id": a unique, short identifier (e.g., "S1", "C2", "L3")
    - "label": a concise, descriptive label for the step (e.g., "Check n <= 1", "Loop: for i in range(N)", "Return result")
  "edges": a list of connections, each with:
    - "from": the id of the source node
    - "to": the id of the target node
    - "label": optional, a short label for the connection (e.g., "Yes", "No", "Next Iteration")

**IMPORTANT:**
- Output ONLY JSON. Do not include any additional text, explanations, or markdown outside the JSON object.
- Ensure the flow is comprehensive and captures all logical branches and iterations.

**Example of a detailed JSON structure for a simple factorial function:**
{{
  "nodes": [
    {{"id": "A", "label": "Start: factorial(n)"}},
    {{"id": "B", "label": "Check if n <= 1"}},
    {{"id": "C", "label": "Return 1 (Base Case)"}},
    {{"id": "D", "label": "Calculate n-1"}},
    {{"id": "E", "label": "Recursive Call: factorial(n-1)"}},
    {{"id": "F", "label": "Multiply n * result_from_recursion"}},
    {{"id": "G", "label": "Return final result"}},
    {{"id": "H", "label": "End"}}
  ],
  "edges": [
    {{"from": "A", "to": "B"}},
    {{"from": "B", "to": "C", "label": "Yes"}},
    {{"from": "B", "to": "D", "label": "No"}},
    {{"from": "C", "to": "H"}},
    {{"from": "D", "to": "E"}},
    {{"from": "E", "to": "F"}},
    {{"from": "F", "to": "G"}},
    {{"from": "G", "to": "H"}}
  ]
}}

Here is the code:
```python
{code_input}
"""
            
            # Prompt for Code Explanation - ENHANCED FOR DEEPER UNDERSTANDING AND CREATIVE LEARNING
            code_explanation_prompt = f"""
You are an expert programming tutor, specializing in Data Structures and Algorithms (DSA).
Explain the following Python code in a clear, concise, and easy-to-understand manner for a student.
Go beyond just describing what each line does. Focus on:

1.  **Purpose and "Why":** Explain *why* certain lines or blocks of code are necessary. What problem does this specific part solve, or what role does it play in the overall logic?
2.  **Core Logic and Ideation:** Break down the main algorithm or logic. How does the code achieve its goal step-by-step, and what was the thought process behind designing it this way?
3.  **Real-World Analogies/Use Cases:** Briefly mention practical scenarios or real-world problems where this code, or the underlying DSA concept it demonstrates, would be applied. Use simple, relatable analogies.
4.  **Key Concepts:** Highlight important programming or DSA concepts demonstrated (e.g., recursion, iteration, specific data structure operations, time/space complexity implications if relevant).
5.  **Creative Learning Elements (like Flashcards/Q&A):**
    * **Key Takeaways:** Provide 1-2 concise bullet points summarizing the most crucial learnings.
    * **Self-Assessment Questions:** Include 1-2 simple Q&A pairs to prompt active recall and understanding.
        * **Question:** [Your question here]?
        * **Answer:** [Concise answer here].

Present the explanation using Markdown for clear formatting.
Keep the overall explanation student-friendly and aim for clarity over exhaustive detail.
Limit the explanation to a maximum of 400 words to keep it digestible.

Here is the code:
```python
{code_input}
```
"""

            try:
                # Get Flowchart JSON from AI
                flowchart_response = client.chat.completions.create(
                    model=model_choice,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant specialized in code analysis and visualization, outputting only valid JSON."},
                        {"role": "user", "content": flowchart_prompt}
                    ],
                    temperature=0.3
                )
                flowchart_output = flowchart_response.choices[0].message.content.strip()

                # Get Code Explanation from AI
                explanation_response = client.chat.completions.create(
                    model=model_choice,
                    messages=[
                        {"role": "system", "content": "You are a helpful programming tutor, providing clear explanations."},
                        {"role": "user", "content": code_explanation_prompt}
                    ],
                    temperature=0.3
                )
                code_explanation = explanation_response.choices[0].message.content.strip()


                # Attempt to extract only the JSON part from the flowchart output
                json_start = flowchart_output.find('{')
                json_end = flowchart_output.rfind('}')

                if json_start != -1 and json_end != -1 and json_end > json_start:
                    json_string = flowchart_output[json_start : json_end + 1]
                else:
                    json_string = flowchart_output

                # Attempt to parse JSON
                try:
                    graph_data = json.loads(json_string)
                except json.JSONDecodeError:
                    st.error("❌ The AI did not return valid JSON for the flowchart. Here is the raw output:")
                    st.code(flowchart_output)
                    st.stop()

                # Validate keys
                if not ("nodes" in graph_data and "edges" in graph_data):
                    st.error("❌ Flowchart JSON missing 'nodes' or 'edges'. Raw output:")
                    st.code(flowchart_output)
                    st.stop()

                # --- START: Graphviz Generation ---
                # Create a Digraph object
                # Using 'ortho' splines for clearer, right-angle connections, and TB for Top-Bottom direction
                dot = graphviz.Digraph(comment='Code Flowchart', graph_attr={'rankdir': 'TB', 'splines': 'ortho'})

                # Add nodes to the Graphviz diagram
                for node in graph_data["nodes"]:
                    node_id = f"N_{node['id']}" # Ensure IDs are unique strings
                    node_label = node["label"]
                    
                    # Default styles
                    shape = "box"
                    fillcolor = "#1E90FF" # Default blue
                    fontcolor = "white"
                    style = "filled"

                    # Apply specific styling based on label content
                    if "start" in node_label.lower():
                        fillcolor = "#32CD32" # Green for start
                        shape = "oval" # Oval for start/end
                    elif "check" in node_label.lower() or "if" in node_label.lower() or "loop" in node_label.lower() or "condition" in node_label.lower():
                        fillcolor = "#FFD700" # Yellow for conditions/loops
                        shape = "diamond" # Diamond for decisions
                        fontcolor = "black" # Black text for yellow background
                    elif "return" in node_label.lower() or "end" in node_label.lower():
                        fillcolor = "#8A2BE2" # Purple for end/return
                        shape = "oval" # Oval for start/end
                    elif "call" in node_label.lower() or "function" in node_label.lower():
                        fillcolor = "#FF6347" # Red for function calls
                        shape = "box" # Box for processes (or perhaps a rounded box for subroutines)
                    elif "initialize" in node_label.lower() or "variable" in node_label.lower() or "assign" in node_label.lower():
                        fillcolor = "#ADD8E6" # Light blue for initialization/data
                        fontcolor = "black"
                        shape = "box" # Process box

                    dot.node(
                        node_id,
                        label=node_label,
                        shape=shape,
                        style=style,
                        fillcolor=fillcolor,
                        fontcolor=fontcolor,
                        tooltip=node_label # Tooltip for hover effect (if supported by viewer)
                    )

                # Add edges to the Graphviz diagram
                for edge in graph_data["edges"]:
                    edge_from_prefixed = f"N_{edge['from']}"
                    edge_to_prefixed = f"N_{edge['to']}"
                    label_text = edge.get("label", "")
                    
                    # Default edge color
                    edge_color = "#666666" # Gray

                    if label_text.lower() == "yes" or "true" in label_text.lower():
                        edge_color = "#32CD32" # Green for 'Yes' paths
                    elif label_text.lower() == "no" or "false" in label_text.lower():
                        edge_color = "#FF6347" # Red for 'No' paths
                    elif "iteration" in label_text.lower() or "loop" in label_text.lower():
                        edge_color = "#0000FF" # Blue for loop paths
                        
                    dot.edge(
                        edge_from_prefixed,
                        edge_to_prefixed,
                        label=label_text,
                        color=edge_color,
                        penwidth="2.0" # Thicker edges
                    )

                # Center the graph using Streamlit columns
                col1, col2, col3 = st.columns([1, 4, 1])
                with col2:
                    st.graphviz_chart(dot)

                # Add explanation for the flowchart (now for the code itself)
                st.markdown("---")
                st.subheader("Code Explanation")
                st.write(code_explanation) # Display the AI-generated code explanation

                # --- END: Graphviz Generation ---

                # Show raw JSON
                with st.expander("🔍 Raw JSON output"):
                    st.code(json.dumps(graph_data, indent=2))

            except Exception as e:
                st.error(f"❌ An error occurred during diagram generation: {str(e)}")

st.markdown("---")
st.caption("Built with ❤️ using OpenRouter + Graphviz + Streamlit.")
