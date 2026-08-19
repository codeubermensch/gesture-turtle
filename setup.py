from setuptools import find_packages, setup

package_name = 'gesture_turtle'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='maithresh',
    maintainer_email='maithreshgokulkumar@gmail.com',
    description='TODO: Gesture controlled turtlesim using OpenCV',
    license='TODO: Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'turtle_controller = gesture_turtle.turtle_controller:main',
            'gesture_bridge = gesture_turtle.gesture_bridge:main',
        ],
    },
)
