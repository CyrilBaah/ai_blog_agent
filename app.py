import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
load_dotenv()

# Environment variables
CLARIFAI_PAT = os.getenv("CLARIFAI_PAT")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not CLARIFAI_PAT:
    st.error("Please set CLARIFAI_PAT environment variable")
    st.stop()

if not SERPER_API_KEY:
    st.error("Please set SERPER_API_KEY environment variable")
    st.stop()

# Configure Clarifai LLM
clarifai_llm = LLM(
    model="openai/gcp/generate/models/gemini-2_5-pro",
    api_key=CLARIFAI_PAT,
    base_url="https://api.clarifai.com/v2/ext/openai/v1"
)

# Initialize tools
search_tool = SerperDevTool()

# Define Agents
researcher = Agent(
    role="Senior Research Analyst",
    goal="Uncover cutting-edge developments and facts on a given topic",
    backstory="""You are a meticulous and insightful research analyst working at a leading tech think tank.
    Your expertise lies in identifying emerging trends, gathering verified information,
    and presenting actionable insights clearly and concisely.""",
    tools=[search_tool],
    verbose=True,
    allow_delegation=False,
    llm=clarifai_llm
)

writer = Agent(
    role="Tech Content Strategist",
    goal="Craft compelling and engaging blog posts on technical topics",
    backstory="""You are a renowned Content Strategist, known for your insightful and engaging articles.
    You transform complex concepts and research findings into compelling narratives
    that are accessible to a tech-savvy audience.""",
    verbose=True,
    allow_delegation=True,
    llm=clarifai_llm
)


def create_tasks(topic):
    """Create research and writing tasks for the given topic"""
    research_task = Task(
        description=f"""Conduct a comprehensive analysis of '{topic}'.
        Identify key trends, breakthrough technologies, important figures, and potential industry impacts.
        Focus on factual and verifiable information.""",
        expected_output="A detailed analysis report in bullet points, including sources if possible.",
        agent=researcher
    )

    writing_task = Task(
        description=f"""Using the insights and research provided on '{topic}', develop an engaging blog post.
        The post should be at least 4-5 paragraphs long, informative yet accessible, catering to a tech-savvy audience.
        Make it sound human, avoid overly complex jargon unless explained, and ensure a logical flow.
        The blog post should have a clear introduction, body, and conclusion.

        IMPORTANT: Format the output as proper markdown with:
        - A compelling title using # 
        - Section headers using ##
        - Proper paragraph breaks
        - Bullet points where appropriate
        - Bold text for emphasis using **text**
        - No code blocks or triple backticks in the output""",
        expected_output="A well-written blog post of at least 4 paragraphs, formatted in clean markdown.",
        agent=writer,
        context=[research_task]
    )

    return research_task, writing_task


def run_blog_generation(topic):
    """Run the blog generation crew for the given topic"""
    research_task, writing_task = create_tasks(topic)

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=1
    )
    result = crew.kickoff()

    return result


# Streamlit App
def main():
    st.title("📝 AI Blog Writing Agent")
    st.markdown("*Powered by Clarifai & CrewAI*")

    st.markdown("""
    This application uses Clarifai and CrewAI to generate high-quality blog posts on topics you provide.

    **How it works:**
    - 🔍 **Researcher Agent** gathers comprehensive information on your topic
    - ✍️ **Writer Agent** crafts an engaging, well-structured blog post
    - 🧠 **Powered by** Clarifai's Gemini 2.5 Pro model via OpenAI-compatible API
    """)

    # Input section
    with st.container():
        topic = st.text_input(
            "Enter your blog topic:",
            placeholder="e.g., The Future of Quantum Computing",
            help="Be specific for better results"
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            generate_button = st.button("🚀 Generate Blog", type="primary")

    # Generation section
    if generate_button:
        if not topic.strip():
            st.error("Please enter a topic for the blog post.")
        else:
            with st.spinner(f"🧠 AI agents are working on: '{topic}'..."):
                try:
                    result = run_blog_generation(topic)

                    st.success("✅ Blog post generated successfully!")
                    st.markdown("---")

                    # Display the result as markdown
                    st.markdown(result)

                    # Download option
                    st.download_button(
                        label="📥 Download as Markdown",
                        data=result,
                        file_name=f"{topic.replace(' ', '_').lower()}_blog.md",
                        mime="text/markdown"
                    )

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    # Sidebar
    with st.sidebar:
        st.header("ℹ️ Information")

        st.markdown("**Environment Variables Required:**")
        st.code("CLARIFAI_PAT=your_clarifai_personal_access_token")
        st.code("SERPER_API_KEY=your_serper_dev_api_key")

        st.markdown("**Current Configuration:**")
        st.markdown(f"- **Model:** `gcp/generate/models/gemini-2_5-pro`")
        st.markdown(f"- **API Base:** `api.clarifai.com`")

        st.markdown("**Features:**")
        st.markdown("- Real-time web research")
        st.markdown("- AI-powered content writing")
        st.markdown("- Markdown formatted output")
        st.markdown("- Download capability")

        st.warning("⚠️ Keep your API keys secure and never commit them to version control.")


if __name__ == "__main__":
    main()