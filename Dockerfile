FROM osrf/ros:humble-desktop

SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-rclpy \
    ros-humble-std-msgs \
    python3-colcon-common-extensions \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Open an interactive shell in /work with ROS already sourced.
RUN echo "source /opt/ros/humble/setup.bash" >> /etc/bash.bashrc
WORKDIR /work

CMD ["bash"]
