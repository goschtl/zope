class UserFolderAPI:
    """
    User Folder objects are containers for user objects. Programmers can
    work with collections of user objects using the API shared by User
    Folder implementations.
    """

    def getUser(self, name):
        """
        Returns the user object specified by name.  If there is no
        user named 'name' in the user folder, return None.

        Permission -- Manage users

        """

    def getUsers(self):
        """
        Returns a sequence of all user objects which reside in the user
        folder.

        Permission -- Manage users
        
        """

    def getUserNames(self):
        """
        Returns a sequence of names of the users which reside in the user
        folder.

        Permission -- Manage users

        """

    def manage_addUser(self, name, password, roles, domains):
        """
        API method for creating a new user object. Note that not all
        user folder implementations support dynamic creation of user
        objects. Implementations that do not support dynamic creation
        of user objects will raise an error for this method.

        Permission -- Manage users

        """


    def manage_editUser(self, name, password, roles, domains):
        """
        API method for changing user object attributes. Note that not
        all user folder implementations support changing of user object
        attributes. Implementations that do not support changing of user
        object attributes will raise an error for this method.

        Permission -- Manage users

        """


    def manage_delUsers(self, names):
        """
        API method for deleting one or more user objects. Note that not
        all user folder implementations support deletion of user objects.
        Implementations that do not support deletion of user objects
        will raise an error for this method.

        Permission -- Manage users

        """
