import git
import utility as u


def show_version():
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    u.log_info(f"Running version {sha}")
