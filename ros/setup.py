from setuptools import find_packages, setup


package_name = "ros_nodes"


setup(
    name=package_name,
    version="0.0.1",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/tim_bot.launch.py"]),
    ],
    install_requires=[
        "setuptools",
        "jpl-rosa==1.0.9",
        "langchain==0.3.27",
        "langchain-openai==0.3.35",
        "openai==2.13.0",
        "python-dotenv==1.2.1",
        "pyserial==3.5",
        "PyAudio==0.2.14",
        "piper-tts==1.3.0",
    ],
    zip_safe=True,
    maintainer="bowman",
    maintainer_email="bowman@example.com",
    description="ROS 2 nodes for Tim bot.",
    license="Proprietary",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "brain_node = ros_nodes.brain_node:main",
            "camera_node = ros_nodes.camera_node:main",
            "ear_node = ros_nodes.ear_node:main",
            "motor_node = ros_nodes.motor_node:main",
            "speech_node = ros_nodes.speech_node:main",
        ],
    },
)
