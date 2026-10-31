from setuptools import setup, find_packages

setup(
    name="complyai",
    version="1.0.0",
    description="Autonomous Legal & Regulatory Compliance Auditor AI/RAG Engine",
    author="ComplyAI Engineering Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.0.0",
    ],
)

