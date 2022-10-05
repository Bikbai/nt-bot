import git
import utility as u

repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha
u.log_info(f"Running version {sha}")
