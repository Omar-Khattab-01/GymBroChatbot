
#import gradio as gr
import os
##from groq import Groq

# Automatically install missing dependencies
try:
    from groq import Groq
except ModuleNotFoundError:
    os.system("pip install groq")
    from groq import Groq

try:
    import gradio as gr
except ModuleNotFoundError:
    os.system("pip install gradio")
    import gradio as gr

# Initialize Groq client
api_key = "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"
client = Groq(api_key=api_key)

# Initialize conversation history
conversation_history = []

def chat_with_bot_stream(user_input, temperature=0.7):
    global conversation_history
    if user_input.strip() == "":
        return []  # Avoid processing empty input

    conversation_history.append({"role": "user", "content": user_input})
    
    if len(conversation_history) == 1:
        conversation_history.insert(0, {
            "role": "system",
            "content": "You are an expert in fitness and nutrition. Provide structured and insightful responses to queries about exercise routines, diet plans, health tips, and overall wellness. Your responses should be informative, encouraging, and tailored to the user's specific fitness goals and dietary needs."
        })
    
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=conversation_history,
        temperature=temperature,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
    
    response_content = ""
    for chunk in completion:
        response_content += chunk.choices[0].delta.content or ""
    
    conversation_history.append({"role": "assistant", "content": response_content})

    ##return gr.update(value=conversation_history, visible=True)

    # Step 1: Return partial update to avoid auto-scrolling
    #yield gr.update(value=conversation_history, visible=True)

    # Step 2: Wait before updating fully
    #time.sleep(0.5)  # Small delay to prevent auto-scroll
    #yield gr.update(value=conversation_history, visible=True)  # Final update
    
    return [{"role": msg["role"], "content": msg["content"]} for msg in conversation_history]

css = """
/* Futuristic Theme */
:root {
    --primary-color: #00ff99;
    --secondary-color: #0066ff;
    --background-dark: #1a1a2e;
    --text-light: #ffffff;
    --neon-glow: 0 0 10px var(--primary-color);
}

body { 
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%);
    color: var(--text-light);
}

.gradio-container {
    background: rgba(26, 26, 46, 0.95);
    border-radius: 15px;
    box-shadow: 0 0 30px rgba(0, 255, 153, 0.2);
    backdrop-filter: blur(10px);
}

h1 { 
    color: var(--text-light);
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 2px;
    text-shadow: 0 0 10px var(--primary-color);
    animation: glow 2s ease-in-out infinite alternate;
}

button, .button, input[type="submit"] { 
    background: linear-gradient(45deg, var(--primary-color), var(--secondary-color)) !important;
    color: var(--text-light) !important;
    border: none !important;
    border-radius: 25px !important;
    padding: 12px 24px !important;
    font-weight: bold !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 15px rgba(0, 255, 153, 0.3) !important;
}

button:hover, .button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 0 20px var(--primary-color) !important;
}

.send_button {
    height: 45px !important;
    width: 120px !important;
    font-size: 14px !important;
}

.button:hover, input[type="submit"]:hover { background-color: #45a049; }
.text_input, textarea { 
    border-radius: 5px; border: 2px solid #ccc; padding: 10px; 
    width: 100%; box-sizing: border-box; margin-bottom: 10px; 
    transition: border-color 0.3s;
}
.text_input:focus, textarea:focus { border-color: #4CAF50; }
"""

# JavaScript to disable chat auto-scroll
js_script = """
<script>
document.addEventListener("DOMContentLoaded", function () {
    var observer = new MutationObserver(function (mutations) {
        var chatContainer = document.querySelector('.wrap-chatbot');
        if (chatContainer) {
            chatContainer.scrollTop = 0;  // Force the scroll to stay at the top
        }
    });

    var chatElement = document.querySelector('.wrap-chatbot');
    if (chatElement) {
        observer.observe(chatElement, { childList: true, subtree: true });
    }
});
</script>
"""


with gr.Blocks(css=css) as demo:
    with gr.Tabs():
        with gr.TabItem("Chat"):
            gr.Markdown(js_script)  # Injecting JavaScript to disable auto-scroll
            gr.Markdown("<h1 style='text-align: center;'>GymBro Fitness Chat</h1>")
            temperature_slider = gr.Slider(minimum=0.5, maximum=1.0, step=0.05, value=0.7, label="Chat Temperature")
            chatbot = gr.Chatbot(label="Talk to GymBro", type='messages')  # Auto-scroll disabled by JS
            
            example_questions = gr.Radio(
            choices=[
                "Can you create a workout plan for me?",
                "What are the best high-protein foods?",
                "How many calories do I need per day?",
                "What’s the best way to lose fat without losing muscle?",
                "What’s the best way to lose fat without losing muscle?",
                "Can you suggest a meal plan based on my dietary restrictions?"
            ],
            label="Not sure where to start? 🤔 Explore GymBro’s powerful features with these questions:"
            )
            example_questions.change(
            fn=lambda x: chat_with_bot_stream(x, temperature_slider.value),
            inputs=example_questions,
            outputs=chatbot
            )
        
            with gr.Row(elem_id="input-container", equal_height=True):
                user_input = gr.Textbox(
                        label="Type your question here",
                        placeholder="Ask about meal or workout plans...",
                        lines=1,
                        scale = 5
                    )
                
                send_button = gr.Button("Send" ,  elem_id="send_button", scale = 1)
        
                send_button.click(
                    fn=chat_with_bot_stream,
                    inputs=[user_input, temperature_slider],
                    outputs=chatbot
                ).then(
                    fn=lambda _: "",  # Clear the input text field by resetting its state
                    inputs=None,
                    outputs=user_input
                   
                )

        

demo.launch()