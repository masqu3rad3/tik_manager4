Getting Started
===============

Defining Common Folder
-------------
On first launch, user will be asked for to define a **common folder**.

The purpose of this folder is to share the templates and user data between the different users of the application.
Therefore it is important to define a folder that is accessible to all users.

**Common Folder** can changed any time from File Menu -> Settings -> User

Adding Users
------------

Users in Tik Manager4 are the people who will be working on the project. They can be artists, supervisors, producers etc.
There are 4 different levels of permissions for the users.

**Observer (Level 0)**: Can only view the project and contents. Can not create or modify any data.

**Generic (Level 1)**: Can save works, versions and do publishes. Can delete *ONLY* their own data.

**Experienced (Level 2)**: Can do anything Generic can do. Additionally can create or edit sub-projects and tasks.

**Admin (Level 3)**: Can do anything in the project. Can add new users. Can delete *ANY* data including others.


Creating Project
----------------

1. In the Tik Manager4 main UI, go to by File Menu -> Create New Project to create a new Tik Manager4 project.
2. Browse to where you want the Project folder live.
3. Define a Project Name
4. Choose a template to start with. These are just presets for sub-project structures and initial metadata.
5. Define the root properties by enabling available metadatas if needed

.. tip:: 

    The metadatas defined in root will be passed to all sub-projects unless they are overridden. It is a good practice to set the values like fps which will apply to most of the project in the root. 

.. note:: 

    Each project can have their own list of metadatas. Check the **settings** area to learn more about how to define metadatas.


Creating Sub-Projects
---------------------

Sub-Projects are the main building blocks of the Tik Manager4. They can be the containers for tasks and other sub-projects.
Depending on the project requirements, a sub-project can be in **shot**, **asset** or **global** *mode*.

.. note::

    **Mode** is simply another metadata that will be inherited or overridden by the sub-projects.

In order to create a sub-project, simply right click to the project root or any sub-project and select 
**Create Sub-Project**.

.. image:: images/create_sub_project.gif

.. hint:: 

    There is no requirement of creating Asset or Shot sub-projects. It is just a way to organize the tasks and assets.

.. attention:: 

    Creating a new sub-project requires level 2 (Experienced) or above permissions.

Creating Tasks
--------------

Everything the artists will save a load must belong to a task. In other words, tasks are the containers of all work.

Each task can have different categories. For example, a task that belongs to a shot sub-project can have
categories like **animation**, **lighting**, **compositing** etc. Whereas a task that belongs to an asset sub-project
can have categories like **modeling**, **rigging**, **texturing** etc.

A task belongs to a global sub-project can have any available category.

Each project can have their own list of available categories.
The available categories are defined in the settings area and can be changed any time.
Check the **settings** area to learn more about how to define categories.

By default, root project will have a pre-created task called **Main**. 

In order to create a new task right click to the project root or any sub-project and select **New Task** from the
context menu.

From the pop-up window, define the task name and define the available categories for that task.

.. image:: images/create_task.gif

.. attention:: 

    Creating a new sub-project requires level 2 (Experienced) or above permissions.












Getting Started
===============

Defining Common Folder
-----------------------
On first launch, users will be asked to define a **common folder**.

The purpose of this folder is to share templates and user data between different users of the application.
Therefore, it is important to define a folder that is accessible to all users.

**Common Folder** can be changed at any time from `File Menu -> Settings -> User`.

Adding Users
------------
Users in Tik Manager4 are individuals who will be working on the project, such as artists, supervisors, and producers.
There are four different levels of permissions for users:

- **Observer (Level 0)**: Can only view projects and contents but cannot create or modify any data.
- **Generic (Level 1)**: Can save works, versions, and perform publishes. Can delete only their own data.
- **Experienced (Level 2)**: Can do everything Generic can do, plus create or edit sub-projects and tasks.
- **Admin (Level 3)**: Has full control over the project, including adding new users and deleting any data.

Creating Project
----------------
1. In the Tik Manager4 main UI, go to `File Menu -> Create New Project` to start a new Tik Manager4 project.
2. Browse to where you want the Project folder to reside.
3. Define a Project Name.
4. Choose a template to start with. These are just presets for sub-project structures and initial metadata.
5. Define the root properties by enabling available metadata if needed.

.. tip::

    Metadata defined at the root level will be inherited by all sub-projects unless overridden. It's recommended to set values such as FPS at the root, as they will apply to most of the project.

.. note::

    Each project can have its list of metadata. Check the **settings** area to learn more about how to define metadata.

Creating Sub-Projects
---------------------
Sub-Projects are the primary building blocks of Tik Manager4, serving as containers for tasks and other sub-projects.
Depending on project requirements, a sub-project can be in shot, asset, or global mode.

.. note::

    **Mode** is simply another metadata that will be inherited or overridden by the sub-projects.

In order to create a sub-project, simply right-click on the project root or any sub-project and select `Create Sub-Project`.

.. image:: images/create_sub_project.gif

.. hint::

    There is no requirement of creating Asset or Shot sub-projects. It is just a way to organize the tasks and assets.
    For very simple projects, we don't even need to create a sub-project. We can directly create tasks under the root project.

.. attention::

    Creating a new sub-project requires level 2 (Experienced) or above permissions.

Creating Tasks
--------------
Tasks are containers for all work performed by artists.
Each task can have different categories, depending on whether it belongs to a shot, asset, or global sub-project.

In order to create a new task, right-click on the project root or any sub-project and select `New Task` from the context menu.

From the pop-up window, define the task name and define the available categories for that task.

.. image:: images/create_task.gif

.. attention::

    Creating a new task requires level 2 (Experienced) or above permissions.
