import git
import utility as u


def show_version():
    try:
        repo = git.Repo(search_parent_directories=True, path='./nt-bot/')
    except Exception as e:
        return "No git repo found"
    sha = repo.head.object.hexsha
    u.log_info(f"Running version {sha}")
