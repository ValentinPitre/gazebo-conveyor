#!/usr/bin/env python3

import rospy, tf, rospkg, random
from gazebo_msgs.srv import DeleteModel, SpawnModel, GetModelState
from geometry_msgs.msg import Quaternion, Pose, Point


class CubeSpawner():

    def __init__(self) -> None:
        self.rospack = rospkg.RosPack()
        self.path = self.rospack.get_path('demo_world') + "/urdf/"
        self.cubes = []
        self.cubes.append(self.path + "red_cube.urdf")
        self.cubes.append(self.path + "green_cube.urdf")
        self.cubes.append(self.path + "blue_cube.urdf")

        self.spawn_cubes = set()
        self.cube_id = -1

        self.sm = rospy.ServiceProxy("/gazebo/spawn_urdf_model", SpawnModel)
        self.dm = rospy.ServiceProxy("/gazebo/delete_model", DeleteModel)
        self.ms = rospy.ServiceProxy("/gazebo/get_model_state", GetModelState)

    def checkNextModel(self):
        return self.checkModel("cube_" + str(self.cube_id))

    def checkModel(self, name):
        res = self.ms(name, "world")
        return not res.success or res.pose.position.y > 0.07

    def spawnModel(self):
        # print(self.col)
        cube = self.cubes[random.randint(0, len(self.cubes) - 1)]
        with open(cube, "r") as f:
            cube_urdf = f.read()

        quat = tf.transformations.quaternion_from_euler(0, 0, random.uniform(-1.5708, 1.5708))
        orient = Quaternion(quat[0], quat[1], quat[2], quat[3])
        pose = Pose(Point(x=random.uniform(-0.025, 0.025), y=0.05, z=0.1), orient)

        self.cube_id = (self.cube_id + 1) % 10
        cube_name = "cube_" + str(self.cube_id)
        if cube_name in self.spawn_cubes:
            self.deleteModel(cube_name)
        else:
            self.spawn_cubes.add(cube_name)
        self.sm(cube_name, cube_urdf, '', pose, 'world')
        rospy.sleep(0.2)

    def deleteModel(self, cube_name):
        self.dm(cube_name)
        rospy.sleep(0.2)

    def shutdown_hook(self):
        for model in self.spawn_cubes:
            self.deleteModel(model)
        print("Shutting down")


if __name__ == "__main__":
    print("Waiting for gazebo services...")
    rospy.init_node("spawn_cubes")
    rospy.wait_for_service("/gazebo/delete_model")
    rospy.wait_for_service("/gazebo/spawn_urdf_model")
    rospy.wait_for_service("/gazebo/get_model_state")
    #r = rospy.Rate(15)
    cs = CubeSpawner()
    rospy.on_shutdown(cs.shutdown_hook)
    while not rospy.is_shutdown():
        if cs.checkNextModel():
            rospy.sleep(random.uniform(1.0, 5.0))
            cs.spawnModel()
        rospy.sleep(0.1)
