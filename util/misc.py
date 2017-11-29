
import os

def get_version():

    try:
        import git
        try:
            return git.Repo(search_parent_directories = True).head.object.hexsha
        except git.exc.InvalidGitRepositoryError as e:
            pass
    except ImportError as e:
        pass

    import subprocess
    g = subprocess.Popen(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
    ver = g.stdout.read().strip().decode()

    return ver

