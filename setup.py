from setuptools import setup, find_packages

setup(
    name="multi-agents",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "anthropic>=0.5.0",
        "boto3>=1.28.0",
        "chromadb>=0.4.0",
        "streamlit>=1.24.0",
        "chainlit>=0.7.0",
        "pyautogen>=0.1.0",
        "langchain>=0.0.267",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
        "pdfplumber>=0.10.0",
        "opencv-python>=4.8.0",
        "pillow>=10.0.0",
    ],
    author="Patrick Rotzetter",
    author_email="your.email@example.com",
    description="Multi-agent AI systems using various frameworks and models",
    keywords="ai, agents, llm, autogen, claude, bedrock",
    python_requires=">=3.8",
)
