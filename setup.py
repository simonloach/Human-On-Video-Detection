import os
import requests

try:
    os.mkdir("output/")
    print("Created '/output")
        
except:
    print("Could not create '/output'")

try:
    os.mkdir("/input")
    print("Created '/input'")
        
except:
    print("Could not create '/input'")

try:
    os.mkdir("/models")
    print("Created '/models'")
        
except:
    print("Could not create '/models'")


os.chdir(os.getcwd()+'/models')
# if is_downloadable
# r = requests.get('https://pjreddie.com/media/files/yolov3.weights', allow_redirects=True)
# open('yolov3.weights', 'wb').write(r.content)

# setup(
#     name = "an_example_pypi_project",
#     version = "0.0.1",
#     author = "Szymon Piskorz",
#     author_email = "sim.piskorz@gmail.com",
#     description = ("Simple people in the video counter"),
#     license = "BSD",
#     keywords = "example documentation tutorial",
#     url = "http://packages.python.org/an_example_pypi_project",
#     packages=['an_example_pypi_project', 'tests'],
#     long_description=read('README'),
#     classifiers=[
#         "Development Status :: 3 - Alpha",
#         "Topic :: Utilities",
#         "License :: OSI Approved :: BSD License",
#     ],
# )