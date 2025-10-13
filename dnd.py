"""
Multi-Agent D&D Game - Streamlit Web Application
=================================================
A beautiful, interactive web interface for the multi-agent D&D game.

Installation:
    pip install streamlit langchain openai python-dotenv

Setup (Streamlit Secrets - Recommended):
    Create .streamlit/secrets.toml in your project directory:
    
    OPENAI_API_KEY = "sk-your-api-key-here"

Run:
    streamlit run dnd_streamlit_app.py
"""

import streamlit as st
import os
from typing import List, Callable
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import time

# ===== PAGE CONFIGURATION =====
st.set_page_config(
    page_title="AI D&D Adventure",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM CSS FOR PASTEL AESTHETIC =====
st.markdown("""
<style>
    /* Main color palette - Soft Pastels */
    :root {
        --pastel-pink: #FFD6E8;
        --pastel-blue: #C1E7FF;
        --pastel-purple: #E0BBE4;
        --pastel-mint: #D4F1E8;
        --pastel-peach: #FFE5CC;
        --pastel-lavender: #E6E6FA;
        --pastel-yellow: #FFF9C4;
        --dark-text: #4A4A4A;
        --light-bg: #FEFEFE;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #FFE5F1 0%, #E6F3FF 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E0BBE4 0%, #FFD6E8 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--dark-text);
    }
    
    /* Headers */
    h1 {
        color: #8B5FBF;
        font-family: 'Georgia', serif;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #FFD6E8, #E0BBE4, #C1E7FF);
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    
    h2 {
        color: #6B8FB5;
        font-family: 'Georgia', serif;
        border-bottom: 2px solid #C1E7FF;
        padding-bottom: 10px;
    }
    
    h3 {
        color: #9D7BA5;
        font-family: 'Georgia', serif;
    }
    
    /* Message containers */
    .character-message {
        background: linear-gradient(135deg, #FFD6E8 0%, #FFF0F5 100%);
        border-left: 5px solid #FF9FC7;
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
        transition: transform 0.2s;
    }
    
    .character-message:hover {
        transform: translateX(5px);
    }
    
    .storyteller-message {
        background: linear-gradient(135deg, #E0BBE4 0%, #F5F0FF 100%);
        border-left: 5px solid #9D7BA5;
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
    }
    
    .quest-box {
        background: linear-gradient(135deg, #FFF9C4 0%, #FFFEF0 100%);
        border: 3px solid #F0E68C;
        padding: 25px;
        border-radius: 20px;
        margin: 20px 0;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .character-profile {
        background: linear-gradient(135deg, #D4F1E8 0%, #F0FFFA 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border: 2px solid #9FD8CB;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #E0BBE4, #FFD6E8);
        color: var(--dark-text);
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        background: linear-gradient(135deg, #FFD6E8, #E0BBE4);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 15px;
        border: 2px solid #E0BBE4;
        padding: 12px;
        background: var(--light-bg);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 15px;
        border: 2px solid #E0BBE4;
        background: var(--light-bg);
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        border-radius: 15px;
        border: 2px solid #C1E7FF;
        background: var(--light-bg);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #FFD6E8, #E0BBE4, #C1E7FF);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #8B5FBF;
        font-size: 28px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #FFE5CC 0%, #FFF5E6 100%);
        border-radius: 15px;
        border: 2px solid #FFDAB9;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 15px;
        border-left: 5px solid #C1E7FF;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #E0BBE4 !important;
    }
    
    /* Character badges */
    .character-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 5px;
        font-weight: 600;
        font-size: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .badge-harry {
        background: linear-gradient(135deg, #FFE5CC, #FFF0DB);
        border: 2px solid #FFD700;
    }
    
    .badge-ron {
        background: linear-gradient(135deg, #FFD6E8, #FFE8F0);
        border: 2px solid #FF69B4;
    }
    
    .badge-hermione {
        background: linear-gradient(135deg, #C1E7FF, #E0F3FF);
        border: 2px solid #87CEEB;
    }
    
    .badge-filch {
        background: linear-gradient(135deg, #D4F1E8, #E8FAF5);
        border: 2px solid #66CDAA;
    }
    
    /* Animation for new messages */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .new-message {
        animation: slideIn 0.5s ease-out;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #8B5FBF;
        font-style: italic;
        margin-top: 40px;
    }
</style>
""", unsafe_allow_html=True)


# ===== AGENT CLASSES =====
class DialogueAgent:
    """Agent that can participate in conversations."""
    
    def __init__(self, name: str, system_message: SystemMessage, model: ChatOpenAI) -> None:
        self.name = name
        self.system_message = system_message
        self.model = model
        self.prefix = f"{self.name}: "
        self.reset()

    def reset(self):
        self.message_history = ["Here is the conversation so far."]

    def send(self) -> str:
        message = self.model(
            [
                self.system_message,
                HumanMessage(content="\n".join(self.message_history + [self.prefix])),
            ]
        )
        return message.content

    def receive(self, name: str, message: str) -> None:
        self.message_history.append(f"{name}: {message}")


class DialogueSimulator:
    """Manages the conversation flow between agents."""
    
    def __init__(
        self,
        agents: List[DialogueAgent],
        selection_function: Callable[[int, List[DialogueAgent]], int],
    ) -> None:
        self.agents = agents
        self._step = 0
        self.select_next_speaker = selection_function

    def reset(self):
        for agent in self.agents:
            agent.reset()

    def inject(self, name: str, message: str):
        for agent in self.agents:
            agent.receive(name, message)
        self._step += 1

    def step(self) -> tuple:
        speaker_idx = self.select_next_speaker(self._step, self.agents)
        speaker = self.agents[speaker_idx]
        message = speaker.send()
        
        for receiver in self.agents:
            receiver.receive(speaker.name, message)
        
        self._step += 1
        return speaker.name, message


def select_next_speaker(step: int, agents: List[DialogueAgent]) -> int:
    """Round-robin with storyteller interleaving."""
    if step % 2 == 0:
        return 0
    else:
        return (step // 2) % (len(agents) - 1) + 1


# ===== HELPER FUNCTIONS =====
def get_character_emoji(name: str) -> str:
    """Return emoji for character."""
    emoji_map = {
        "Harry Potter": "⚡",
        "Ron Weasley": "🦁",
        "Hermione Granger": "📚",
        "Argus Filch": "🐱",
        "Draco Malfoy": "🐍",
        "Luna Lovegood": "🌙",
        "Neville Longbottom": "🌿",
        "Dungeon Master": "🎭"
    }
    return emoji_map.get(name, "🎲")


def get_character_color(name: str) -> str:
    """Return color class for character."""
    color_map = {
        "Harry Potter": "badge-harry",
        "Ron Weasley": "badge-ron",
        "Hermione Granger": "badge-hermione",
        "Argus Filch": "badge-filch"
    }
    return color_map.get(name, "")


def initialize_session_state():
    """Initialize all session state variables."""
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'simulator' not in st.session_state:
        st.session_state.simulator = None
    if 'character_descriptions' not in st.session_state:
        st.session_state.character_descriptions = {}
    if 'quest_details' not in st.session_state:
        st.session_state.quest_details = ""
    if 'game_step' not in st.session_state:
        st.session_state.game_step = 0
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""


def generate_character_description(character_name: str, game_description: str, word_limit: int, api_key: str) -> str:
    """Generate character description using LLM."""
    os.environ["OPENAI_API_KEY"] = api_key
    
    player_descriptor_system_message = SystemMessage(
        content="You can add detail to the description of a Dungeons & Dragons player."
    )
    
    character_specifier_prompt = [
        player_descriptor_system_message,
        HumanMessage(
            content=f"""{game_description}
            Please reply with a creative description of the character, {character_name}, in {word_limit} words or less. 
            Speak directly to {character_name}.
            Do not add anything else."""
        ),
    ]
    
    character_description = ChatOpenAI(temperature=1.0)(character_specifier_prompt).content
    return character_description


def generate_character_system_message(
    character_name: str,
    character_description: str,
    game_description: str,
    storyteller_name: str,
    word_limit: int
) -> SystemMessage:
    """Create system message for character."""
    return SystemMessage(
        content=(
            f"""{game_description}
    Your name is {character_name}. 
    Your character description is as follows: {character_description}.
    You will propose actions you plan to take and {storyteller_name} will explain what happens when you take those actions.
    Speak in the first person from the perspective of {character_name}.
    For describing your own body movements, wrap your description in '*'.
    Do not change roles!
    Do not speak from the perspective of anyone else.
    Remember you are {character_name}.
    Stop speaking the moment you finish speaking from your perspective.
    Never forget to keep your response to {word_limit} words!
    Do not add anything else.
    """
        )
    )


# ===== MAIN APP =====
def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
        <h1>🎲 Multi-Agent D&D Adventure 🎲</h1>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Game Configuration")
        st.markdown("---")
        
        # Try to get API key from secrets, fallback to input
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
            st.session_state.api_key = api_key
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("✅ API Key loaded from secrets")
        except:
            # API Key input if not in secrets
            api_key = st.text_input(
                "🔑 OpenAI API Key",
                type="password",
                value=st.session_state.api_key,
                help="Enter your OpenAI API key to start the adventure"
            )
            
            if api_key:
                st.session_state.api_key = api_key
                os.environ["OPENAI_API_KEY"] = api_key
        
        st.markdown("---")
        
        # Character selection
        st.markdown("### 🎭 Choose Your Heroes")
        default_characters = ["Harry Potter", "Ron Weasley", "Hermione Granger", "Argus Filch"]
        
        character_names = st.multiselect(
            "Select Characters",
            options=["Harry Potter", "Ron Weasley", "Hermione Granger", "Argus Filch", 
                     "Draco Malfoy", "Luna Lovegood", "Neville Longbottom"],
            default=default_characters,
            help="Choose 2-5 characters for your adventure"
        )
        
        st.markdown("---")
        
        # Quest configuration
        st.markdown("### 🗺️ Quest Setup")
        quest = st.text_area(
            "Quest Objective",
            value="Find all of Lord Voldemort's seven horcruxes.",
            help="Describe the main quest objective"
        )
        
        storyteller_name = st.text_input(
            "Storyteller Name",
            value="Dungeon Master",
            help="Name of the game narrator"
        )
        
        word_limit = st.slider(
            "Response Word Limit",
            min_value=30,
            max_value=100,
            value=50,
            help="Maximum words per character response"
        )
        
        max_iterations = st.slider(
            "Adventure Length",
            min_value=5,
            max_value=50,
            value=20,
            help="Number of conversation turns"
        )
        
        st.markdown("---")
        
        # Control buttons
        col1, col2 = st.columns(2)
        
        with col1:
            start_button = st.button("🎮 Start Adventure", use_container_width=True)
        
        with col2:
            reset_button = st.button("🔄 Reset Game", use_container_width=True)
        
        if reset_button:
            st.session_state.game_started = False
            st.session_state.messages = []
            st.session_state.simulator = None
            st.session_state.character_descriptions = {}
            st.session_state.quest_details = ""
            st.session_state.game_step = 0
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; color: #8B5FBF; font-size: 12px; padding: 20px;'>
                <p>✨ Powered by LangChain & OpenAI</p>
                <p>🎨 Beautiful Pastel Design</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    if not st.session_state.api_key:
        st.info("👈 Please enter your OpenAI API key in the sidebar or set up Streamlit secrets to begin your adventure!")
        
        st.markdown("""
        <div class='quest-box'>
            <h2>🌟 Welcome to the Multi-Agent D&D Adventure! 🌟</h2>
            <p style='font-size: 18px; color: #4A4A4A;'>
                Watch as AI characters come to life and embark on epic quests together!
            </p>
            <br>
            <p style='font-size: 14px; color: #6B6B6B;'>
                This application uses advanced AI agents that collaborate autonomously to create 
                dynamic storytelling experiences. Each character has unique personality traits 
                and will interact naturally with others to complete the quest.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature showcase
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class='character-profile'>
                <h3 style='text-align: center;'>🎭 Dynamic Characters</h3>
                <p style='text-align: center;'>AI agents with unique personalities and goals</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='character-profile'>
                <h3 style='text-align: center;'>📖 Emergent Storytelling</h3>
                <p style='text-align: center;'>Unpredictable narratives that evolve naturally</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class='character-profile'>
                <h3 style='text-align: center;'>🤝 Collaborative AI</h3>
                <p style='text-align: center;'>Watch agents work together to solve challenges</p>
            </div>
            """, unsafe_allow_html=True)
        
        return
    
    if len(character_names) < 2:
        st.warning("⚠️ Please select at least 2 characters to start the adventure!")
        return
    
    # Start game logic
    if start_button and not st.session_state.game_started:
        with st.spinner("🎨 Generating character descriptions..."):
            game_description = f"""Here is the topic for a Dungeons & Dragons game: {quest}.
                The characters are: {', '.join(character_names)}.
                The story is narrated by the storyteller, {storyteller_name}."""
            
            # Generate descriptions
            character_descriptions = {}
            progress_bar = st.progress(0)
            
            for idx, character_name in enumerate(character_names):
                character_descriptions[character_name] = generate_character_description(
                    character_name, game_description, word_limit, st.session_state.api_key
                )
                progress_bar.progress((idx + 1) / (len(character_names) + 2))
                time.sleep(0.1)
            
            storyteller_description = generate_character_description(
                storyteller_name, game_description, word_limit, st.session_state.api_key
            )
            progress_bar.progress((len(character_names) + 1) / (len(character_names) + 2))
            
            # Generate detailed quest
            quest_specifier_prompt = [
                SystemMessage(content="You can make a task more specific."),
                HumanMessage(
                    content=f"""{game_description}
                    
                    You are the storyteller, {storyteller_name}.
                    Please make the quest more specific. Be creative and imaginative.
                    Please reply with the specified quest in {word_limit} words or less. 
                    Speak directly to the characters: {', '.join(character_names)}.
                    Do not add anything else."""
                ),
            ]
            
            specified_quest = ChatOpenAI(temperature=1.0)(quest_specifier_prompt).content
            progress_bar.progress(1.0)
            time.sleep(0.5)
            
            # Create system messages
            character_system_messages = [
                generate_character_system_message(
                    character_name,
                    character_descriptions[character_name],
                    game_description,
                    storyteller_name,
                    word_limit
                )
                for character_name in character_names
            ]
            
            storyteller_system_message = SystemMessage(
                content=(
                    f"""{game_description}
            You are the storyteller, {storyteller_name}. 
            Your description is as follows: {storyteller_description}.
            The other players will propose actions to take and you will explain what happens when they take those actions.
            Speak in the first person from the perspective of {storyteller_name}.
            Do not change roles!
            Do not speak from the perspective of anyone else.
            Remember you are the storyteller, {storyteller_name}.
            Stop speaking the moment you finish speaking from your perspective.
            Never forget to keep your response to {word_limit} words!
            Do not add anything else.
            """
                )
            )
            
            # Create agents
            characters = []
            for character_name, character_system_message in zip(character_names, character_system_messages):
                characters.append(
                    DialogueAgent(
                        name=character_name,
                        system_message=character_system_message,
                        model=ChatOpenAI(temperature=0.2),
                    )
                )
            
            storyteller = DialogueAgent(
                name=storyteller_name,
                system_message=storyteller_system_message,
                model=ChatOpenAI(temperature=0.2),
            )
            
            # Create simulator
            simulator = DialogueSimulator(
                agents=[storyteller] + characters,
                selection_function=select_next_speaker
            )
            
            simulator.reset()
            simulator.inject(storyteller_name, specified_quest)
            
            # Save to session state
            st.session_state.simulator = simulator
            st.session_state.character_descriptions = character_descriptions
            st.session_state.character_descriptions[storyteller_name] = storyteller_description
            st.session_state.quest_details = specified_quest
            st.session_state.game_started = True
            st.session_state.messages = [(storyteller_name, specified_quest)]
            st.session_state.game_step = 0
            st.session_state.character_names = character_names
            st.session_state.storyteller_name = storyteller_name
            st.session_state.max_iterations = max_iterations
            
            st.success("✨ Characters generated! The adventure begins...")
            st.rerun()
    
    # Display game if started
    if st.session_state.game_started:
        # Display quest
        st.markdown(f"""
        <div class='quest-box'>
            <h2>🎯 The Quest</h2>
            <p style='font-size: 18px; font-weight: 600; color: #4A4A4A;'>
                {st.session_state.quest_details}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Character profiles in expander
        with st.expander("📋 View Character Profiles", expanded=False):
            cols = st.columns(len(st.session_state.character_names) + 1)
            
            for idx, (name, description) in enumerate(st.session_state.character_descriptions.items()):
                with cols[idx % len(cols)]:
                    emoji = get_character_emoji(name)
                    badge_class = get_character_color(name)
                    st.markdown(f"""
                    <div class='character-profile'>
                        <h4 style='text-align: center;'>{emoji} {name}</h4>
                        <p style='font-size: 13px; color: #6B6B6B;'>{description}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Game metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎮 Turn", st.session_state.game_step)
        with col2:
            st.metric("🎭 Characters", len(st.session_state.character_names))
        with col3:
            progress = min(100, int((st.session_state.game_step / st.session_state.max_iterations) * 100))
            st.metric("📊 Progress", f"{progress}%")
        
        st.markdown("---")
        
        # Display messages
        st.markdown("### 📜 Adventure Log")
        
        message_container = st.container()
        with message_container:
            for speaker, message in st.session_state.messages:
                emoji = get_character_emoji(speaker)
                
                if speaker == st.session_state.storyteller_name:
                    st.markdown(f"""
                    <div class='storyteller-message new-message'>
                        <h4>{emoji} {speaker}</h4>
                        <p style='font-size: 16px; color: #4A4A4A; line-height: 1.6;'>{message}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    badge_class = get_character_color(speaker)
                    st.markdown(f"""
                    <div class='character-message new-message'>
                        <span class='character-badge {badge_class}'>{emoji} {speaker}</span>
                        <p style='font-size: 16px; color: #4A4A4A; margin-top: 10px; line-height: 1.6;'>{message}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Next turn button
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.session_state.game_step < st.session_state.max_iterations:
                if st.button("⏭️ Next Turn", use_container_width=True, type="primary"):
                    with st.spinner("🎲 Rolling dice..."):
                        speaker, message = st.session_state.simulator.step()
                        st.session_state.messages.append((speaker, message))
                        st.session_state.game_step += 1
                        time.sleep(0.5)
                        st.rerun()
            else:
                st.markdown("""
                <div class='quest-box'>
                    <h3>🏆 Adventure Complete!</h3>
                    <p>The quest has concluded. Reset the game to start a new adventure!</p>
                </div>
                """, unsafe_allow_html=True)
    


if __name__ == "__main__":
    main()