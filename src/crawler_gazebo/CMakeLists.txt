cmake_minimum_required(VERSION 2.8.3)

project(crawler_gazebo)

find_package(catkin REQUIRED COMPONENTS
  rospy
  message_generation
  std_msgs
  geometry_msgs
)
catkin_python_setup()


generate_messages(
  DEPENDENCIES
  std_msgs
  geometry_msgs
)
include_directories(
# include
  ${catkin_INCLUDE_DIRS}
)


catkin_package()


install(DIRECTORY
  msg
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

find_package(roslaunch)

foreach(dir config launch meshes urdf src)
	install(DIRECTORY ${dir}/
		DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/${dir})
endforeach(dir)