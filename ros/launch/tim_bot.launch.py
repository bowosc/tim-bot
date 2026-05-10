from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    start_ear = LaunchConfiguration("start_ear")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "start_ear",
                default_value="false",
                description="Start the interactive ear node. Keep false unless launching from an interactive terminal.",
            ),
            Node(
                package="ros_nodes",
                executable="camera_node",
                name="camera_node",
                output="screen",
            ),
            Node(
                package="ros_nodes",
                executable="brain_node",
                name="brain_node",
                output="screen",
            ),
            Node(
                package="ros_nodes",
                executable="motor_node",
                name="motor_node",
                output="screen",
            ),
            Node(
                package="ros_nodes",
                executable="speech_node",
                name="speech_node",
                output="screen",
            ),
            Node(
                package="ros_nodes",
                executable="ear_node",
                name="ear_node",
                output="screen",
                emulate_tty=True,
                condition=IfCondition(start_ear),
            ),
        ]
    )
