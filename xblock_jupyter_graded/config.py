"""Application config"""
import os

# Root directory where nbgrader data will be stored in EdX
EDX_ROOT = "/var/www/nbgrader/courses/"

# Root directory where nbgrader data will be stored in Container
CONT_ROOT = "/home/nbgrader/course/"

# Root directory where nbgrader data will be stored in Host
HOST_ROOT = os.getenv("JUPYTER_GRADER_HOST_ROOT", '/var/www/nbgrader/courses')

# nbgrader directory names - these are the default names nbgrader expects
# but could be mofied in nbgrader config and those reflected here if so desired
RELEASE = "release"
SOURCE = "source"
SUBMITTED = "submitted"
AUTOGRADED = "autograded"
FEEDBACK = "feedback"
